"""Time-aggregated simulation at Table 2 parameters."""
from __future__ import annotations

import numpy as np
import pytest

from geap.lrr.estimation.aggregation import model_moments
from geap.lrr.estimation.goldens import TABLE_2_LRR, TABLE_2_LRR_H, TABLE_3_LRR_MODEL
from geap.lrr.estimation.simulate import simulate_annual


def test_simulated_annual_consumption_mean_is_h_mu():
    sim = simulate_annual(TABLE_2_LRR, TABLE_2_LRR_H, years=400, seed=1, burn_in=20)
    assert sim["dc"].mean() == pytest.approx(TABLE_2_LRR_H * TABLE_2_LRR.mu_c, abs=0.01)
    assert sim["rf"].mean() == pytest.approx(0.010, abs=0.01)


def test_closed_form_corr_dc_zd_matches_simulation_not_the_paper_cell():
    """The printed 0.240 is not the log-linear population correlation.

    A long simulated annual panel at Table 2 lands on the closed form
    (~0.176), not on Table 3's model column.
    """
    sim = simulate_annual(TABLE_2_LRR, TABLE_2_LRR_H, years=4000, seed=0, burn_in=40)
    dc = sim["dc"].to_numpy(dtype=float)
    z = sim["log_pd"].to_numpy(dtype=float)
    ok = np.isfinite(dc) & np.isfinite(z)
    dc, z = dc[ok], z[ok]
    sim_corr = float(np.corrcoef(dc[1:], z[:-1])[0, 1])
    closed = model_moments(TABLE_2_LRR, TABLE_2_LRR_H)["corr_dc_zd"]
    assert sim_corr == pytest.approx(closed, abs=0.04)
    assert abs(closed - TABLE_3_LRR_MODEL["corr_dc_zd"]) > 0.03


def test_simulated_market_return_is_simple_and_carries_its_shocks():
    # rm follows the data panel: a simple annual return, so its log is
    # the model's r_d, shocks included.
    sim = simulate_annual(TABLE_2_LRR, TABLE_2_LRR_H, years=4000, seed=0, burn_in=40)
    m = model_moments(TABLE_2_LRR, TABLE_2_LRR_H)
    rm = sim["rm"].to_numpy(dtype=float)
    rf = sim["rf"].to_numpy(dtype=float)
    assert np.all(rm > -1.0)
    assert np.std(np.log1p(rm), ddof=1) == pytest.approx(m["vol_rd"], rel=0.1)
    assert np.mean(rm - rf) == pytest.approx(m["mean_excess"], abs=0.015)
