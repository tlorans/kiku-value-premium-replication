import numpy as np
from kiku_value_premium.empirical.goldens import (
    END,
    FIGURE2_START,
    START,
    TABLE_I,
    TABLE_VI_PHI,
)
from kiku_value_premium.empirical.tables import newey_west_mean, within_se


def test_windows():
    assert START == 1930
    assert END == 2003
    assert FIGURE2_START == 1952


def test_table_i_value_mean_return_golden():
    mu, se = TABLE_I["Value"]["ret_mean"]
    assert mu == 13.88
    assert se == 1.74


def test_table_vi_phi_goldens():
    assert TABLE_VI_PHI["Growth"] == (-0.38, 1.34)
    assert TABLE_VI_PHI["Value"] == (2.16, 1.44)
    assert TABLE_VI_PHI["Market"] == (0.66, 1.20)


def test_newey_west_mean_constant_series():
    mu, se = newey_west_mean(np.ones(20), lags=8)
    assert abs(mu - 1.0) < 1e-12
    assert se == 0.0


def test_within_se_accepts_on_band():
    assert within_se(13.88 + 1.74, 13.88, 1.74)
    assert not within_se(13.88 + 1.75, 13.88, 1.74)
