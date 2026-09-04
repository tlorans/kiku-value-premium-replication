"""Time-aggregated moments at the published Table 2 LRR parameters."""
from __future__ import annotations

import numpy as np
import pytest

from geap.lrr.estimation.aggregation import model_moments
from geap.lrr.estimation.goldens import (
    TABLE_2_LRR,
    TABLE_2_LRR_H,
    TABLE_2_NOVOL,
    TABLE_2_NOVOL_H,
    TABLE_3_LRR_MODEL,
    TABLE_3_NOVOL_MODEL,
)


def test_mean_consumption_growth_is_h_times_mu():
    m = model_moments(TABLE_2_LRR, h=TABLE_2_LRR_H)
    assert m["mean_dc"] == pytest.approx(TABLE_2_LRR_H * TABLE_2_LRR.mu_c)


def test_h_one_consumption_variance_is_monthly():
    p = TABLE_2_LRR
    m = model_moments(p, h=1)
    var_x = (p.phi_e * p.sigma) ** 2 / (1.0 - p.rho**2)
    assert m["vol_dc"] ** 2 == pytest.approx(var_x + p.sigma**2, rel=1e-10)


def test_table3_means_at_table2_params():
    m = model_moments(TABLE_2_LRR, h=TABLE_2_LRR_H)
    assert m["mean_rf"] == pytest.approx(TABLE_3_LRR_MODEL["mean_rf"], abs=1e-3)
    assert m["mean_zd"] == pytest.approx(TABLE_3_LRR_MODEL["mean_zd"], abs=1e-3)
    assert m["mean_excess"] == pytest.approx(TABLE_3_LRR_MODEL["mean_excess"], abs=1e-3)


def test_table3_second_moments_at_table2_params():
    m = model_moments(TABLE_2_LRR, h=TABLE_2_LRR_H)
    tight = {
        "vol_dc": 2e-3,
        "ac1_dc": 2e-3,
        "ac2_dc": 2e-3,
        "vol_dd": 2e-3,
        "ac1_dd": 2e-3,
        "corr_dc_dd": 2e-3,
        "vol_zd": 1e-2,
        "ac1_zd": 1e-2,
        "vol_rd": 2e-3,
    }
    for key, tol in tight.items():
        assert m[key] == pytest.approx(TABLE_3_LRR_MODEL[key], abs=tol), key


def test_table3_predictability_matches_the_paper():
    m = model_moments(TABLE_2_LRR, h=TABLE_2_LRR_H)
    # corr(r_d, z_{d,-1}) is the lagged return predictability: a high
    # price-dividend ratio forecasts a low return, so it is negative in
    # both the sample and the LRR model (Table 3).
    assert m["corr_rd_zd"] == pytest.approx(TABLE_3_LRR_MODEL["corr_rd_zd"], abs=0.02)
    # corr(Δc, z_{d,-1}) is positive: a high P/D forecasts high
    # consumption growth through the persistent expected-growth channel.
    # The constant-σ log-linear covariance understates the printed 0.240
    # because the e-shock overlap carries stochastic-volatility fourth
    # moments the closed form does not integrate.
    assert m["corr_dc_zd"] == pytest.approx(TABLE_3_LRR_MODEL["corr_dc_zd"], abs=0.08)
    assert m["corr_dc_zd"] > 0.15


def test_table3_novol_model_column_matches_the_paper():
    m = model_moments(TABLE_2_NOVOL, h=TABLE_2_NOVOL_H)
    tight = {
        "vol_dc": 3e-3,
        "ac1_dc": 3e-3,
        "ac2_dc": 3e-3,
        "vol_dd": 3e-3,
        "ac1_dd": 3e-3,
        "corr_dc_dd": 3e-3,
        "mean_zd": 3e-2,
        "vol_zd": 4e-2,
        "ac1_zd": 2e-2,
        "mean_excess": 3e-3,
        "vol_rd": 3e-3,
        "mean_rf": 3e-3,
    }
    for key, tol in tight.items():
        assert m[key] == pytest.approx(TABLE_3_NOVOL_MODEL[key], abs=tol), key
    # Without stochastic volatility the return-predictability correlation
    # is positive (the volatility channel that made it negative is off).
    assert m["corr_rd_zd"] == pytest.approx(TABLE_3_NOVOL_MODEL["corr_rd_zd"], abs=0.02)
    assert m["corr_dc_zd"] == pytest.approx(TABLE_3_NOVOL_MODEL["corr_dc_zd"], abs=0.06)
