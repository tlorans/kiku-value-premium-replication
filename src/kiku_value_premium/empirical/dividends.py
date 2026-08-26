from __future__ import annotations

import numpy as np
import pandas as pd


def campbell_shiller_annual(
    ret: pd.Series, retx: pd.Series, deflator: pd.Series
) -> pd.DataFrame:
    """Annual real return, log dividend growth, and year-end P/D."""
    idx = ret.index.intersection(retx.index)
    r = ret.loc[idx].astype(float)
    rx = retx.loc[idx].astype(float)
    v = 100.0
    rows = []
    year_div = {}
    year_v = {}
    year_ret = {}
    for dt in r.index:
        ri = r.loc[dt]
        rxi = rx.loc[dt]
        if not np.isfinite(ri) or not np.isfinite(rxi):
            continue
        d = (ri - rxi) * v
        v = v * (1.0 + rxi)
        year = int(dt.year)
        year_div[year] = year_div.get(year, 0.0) + max(d, 0.0)
        year_v[year] = v
        year_ret.setdefault(year, 1.0)
        year_ret[year] *= 1.0 + ri
    years = sorted(year_div)
    for y in years:
        rows.append(
            {
                "year": y,
                "ret": year_ret[y] - 1.0,
                "div": year_div[y],
                "v": year_v[y],
            }
        )
    out = pd.DataFrame(rows)
    out["defl"] = out["year"].map(deflator)
    out["div_real"] = out["div"] / out["defl"]
    out["v_real"] = out["v"] / out["defl"]
    out["pd"] = np.where(out["div_real"] > 0, out["v_real"] / out["div_real"], np.nan)
    pos = out["div_real"].where(out["div_real"] > 0)
    out["dgrowth"] = np.log(pos).diff()
    prev = out["defl"].shift(1)
    out["ret"] = (1.0 + out["ret"]) * (prev / out["defl"]) - 1.0
    return out
