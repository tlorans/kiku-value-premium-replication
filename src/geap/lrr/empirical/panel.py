from __future__ import annotations

import io
import urllib.request
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

from .construction import book_equity_frame, form_bm_quintiles, value_weight_monthly
from .consumption import load_consumption, load_deflator
from .dividends import campbell_shiller_annual
from .rates import real_rf_from_monthly
from .wrds import (
    EmpiricalDataError,
    _download_ccm_links,
    _download_compustat_annual,
    _download_crsp_mcti,
    _download_crsp_monthly,
    _download_crsp_msi,
    _is_credentials_failure,
)

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data" / "raw"
PANEL_CSV = ROOT / "data" / "annual_panel.csv"
DC_CSV = ROOT / "data" / "consumption_annual.csv"
RF_CSV = ROOT / "data" / "rf_annual.csv"

WRDS_CACHE = ("msf", "funda", "names", "link", "mcti")

_HIST_BE_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Historical_BE_Data.zip"
)
_CLAIMS = {1: "Growth", 5: "Value"}


def _parquet_path(name: str) -> Path:
    return RAW / f"{name}.parquet"


def _cache_ready() -> bool:
    return all(_parquet_path(name).exists() for name in WRDS_CACHE)


def _to_parquet(df: pd.DataFrame, name: str) -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    try:
        df.to_parquet(_parquet_path(name), index=False)
    except ImportError as exc:
        raise EmpiricalDataError(
            "Install the data extra: uv pip install -e '.[data]'"
        ) from exc


def _read_parquet(name: str) -> pd.DataFrame:
    path = _parquet_path(name)
    if not path.exists():
        raise EmpiricalDataError(f"Missing cache {path}; rerun with refresh=True")
    return pd.read_parquet(path)


def _pull_wrds() -> dict[str, pd.DataFrame]:
    try:
        msf = _download_crsp_monthly()
        funda = _download_compustat_annual()
        link = _download_ccm_links()
        msi = _download_crsp_msi()
        mcti = _download_crsp_mcti()
    except EmpiricalDataError:
        raise
    except Exception as exc:
        if _is_credentials_failure(exc):
            raise EmpiricalDataError(
                "WRDS credentials missing or rejected. "
                "Call tidyfinance.set_wrds_credentials()."
            ) from exc
        raise EmpiricalDataError("WRDS download failed") from exc
    # Derived names for the parquet cache. Monthly exchcd on msf is the
    # universe key; do not freeze the first exchcd per permno.
    names = (
        msf.groupby(["permno", "exchcd"], as_index=False)
        .agg(namedt=("date", "min"), nameendt=("date", "max"))
        .assign(shrcd=11)
    )
    return {
        "msf": msf,
        "names": names,
        "link": link,
        "funda": funda,
        "mcti": mcti,
        "msi": msi,
    }


def _parse_hist_be(text: str) -> pd.DataFrame:
    rows: list[tuple[int, int, float]] = []
    for line in text.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        try:
            permno = int(float(parts[0]))
            vals = [float(x) for x in parts[3:]]
        except ValueError:
            continue
        for i, be in enumerate(vals):
            if not np.isfinite(be) or be <= -99.0:
                continue
            moody_year = 1926 + i
            rows.append((permno, moody_year - 1, be))
    if not rows:
        raise EmpiricalDataError("Ken French historical book equity parsed empty")
    return pd.DataFrame(rows, columns=["permno", "year", "be"])


def _download_hist_be() -> pd.DataFrame:
    req = urllib.request.Request(_HIST_BE_URL, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            blob = resp.read()
    except Exception as exc:
        raise EmpiricalDataError(
            "Failed to download Ken French historical book equity"
        ) from exc
    with zipfile.ZipFile(io.BytesIO(blob)) as zf:
        name = zf.namelist()[0]
        text = zf.read(name).decode("latin-1")
    return _parse_hist_be(text)


def _load_raw(refresh: bool) -> dict[str, pd.DataFrame]:
    if refresh or not _cache_ready():
        tables = _pull_wrds()
        for name, df in tables.items():
            _to_parquet(df, name)
    else:
        tables = {name: _read_parquet(name) for name in WRDS_CACHE}
        tables["msi"] = _read_parquet("msi")
    hist_path = _parquet_path("hist_be")
    if refresh or not hist_path.exists():
        hist = _download_hist_be()
        _to_parquet(hist, "hist_be")
        tables["hist_be"] = hist
    else:
        tables["hist_be"] = _read_parquet("hist_be")
    return tables


def _filter_universe(msf: pd.DataFrame, names: pd.DataFrame) -> pd.DataFrame:
    # tidyfinance v1 already restricted ordinary shares. Monthly exchcd
    # (after 31/32/33 → 1/2/3) is the NYSE/AMEX/NASDAQ cut.
    out = msf.copy()
    out["permno"] = pd.to_numeric(out["permno"], errors="coerce")
    out["date"] = pd.to_datetime(out["date"])
    if "exchcd" not in out.columns:
        nm = names.copy()
        nm["permno"] = pd.to_numeric(nm["permno"], errors="coerce")
        nm["namedt"] = pd.to_datetime(nm["namedt"])
        nm["nameendt"] = pd.to_datetime(nm["nameendt"]).fillna(
            pd.Timestamp("2099-12-31")
        )
        nm["exchcd"] = pd.to_numeric(nm["exchcd"], errors="coerce")
        out = out.merge(
            nm[["permno", "namedt", "nameendt", "exchcd"]],
            on="permno",
            how="inner",
        )
        out = out[(out["date"] >= out["namedt"]) & (out["date"] <= out["nameendt"])]
        out = out.drop(columns=["namedt", "nameendt"])
    out["exchcd"] = pd.to_numeric(out["exchcd"], errors="coerce")
    out = out[out["exchcd"].isin((1, 2, 3))]
    out = out.drop_duplicates(["permno", "date"])
    for col in ("ret", "retx", "prc", "shrout"):
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["permno"] = out["permno"].astype(int)
    return out


def _compustat_be(funda: pd.DataFrame, link: pd.DataFrame) -> pd.DataFrame:
    fun = funda.copy()
    fun["gvkey"] = fun["gvkey"].astype(str).str.zfill(6)
    fun["datadate"] = pd.to_datetime(fun["datadate"])
    fun["be"] = book_equity_frame(fun)
    fun = fun[np.isfinite(fun["be"]) & (fun["be"] > 0)]
    fun["year"] = fun["datadate"].dt.year.astype(int)
    fun = fun.sort_values(["gvkey", "datadate"]).drop_duplicates(
        ["gvkey", "year"], keep="last"
    )
    lnk = link.copy()
    lnk["gvkey"] = lnk["gvkey"].astype(str).str.zfill(6)
    lnk["permno"] = pd.to_numeric(lnk["lpermno"], errors="coerce")
    lnk["linkdt"] = pd.to_datetime(lnk["linkdt"])
    lnk["linkenddt"] = pd.to_datetime(lnk["linkenddt"]).fillna(pd.Timestamp("2099-12-31"))
    merged = fun.merge(
        lnk[["gvkey", "permno", "linkdt", "linkenddt"]], on="gvkey", how="inner"
    )
    merged = merged[
        (merged["datadate"] >= merged["linkdt"])
        & (merged["datadate"] <= merged["linkenddt"])
        & merged["permno"].notna()
    ]
    merged["permno"] = merged["permno"].astype(int)
    merged = merged.sort_values(["permno", "year", "datadate"]).drop_duplicates(
        ["permno", "year"], keep="last"
    )
    return merged[["permno", "year", "be"]]


def _combine_book(comp_be: pd.DataFrame, hist_be: pd.DataFrame) -> pd.DataFrame:
    hist = hist_be.copy()
    hist["permno"] = pd.to_numeric(hist["permno"], errors="coerce").astype(int)
    hist["year"] = pd.to_numeric(hist["year"], errors="coerce").astype(int)
    hist["be"] = pd.to_numeric(hist["be"], errors="coerce")
    hist = hist[np.isfinite(hist["be"]) & (hist["be"] > 0)]
    hist = hist.rename(columns={"be": "be_h"})
    comp = comp_be.rename(columns={"be": "be_c"})
    both = hist.merge(comp, on=["permno", "year"], how="outer")
    both["be"] = both["be_c"].where(both["be_c"].notna() & (both["be_c"] > 0), both["be_h"])
    return both.loc[both["be"].notna() & (both["be"] > 0), ["permno", "year", "be"]]


def _market_monthly(msi: pd.DataFrame) -> pd.DataFrame:
    m = msi.copy()
    m["date"] = pd.to_datetime(m["date"])
    m["ret"] = pd.to_numeric(m["vwretd"], errors="coerce")
    retx_col = "vwretx" if "vwretx" in m.columns else None
    if retx_col is None:
        raise EmpiricalDataError("crsp.msi is missing vwretx")
    m["retx"] = pd.to_numeric(m[retx_col], errors="coerce")
    m = m.dropna(subset=["date", "ret", "retx"]).drop_duplicates("date")
    return m[["date", "ret", "retx"]]


def _to_cs_series(frame: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    g = frame.sort_values("date").drop_duplicates("date")
    idx = pd.DatetimeIndex(pd.to_datetime(g["date"]))
    ret = pd.Series(pd.to_numeric(g["ret"], errors="coerce").to_numpy(), index=idx)
    retx = pd.Series(pd.to_numeric(g["retx"], errors="coerce").to_numpy(), index=idx)
    return ret, retx


def _annualize(
    monthly: pd.DataFrame,
    market: pd.DataFrame,
    deflator: pd.Series,
    start: int = 1930,
    end: int = 2003,
) -> pd.DataFrame:
    rows = []
    for q, name in _CLAIMS.items():
        ret, retx = _to_cs_series(monthly.loc[monthly["quintile"] == q])
        ann = campbell_shiller_annual(ret, retx, deflator)
        ann["claim"] = name
        rows.append(ann[["year", "claim", "ret", "dgrowth", "pd"]])
    ret, retx = _to_cs_series(market)
    ann = campbell_shiller_annual(ret, retx, deflator)
    ann["claim"] = "Market"
    rows.append(ann[["year", "claim", "ret", "dgrowth", "pd"]])
    out = pd.concat(rows, ignore_index=True)
    out["year"] = out["year"].astype(int)
    out = out[(out["year"] >= start) & (out["year"] <= end)]
    out["claim"] = pd.Categorical(
        out["claim"], categories=["Growth", "Value", "Market"], ordered=True
    )
    return out.sort_values(["claim", "year"]).reset_index(drop=True)


def _write_outputs(
    panel: pd.DataFrame,
    dc: pd.Series,
    rf: pd.Series,
    start: int = 1930,
    end: int = 2003,
) -> None:
    PANEL_CSV.parent.mkdir(parents=True, exist_ok=True)
    panel[["year", "claim", "ret", "dgrowth", "pd"]].to_csv(PANEL_CSV, index=False)
    dc_out = dc.loc[(dc.index >= start) & (dc.index <= end)].rename("dc")
    dc_out.index.name = "year"
    dc_out.reset_index().to_csv(DC_CSV, index=False)
    rf_out = rf.loc[(rf.index >= start) & (rf.index <= end)].rename("rf")
    rf_out.index.name = "year"
    rf_out.reset_index().to_csv(RF_CSV, index=False)


def build_annual_panel(
    refresh: bool = False, start: int = 1930, end: int = 2003
) -> pd.DataFrame:
    """Build the annual book-to-market claims panel for 1930–2003 by default.

    Pulls CRSP from 1925, forms NYSE book-to-market quintiles, and
    Campbell–Shiller annualizes returns, dividend growth, and price-dividend
    ratios. ``start`` / ``end`` cut the public sample; they do not change the
    raw extract window.

    Examples
    --------
    ```python
    import geap
    panel = geap.build_annual_panel()
    ```
    """
    raw = _load_raw(refresh)
    msf = _filter_universe(raw["msf"], raw["names"])
    if msf.empty:
        raise EmpiricalDataError("No ordinary NYSE/AMEX/NASDAQ stocks in CRSP extract")
    book = _combine_book(_compustat_be(raw["funda"], raw["link"]), raw["hist_be"])
    assignments = form_bm_quintiles(msf, book)
    if assignments.empty:
        raise EmpiricalDataError("BM quintile assignments are empty")
    monthly = value_weight_monthly(msf, assignments)
    market = _market_monthly(raw["msi"])
    deflator = load_deflator()
    panel = _annualize(monthly, market, deflator, start=start, end=end)
    if panel.empty or set(panel["claim"].unique()) != {"Growth", "Value", "Market"}:
        raise EmpiricalDataError("Annual panel is missing Growth/Value/Market")
    if panel["ret"].isna().any():
        raise EmpiricalDataError(
            f"Annual panel has missing returns in {start}–{end}"
        )
    dc = load_consumption()
    mcti = raw["mcti"].copy()
    if "cpi" not in mcti.columns and "cpiind" in mcti.columns:
        mcti = mcti.rename(columns={"cpiind": "cpi"})
    mcti["caldt"] = pd.to_datetime(mcti["caldt"])
    t90 = pd.Series(
        pd.to_numeric(mcti["t90ret"], errors="coerce").to_numpy(),
        index=pd.DatetimeIndex(mcti["caldt"]),
        name="t90ret",
    )
    cpi = pd.Series(
        pd.to_numeric(mcti["cpi"], errors="coerce").to_numpy(),
        index=pd.DatetimeIndex(mcti["caldt"]),
        name="cpi",
    )
    rf = real_rf_from_monthly(t90, cpi)
    rf = pd.Series(rf.to_numpy(), index=pd.Index(rf.index.year.astype(int), name="year"), name="rf")
    rf = rf[~rf.index.duplicated(keep="last")].sort_index()
    _write_outputs(panel, dc, rf, start=start, end=end)
    return panel
