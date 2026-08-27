from __future__ import annotations

import numpy as np
import pandas as pd


def real_rf_from_monthly(t90ret: pd.Series, cpi: pd.Series) -> pd.Series:
    """Annual real T-bill: monthly T-bill minus 12-month MA of log CPI inflation."""
    idx = t90ret.index.intersection(cpi.index)
    t90 = t90ret.loc[idx].astype(float).sort_index()
    price = cpi.loc[idx].astype(float).sort_index()
    inflation = np.log(price / price.shift(1))
    real = t90 - inflation.rolling(12).mean()
    annual = real.resample("YE").mean()
    annual.name = "rf"
    return annual
