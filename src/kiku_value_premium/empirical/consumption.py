from __future__ import annotations

import io
import urllib.request

import numpy as np
import pandas as pd

_FRED_CSV = "https://fred.stlouisfed.org/graph/fredgraph.csv?id={id}"
_ND = "DNDGRA3A086NBEA"
_SV = "DSERRA3A086NBEA"
_POP = "B230RC0A052NBEA"
_DEFL = "DPCERD3A086NBEA"


def consumption_growth_from_levels(
    nd: pd.Series, sv: pd.Series, pop: pd.Series
) -> pd.Series:
    """Log growth of real per-capita nondurables + services."""
    level = (nd.astype(float) + sv.astype(float)) / pop.astype(float)
    return np.log(level).diff().dropna()


def _fred_annual_series(series_id: str, timeout: float = 30.0) -> pd.Series:
    url = _FRED_CSV.format(id=series_id)
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        raw = resp.read().decode()
    df = pd.read_csv(io.StringIO(raw))
    date_col = df.columns[0]
    value_col = df.columns[1]
    years = pd.to_datetime(df[date_col]).dt.year.astype(int)
    s = pd.Series(pd.to_numeric(df[value_col], errors="coerce").to_numpy(), index=years)
    s = s[~s.index.duplicated(keep="last")].sort_index()
    s.name = series_id
    return s


def load_consumption() -> pd.Series:
    """Annual log growth of real per-capita ND+S from FRED NIPA series."""
    nd = _fred_annual_series(_ND)
    sv = _fred_annual_series(_SV)
    pop = _fred_annual_series(_POP)
    idx = nd.index.intersection(sv.index).intersection(pop.index)
    dc = consumption_growth_from_levels(nd.loc[idx], sv.loc[idx], pop.loc[idx])
    dc.name = "dc"
    return dc


def load_deflator() -> pd.Series:
    """Annual PCE implicit price deflator from FRED (DPCERD3A086NBEA)."""
    return _fred_annual_series(_DEFL)
