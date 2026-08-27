from __future__ import annotations

import numpy as np
import pandas as pd
import tidyfinance as tf

_CRSP_BAD = (-66.0, -77.0, -88.0, -99.0)


def crsp_return(s) -> pd.Series:
    """Numeric CRSP return; letter/sentinel missing codes become NaN."""
    x = pd.to_numeric(s, errors="coerce")
    return x.mask(x.isin(_CRSP_BAD))


def _compound_delist(ret: pd.Series, dlret: pd.Series) -> pd.Series:
    both = ret.notna() & dlret.notna()
    only = ret.isna() & dlret.notna()
    out = ret.copy()
    out.loc[both] = (1.0 + ret.loc[both]) * (1.0 + dlret.loc[both]) - 1.0
    out.loc[only] = dlret.loc[only]
    return out


def apply_delisting_returns(msf: pd.DataFrame, delist: pd.DataFrame) -> pd.DataFrame:
    """Compound CRSP monthly ret/retx with the delisting increment (Fama–French).

    Never substitutes ``ret`` for missing ``retx`` / ``dlretx``. Performance-related
    delists (codes 400–599) with no CRSP delisting return get −30% on both sides.
    """
    out = msf.copy()
    out["date"] = pd.to_datetime(out["date"])
    out["permno"] = pd.to_numeric(out["permno"], errors="coerce")
    out["ret"] = crsp_return(out["ret"])
    out["retx"] = crsp_return(out["retx"])
    out["month"] = out["date"].dt.to_period("M")
    dl = delist.copy()
    dl["permno"] = pd.to_numeric(dl["permno"], errors="coerce")
    dl["dlstdt"] = pd.to_datetime(dl["dlstdt"])
    dl["dlret"] = crsp_return(dl["dlret"])
    if "dlretx" in dl.columns:
        dl["dlretx"] = crsp_return(dl["dlretx"])
    else:
        dl["dlretx"] = np.nan
    dl["dlstcd"] = pd.to_numeric(dl["dlstcd"], errors="coerce") if "dlstcd" in dl.columns else np.nan
    dl["month"] = dl["dlstdt"].dt.to_period("M")
    dl = dl.sort_values("dlstdt").drop_duplicates(["permno", "month"], keep="last")
    m = out.merge(
        dl[["permno", "month", "dlret", "dlretx", "dlstcd"]],
        on=["permno", "month"],
        how="left",
    )
    m["ret"] = _compound_delist(m["ret"], m["dlret"])
    m["retx"] = _compound_delist(m["retx"], m["dlretx"])
    perf = m["dlstcd"].between(400, 599)
    m.loc[perf & m["ret"].isna(), "ret"] = -0.30
    m.loc[perf & m["retx"].isna(), "retx"] = -0.30

    matched = set(zip(m["permno"], m["month"]))
    last = out.sort_values("date").groupby("permno", sort=False).tail(1)
    last_map = last.set_index("permno")
    extras = []
    for rec in dl.itertuples(index=False):
        if (rec.permno, rec.month) in matched or rec.permno not in last_map.index:
            continue
        stcd = rec.dlstcd
        ret = rec.dlret if np.isfinite(rec.dlret) else (
            -0.30 if np.isfinite(stcd) and 400 <= stcd <= 599 else np.nan
        )
        retx = rec.dlretx if np.isfinite(rec.dlretx) else (
            -0.30 if np.isfinite(stcd) and 400 <= stcd <= 599 else np.nan
        )
        if not np.isfinite(ret) and not np.isfinite(retx):
            continue
        prev = last_map.loc[rec.permno]
        extras.append(
            {
                "permno": rec.permno,
                "date": rec.month.to_timestamp(how="end").normalize(),
                "ret": ret,
                "retx": retx,
                "prc": prev["prc"],
                "shrout": prev["shrout"],
                "exchcd": prev["exchcd"] if "exchcd" in last_map.columns else np.nan,
            }
        )
    m = m.drop(columns=["month", "dlret", "dlretx", "dlstcd"], errors="ignore")
    if extras:
        extra = pd.DataFrame(extras)
        for col in m.columns:
            if col not in extra.columns:
                extra[col] = np.nan
        m = pd.concat([m, extra[list(m.columns)]], ignore_index=True)
    return m


def book_equity(seq, txditc, pstkrv, pstkl, pstk) -> float:
    preferred = 0.0
    for cand in (pstkrv, pstkl, pstk):
        if np.isfinite(cand):
            preferred = float(cand)
            break
    tax = 0.0 if not np.isfinite(txditc) else float(txditc)
    return float(seq) + tax - preferred


def nyse_quintile_labels(bm_all, bm_nyse) -> np.ndarray:
    edges = np.quantile(np.asarray(bm_nyse, dtype=float), [0.2, 0.4, 0.6, 0.8])
    return np.digitize(np.asarray(bm_all, dtype=float), edges, right=True) + 1


def book_equity_frame(df: pd.DataFrame) -> pd.Series:
    preferred = pd.to_numeric(df["pstkrv"], errors="coerce")
    for col in ("pstkl", "pstk"):
        alt = pd.to_numeric(df[col], errors="coerce")
        preferred = preferred.where(np.isfinite(preferred), alt)
    preferred = preferred.fillna(0.0)
    tax = pd.to_numeric(df["txditc"], errors="coerce").fillna(0.0)
    seq = pd.to_numeric(df["seq"], errors="coerce")
    return seq + tax - preferred


def form_bm_quintiles(msf: pd.DataFrame, book: pd.DataFrame) -> pd.DataFrame:
    """June NYSE-breakpoint BM quintiles (1=Growth, 5=Value).

    ``book`` is PERMNO-level BE indexed by calendar year of fiscal year-end.
    """
    work = msf.copy()
    work["date"] = pd.to_datetime(work["date"])
    work["me"] = (
        work["prc"].abs() * pd.to_numeric(work["shrout"], errors="coerce") / 1000.0
    )
    work["year"] = work["date"].dt.year
    work["month"] = work["date"].dt.month
    june = work.loc[work["month"] == 6, ["permno", "year", "me", "exchcd"]].rename(
        columns={"year": "sort_year", "me": "me_june"}
    )
    dec = work.loc[work["month"] == 12, ["permno", "year", "me"]].rename(
        columns={"me": "me_dec"}
    )
    dec["sort_year"] = dec["year"] + 1
    be = book.copy()
    be["sort_year"] = be["year"] + 1
    asg = june.merge(
        dec[["permno", "sort_year", "me_dec"]], on=["permno", "sort_year"], how="inner"
    )
    asg = asg.merge(
        be[["permno", "sort_year", "be"]], on=["permno", "sort_year"], how="inner"
    )
    asg = asg[(asg["me_june"] > 0) & (asg["me_dec"] > 0) & (asg["be"] > 0)].copy()
    asg["bm"] = asg["be"] / asg["me_dec"]
    rows = []
    for _, g in asg.groupby("sort_year"):
        nyse = g.loc[g["exchcd"] == 1, "bm"].to_numpy(dtype=float)
        nyse = nyse[np.isfinite(nyse)]
        if nyse.size < 5:
            continue
        labeled = g.copy()
        labeled["exchange"] = labeled["exchcd"].map(
            {1: "NYSE", 2: "AMEX", 3: "NASDAQ"}
        )
        labeled["quintile"] = tf.assign_portfolio(
            labeled,
            sorting_variable="bm",
            breakpoint_options=tf.breakpoint_options(
                n_portfolios=5,
                breakpoints_exchanges="NYSE",
            ),
            data_options=tf.data_options(exchange="exchange"),
        ).astype(int)
        rows.append(labeled[["permno", "sort_year", "quintile", "me_june"]])
    if not rows:
        return pd.DataFrame(columns=["permno", "sort_year", "quintile", "me_june"])
    return pd.concat(rows, ignore_index=True)


def value_weight_monthly(msf: pd.DataFrame, assignments: pd.DataFrame) -> pd.DataFrame:
    """Value-weight monthly ret/retx by quintile; hold July t through June t+1."""
    work = msf.copy()
    work["date"] = pd.to_datetime(work["date"])
    work["year"] = work["date"].dt.year.astype(int)
    work["month"] = work["date"].dt.month.astype(int)
    work["sort_year"] = np.where(work["month"] >= 7, work["year"], work["year"] - 1)
    work["me"] = (
        work["prc"].abs() * pd.to_numeric(work["shrout"], errors="coerce") / 1000.0
    )
    work = work.sort_values(["permno", "date"])
    work["lag_me"] = work.groupby("permno", sort=False)["me"].shift(1)
    work["lag_prc"] = work.groupby("permno", sort=False)["prc"].shift(1)
    work["ret"] = crsp_return(work["ret"])
    work["retx"] = crsp_return(work["retx"])
    # Missing retx: infer capital gain from prices. Never fill retx with ret
    # (that would force Campbell–Shiller d = (ret-retx)*v to zero).
    need = work["retx"].isna() & work["ret"].notna()
    cg = work["prc"].abs() / work["lag_prc"].abs() - 1.0
    work["retx"] = work["retx"].where(~need, cg)
    port = work.merge(assignments, on=["permno", "sort_year"], how="inner")
    port["w"] = port["lag_me"].where(port["lag_me"] > 0, port["me_june"])
    port = port[
        np.isfinite(port["ret"])
        & np.isfinite(port["retx"])
        & (port["w"] > 0)
        & port["quintile"].isin((1, 5))
    ].copy()
    port["w_ret"] = port["w"] * port["ret"]
    port["w_retx"] = port["w"] * port["retx"]
    agg = port.groupby(["date", "quintile"], sort=True).agg(
        w=("w", "sum"), w_ret=("w_ret", "sum"), w_retx=("w_retx", "sum")
    )
    return pd.DataFrame(
        {
            "date": agg.index.get_level_values("date"),
            "quintile": agg.index.get_level_values("quintile"),
            "ret": agg["w_ret"] / agg["w"],
            "retx": agg["w_retx"] / agg["w"],
        }
    ).reset_index(drop=True)
