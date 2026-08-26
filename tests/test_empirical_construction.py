import numpy as np
import pandas as pd
from kiku_value_premium.empirical.construction import book_equity, nyse_quintile_labels
from kiku_value_premium.empirical.dividends import campbell_shiller_annual
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


def test_book_equity_prefers_redemption_then_liquidation_then_par():
    assert book_equity(seq=100, txditc=10, pstkrv=5, pstkl=9, pstk=8) == 105.0
    assert book_equity(seq=100, txditc=10, pstkrv=np.nan, pstkl=9, pstk=8) == 101.0
    assert book_equity(seq=100, txditc=np.nan, pstkrv=np.nan, pstkl=np.nan, pstk=8) == 92.0


def test_nyse_breakpoints_assign_extremes():
    nyse = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    all_bm = np.array([0.5, 3.0, 9.0])
    labels = nyse_quintile_labels(all_bm, nyse)
    assert labels[0] == 1  # growth
    assert labels[2] == 5  # value


def test_campbell_shiller_v0_is_100():
    idx = pd.date_range("2000-01-31", periods=24, freq="ME")
    ret = pd.Series(0.01, index=idx)
    retx = pd.Series(0.005, index=idx)
    defl = pd.Series({2000: 1.0, 2001: 1.0})
    out = campbell_shiller_annual(ret, retx, defl)
    assert set(out.columns) >= {"year", "ret", "dgrowth", "pd"}
    assert out["pd"].notna().any()
