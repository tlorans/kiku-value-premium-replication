"""Annual (1930–2015) and quarterly (1948–2015) samples for BKY (2016)."""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import pandas as pd

from ..empirical.consumption import load_consumption, load_consumption_quarterly
from ..empirical.dividends import campbell_shiller_annual

ROOT = Path(__file__).resolve().parents[4]
ANNUAL_CSV = ROOT / "data" / "bky_annual.csv"
QUARTERLY_CSV = ROOT / "data" / "bky_quarterly.csv"
CROSS_CSV = ROOT / "data" / "bky_cross_section.csv"
BKY_RAW = ROOT / "data" / "raw"
MSI_PARQUET = BKY_RAW / "bky_msi.parquet"
MCTI_PARQUET = BKY_RAW / "bky_mcti.parquet"
CRSP_START = "1925-12-01"
CRSP_END = "2015-12-31"

BKY_START = 1930
BKY_END = 2015
QUARTERLY_START = 1948


def load_annual(
    path: Path | None = None,
    *,
    start: int = BKY_START,
    end: int = BKY_END,
) -> pd.DataFrame:
    """Shipped annual real consumption, CRSP VW market, P/D, and T-bill.

    Columns: ``year``, ``dc``, ``dd``, ``rm``, ``log_pd``, ``rf``.
    Rebuild with :func:`build_annual`.
    """
    csv = Path(path) if path is not None else ANNUAL_CSV
    if not csv.exists():
        raise FileNotFoundError(
            f"Missing {csv}. Rebuild with geap.lrr.estimation.data.build_annual()."
        )
    df = pd.read_csv(csv)
    out = df[(df["year"] >= start) & (df["year"] <= end)].copy()
    return out.sort_values("year").reset_index(drop=True)


def load_quarterly(
    path: Path | None = None,
    *,
    start: int = QUARTERLY_START,
    end: int = BKY_END,
) -> pd.DataFrame:
    """Shipped quarterly real consumption, dividends, market, P/D, and T-bill.

    Columns: ``date``, ``dc``, ``dd``, ``rm``, ``log_pd``, ``rf``.
    """
    csv = Path(path) if path is not None else QUARTERLY_CSV
    if not csv.exists():
        raise FileNotFoundError(
            f"Missing {csv}. Rebuild with geap.lrr.estimation.data.build_quarterly()."
        )
    df = pd.read_csv(csv, parse_dates=["date"])
    years = df["date"].dt.year
    out = df[(years >= start) & (years <= end)].copy()
    return out.sort_values("date").reset_index(drop=True)


def load_cross_section(path: Path | None = None) -> pd.DataFrame:
    """Annual real returns, dividend growth, and log P/D for size and B/M legs.

    Columns: ``year``, ``claim``, ``ret``, ``dgrowth``, ``pd``.
    Claims are ``small``, ``large``, ``growth``, ``value``.
    """
    csv = Path(path) if path is not None else CROSS_CSV
    if not csv.exists():
        raise FileNotFoundError(
            f"Missing {csv}. Rebuild with "
            "geap.lrr.estimation.data.build_cross_section()."
        )
    df = pd.read_csv(csv)
    return df.sort_values(["year", "claim"]).reset_index(drop=True)


def _ensure_wrds_env() -> None:
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            s = line.strip()
            if not s or s.startswith("#") or "=" not in s:
                continue
            key, _, val = s.partition("=")
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val
    if not os.environ.get("WRDS_USER") and os.environ.get("WRDS_USERNAME"):
        os.environ["WRDS_USER"] = os.environ["WRDS_USERNAME"]


def _crsp_msi_mcti(refresh: bool = False) -> tuple[pd.DataFrame, pd.DataFrame]:
    """CRSP VW index and CPI/T-bill (BKY 2016 market and real rate)."""
    from ..empirical.wrds import _download_crsp_mcti, _download_crsp_msi

    BKY_RAW.mkdir(parents=True, exist_ok=True)
    if refresh or not MSI_PARQUET.exists() or not MCTI_PARQUET.exists():
        _ensure_wrds_env()
        msi = _download_crsp_msi(CRSP_START, CRSP_END)
        mcti = _download_crsp_mcti(CRSP_START, CRSP_END)
        msi.to_parquet(MSI_PARQUET, index=False)
        mcti.to_parquet(MCTI_PARQUET, index=False)
    else:
        msi = pd.read_parquet(MSI_PARQUET)
        mcti = pd.read_parquet(MCTI_PARQUET)
    return msi, mcti


def _cpi_by_year(mcti: pd.DataFrame) -> pd.Series:
    m = mcti.copy()
    m.columns = [str(c).lower() for c in m.columns]
    if "cpi" not in m.columns and "cpiind" in m.columns:
        m = m.rename(columns={"cpiind": "cpi"})
    date_col = "caldt" if "caldt" in m.columns else "date"
    m[date_col] = pd.to_datetime(m[date_col])
    m["cpi"] = pd.to_numeric(m["cpi"], errors="coerce")
    s = m.dropna(subset=["cpi"]).set_index(date_col)["cpi"].sort_index()
    annual = s.resample("YE").last().dropna()
    return pd.Series(annual.to_numpy(), index=annual.index.year.astype(int), name="cpi")


def _mcti_monthly(mcti: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    m = mcti.copy()
    m.columns = [str(c).lower() for c in m.columns]
    if "cpi" not in m.columns and "cpiind" in m.columns:
        m = m.rename(columns={"cpiind": "cpi"})
    date_col = "caldt" if "caldt" in m.columns else "date"
    m[date_col] = pd.to_datetime(m[date_col])
    m = m.dropna(subset=[date_col]).set_index(date_col).sort_index()
    t90 = pd.to_numeric(m["t90ret"], errors="coerce")
    cpi = pd.to_numeric(m["cpi"], errors="coerce")
    return t90, cpi


def _ex_ante_real_rate(nom: pd.Series, infl: pd.Series) -> pd.Series:
    """Bansal, Kiku, and Yaron (2012): fitted ex-post real T-bill.

    Regress the ex-post real three-month bill on the nominal rate and
    past inflation. The fitted value is the ex-ante real rate.
    """
    ex_post = nom - infl
    lag = infl.shift(1)
    ok = ex_post.notna() & nom.notna() & lag.notna()
    a = np.column_stack(
        [
            np.ones(int(ok.sum())),
            nom[ok].to_numpy(dtype=float),
            lag[ok].to_numpy(dtype=float),
        ]
    )
    coef, *_ = np.linalg.lstsq(a, ex_post[ok].to_numpy(dtype=float), rcond=None)
    fitted = coef[0] + coef[1] * nom + coef[2] * lag
    fitted.name = "rf"
    return fitted


def _rf_from_mcti(mcti: pd.DataFrame) -> pd.Series:
    """Annual ex-ante real T-bill from CRSP ``t90ret`` and CPI."""
    t90, cpi = _mcti_monthly(mcti)
    nom = (1.0 + t90).resample("YE").prod() - 1.0
    pi = cpi.resample("YE").last().pct_change()
    rf = _ex_ante_real_rate(nom, pi).dropna()
    out = pd.Series(rf.to_numpy(), index=rf.index.year.astype(int), name="rf")
    return out[~out.index.duplicated(keep="last")].sort_index()


def build_annual(path: Path | None = None, *, refresh: bool = False) -> pd.DataFrame:
    """1930–2015 annual sample from the JME paper's sources.

    Market returns, dividends, and P/D are the CRSP value-weighted
    NYSE/AMEX/NASDAQ index (``crsp.msi``), Campbell–Shiller per-share,
    deflated with the BLS CPI on WRDS (``crsp.mcti``). Consumption is
    BEA NIPA real per-capita nondurables and services (FRED). The real
    T-bill is the Bansal, Kiku, and Yaron (2012) fitted ex-post real
    90-day bill.
    """
    from ..empirical.panel import _market_monthly, _to_cs_series

    msi, mcti = _crsp_msi_mcti(refresh=refresh)
    ret, retx = _to_cs_series(_market_monthly(msi))
    ann = campbell_shiller_annual(ret, retx, _cpi_by_year(mcti)).set_index("year")
    dc = load_consumption()
    rf = _rf_from_mcti(mcti)
    years = np.arange(BKY_START, BKY_END + 1)
    out = pd.DataFrame(
        {
            "year": years,
            "dc": dc.reindex(years).to_numpy(),
            "dd": ann["dgrowth"].reindex(years).to_numpy(),
            "rm": ann["ret"].reindex(years).to_numpy(),
            "log_pd": np.log(ann["pd"].reindex(years).to_numpy(dtype=float)),
            "rf": rf.reindex(years).to_numpy(),
        }
    )
    out = out.dropna().reset_index(drop=True)
    csv = Path(path) if path is not None else ANNUAL_CSV
    csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(csv, index=False)
    return out


def sample_moments(data: pd.DataFrame) -> dict[str, float]:
    """Table 1 descriptive statistics on an annual sample."""
    d = data.set_index("year")
    def _ms(col: str) -> tuple[float, float]:
        x = d[col].astype(float).to_numpy()
        x = x[np.isfinite(x)]
        return float(x.mean()), float(x.std(ddof=1))

    out = {}
    for name, col in (
        ("dc", "dc"),
        ("dd", "dd"),
        ("rm", "rm"),
        ("log_pd", "log_pd"),
        ("rf", "rf"),
    ):
        mu, sd = _ms(col)
        out[f"{name}_mean"] = mu
        out[f"{name}_std"] = sd
    return out


def _shiller_monthlies() -> pd.DataFrame:
    """December-or-quarterly rows from Shiller's ie_data.xls (cached in memory)."""
    import urllib.request

    import xlrd

    url = "http://www.econ.yale.edu/~shiller/data/ie_data.xls"
    dest = ROOT / "data" / "_shiller.xls"
    if not dest.exists():
        urllib.request.urlretrieve(url, dest)
    raw = pd.read_excel(dest, sheet_name="Data", header=None, skiprows=8)
    raw = raw.iloc[:, :12]
    raw.columns = [
        "date", "P", "D", "E", "CPI", "frac", "gs10", "rP", "rD", "rTR", "rE", "rTRe",
    ]
    raw["date"] = pd.to_numeric(raw["date"], errors="coerce")
    raw = raw.dropna(subset=["date", "P", "D"])
    raw["year"] = (raw["date"] // 1).astype(int)
    raw["month"] = np.round((raw["date"] % 1) * 100).astype(int).clip(1, 12)
    return raw


def _french_monthly_rf() -> pd.Series:
    import tidyfinance as tf

    ff = tf.download_data(
        "factors_ff_3_monthly", start_date="1926-01-01", end_date="2016-12-31"
    )
    ff = ff.copy()
    ff["dt"] = pd.to_datetime(ff["date"]).dt.to_period("M").dt.to_timestamp()
    return ff.set_index("dt")["risk_free"].astype(float)


def _quarterly_market(ret: pd.Series, retx: pd.Series, cpi: pd.Series) -> pd.DataFrame:
    """Campbell–Shiller at the quarter: P over trailing four-quarter dividends."""
    idx = ret.index.intersection(retx.index).intersection(cpi.index)
    r = ret.loc[idx].astype(float).sort_index()
    rx = retx.loc[idx].astype(float)
    price = cpi.loc[idx].astype(float)
    v = 100.0
    rows = []
    for dt in r.index:
        ri, rxi = float(r.loc[dt]), float(rx.loc[dt])
        if not np.isfinite(ri) or not np.isfinite(rxi):
            continue
        d = (ri - rxi) * v
        v = v * (1.0 + rxi)
        rows.append((dt, v, max(d, 0.0), ri))
    m = pd.DataFrame(rows, columns=["date", "v", "d", "r"]).set_index("date")
    m["cpi"] = price.reindex(m.index)
    q_v = m["v"].resample("QE").last()
    q_d = m["d"].resample("QE").sum()
    q_r = (1.0 + m["r"]).resample("QE").prod() - 1.0
    q_cpi = m["cpi"].resample("QE").last()
    trail = q_d.rolling(4).sum()
    pd_q = q_v / trail.replace(0.0, np.nan)
    dd = np.log(q_d.where(q_d > 0)).diff()
    infl = q_cpi.pct_change()
    rm = (1.0 + q_r) * (q_cpi.shift(1) / q_cpi) - 1.0
    out = pd.DataFrame(
        {"dd": dd, "rm": rm, "log_pd": np.log(pd_q), "cpi": q_cpi}
    )
    return out


def build_quarterly(path: Path | None = None, *, refresh: bool = False) -> pd.DataFrame:
    """1948–2015 quarterly sample from CRSP VW, BLS CPI, and NIPA."""
    from ..empirical.panel import _market_monthly, _to_cs_series

    msi, mcti = _crsp_msi_mcti(refresh=refresh)
    ret, retx = _to_cs_series(_market_monthly(msi))
    t90, cpi = _mcti_monthly(mcti)
    cpi = cpi.copy()
    cpi.index = pd.DatetimeIndex(cpi.index)
    mkt = _quarterly_market(ret, retx, cpi)
    nom_q = (1.0 + t90).resample("QE").prod() - 1.0
    pi_q = cpi.resample("QE").last().pct_change()
    rf_q = _ex_ante_real_rate(nom_q, pi_q)
    dc = load_consumption_quarterly()
    dc.index = dc.index + pd.offsets.QuarterEnd(0)
    out = pd.DataFrame(
        {
            "date": mkt.index,
            "dc": dc.reindex(mkt.index).to_numpy(),
            "dd": mkt["dd"].to_numpy(),
            "rm": mkt["rm"].to_numpy(),
            "log_pd": mkt["log_pd"].to_numpy(),
            "rf": rf_q.reindex(mkt.index).to_numpy(),
        }
    )
    years = pd.to_datetime(out["date"]).dt.year
    out = out[(years >= QUARTERLY_START) & (years <= BKY_END)].dropna()
    csv = Path(path) if path is not None else QUARTERLY_CSV
    csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(csv, index=False)
    return out.reset_index(drop=True)


def _french_portfolio(kind: str, with_div: bool) -> pd.DataFrame:
    import tidyfinance as tf

    key = {
        ("size", True): "factors_ff_size_monthly",
        ("size", False): "factors_ff_size_exdividends_monthly",
        ("bm", True): "factors_ff_bm_monthly",
        ("bm", False): "factors_ff_bm_exdividends_monthly",
    }[(kind, with_div)]
    df = tf.download_data(key, start_date="1926-07-01", end_date="2016-12-31")
    df = df.copy()
    df["date"] = pd.to_datetime(df["date"])
    return df.set_index("date")


def build_cross_section(path: Path | None = None, *, refresh: bool = False) -> pd.DataFrame:
    """Annual Campbell–Shiller P/D for CRSP size and B/M 20% legs.

    Ken French lo20/hi20 are CRSP value-weighted NYSE/AMEX/NASDAQ
    portfolios. Returns are deflated with the BLS CPI on WRDS.
    """
    _, mcti = _crsp_msi_mcti(refresh=refresh)
    deflator = _cpi_by_year(mcti)
    legs = {
        "small": ("size", "lo 20"),
        "large": ("size", "hi 20"),
        "growth": ("bm", "lo 20"),
        "value": ("bm", "hi 20"),
    }
    frames = []
    for claim, (kind, col) in legs.items():
        ret = _french_portfolio(kind, True)[col].astype(float)
        retx = _french_portfolio(kind, False)[col].astype(float)
        ann = campbell_shiller_annual(ret, retx, deflator)
        ann = ann[(ann["year"] >= BKY_START) & (ann["year"] <= BKY_END)]
        piece = pd.DataFrame(
            {
                "year": ann["year"].to_numpy(),
                "claim": claim,
                "ret": ann["ret"].to_numpy(),
                "dgrowth": ann["dgrowth"].to_numpy(),
                "pd": ann["pd"].to_numpy(),
            }
        )
        frames.append(piece)
    out = pd.concat(frames, ignore_index=True)
    csv = Path(path) if path is not None else CROSS_CSV
    csv.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(csv, index=False)
    return out
