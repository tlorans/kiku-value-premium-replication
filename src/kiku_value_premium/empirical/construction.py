from __future__ import annotations

import numpy as np
import pandas as pd


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
        labeled["quintile"] = nyse_quintile_labels(
            labeled["bm"].to_numpy(dtype=float), nyse
        )
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
    work["ret"] = pd.to_numeric(work["ret"], errors="coerce")
    work["retx"] = pd.to_numeric(work["retx"], errors="coerce")
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
