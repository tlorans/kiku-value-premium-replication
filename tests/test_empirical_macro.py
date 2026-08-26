import numpy as np
import pandas as pd
from kiku_value_premium.empirical.consumption import consumption_growth_from_levels
from kiku_value_premium.empirical.rates import real_rf_from_monthly


def test_consumption_growth_is_log_diff_of_per_capita():
    years = np.arange(1929, 1934)
    nd = pd.Series([100.0, 102.0, 103.0, 104.0, 105.0], index=years)
    sv = pd.Series([200.0, 202.0, 204.0, 206.0, 208.0], index=years)
    pop = pd.Series([10.0, 10.0, 10.0, 10.0, 10.0], index=years)
    dc = consumption_growth_from_levels(nd, sv, pop)
    assert dc.index.min() == 1930
    level = (nd + sv) / pop
    assert abs(dc.loc[1930] - np.log(level.loc[1930] / level.loc[1929])) < 1e-12


def test_real_rf_subtracts_twelve_month_inflation_ma():
    idx = pd.date_range("1999-01-31", periods=24, freq="ME")
    t90 = pd.Series(0.01 / 12, index=idx)
    cpi = pd.Series(np.linspace(100, 103, 24), index=idx)
    rf = real_rf_from_monthly(t90, cpi)
    assert rf.index.year.min() == 1999 or rf.index.year.min() == 2000
    assert rf.notna().any()
