"""Tables 4–6 and 8: restricted h and the No-Vol nested model."""
from __future__ import annotations

import numpy as np
import pytest

from geap.lrr.estimation.aggregation import long_run_variance_share, model_moments
from geap.lrr.estimation.data import load_annual
from geap.lrr.estimation.estimate import estimate_bky
from geap.lrr.estimation.goldens import (
    COLD_START,
    TABLE_2_LRR,
    TABLE_2_LRR_H,
    TABLE_2_NOVOL,
    TABLE_2_NOVOL_H,
    TABLE_4_ANNUAL,
    TABLE_5_ANNUAL_MODEL,
    TABLE_6,
    TABLE_8_H,
    TABLE_8_NO_TA,
    TABLE_8_TA,
)


def test_table5_model_moments_at_the_annual_estimates():
    m = model_moments(TABLE_4_ANNUAL, h=1)
    for key, paper in TABLE_5_ANNUAL_MODEL.items():
        assert m[key] == pytest.approx(paper, abs=2e-3), key


def test_annual_spec_understates_price_volatility_and_the_premium():
    lrr = model_moments(TABLE_2_LRR, TABLE_2_LRR_H)
    ann = model_moments(TABLE_4_ANNUAL, h=1)
    assert ann["vol_zd"] < 0.5 * lrr["vol_zd"]
    assert ann["mean_excess"] < lrr["mean_excess"]
    assert ann["ac1_dc"] < lrr["ac1_dc"]


def test_long_run_share_is_24_percent_with_aggregation_10_without():
    lrr = long_run_variance_share(TABLE_2_LRR, TABLE_2_LRR_H)
    ann = long_run_variance_share(TABLE_4_ANNUAL, 1)
    assert lrr == pytest.approx(0.24, abs=0.02)
    assert ann == pytest.approx(0.10, abs=0.02)
    assert lrr > 1.5 * ann


def test_table6_monthly_is_close_to_the_unrestricted_model():
    monthly = model_moments(TABLE_6[12], h=12)
    lrr = model_moments(TABLE_2_LRR, TABLE_2_LRR_H)
    assert monthly["mean_rf"] == pytest.approx(lrr["mean_rf"], abs=0.005)
    assert monthly["mean_excess"] == pytest.approx(lrr["mean_excess"], abs=0.02)


def test_no_vol_and_quarterly_specs_solve():
    nv = model_moments(TABLE_2_NOVOL, TABLE_2_NOVOL_H)
    q = model_moments(TABLE_8_TA, TABLE_8_H)
    q0 = model_moments(TABLE_8_NO_TA, h=1)
    assert nv["mean_rf"] == pytest.approx(0.010, abs=0.005)
    assert q["mean_rf"] > 0
    assert q0["mean_excess"] > 0
    # Ignoring quarterly time aggregation raises risk aversion in the paper.
    assert TABLE_8_NO_TA.gamma > TABLE_8_TA.gamma


def test_no_vol_restriction_zeros_nu_and_sigma_w():
    data = load_annual()
    assert abs(COLD_START.nu) > 0.5
    assert COLD_START.sigma_w > 0.0
    fit = estimate_bky(
        data, start=COLD_START, stochastic_vol=False, method="staged", h=9,
    )
    assert fit.h == 9
    assert fit.stochastic_vol is False
    assert fit.params.nu == pytest.approx(0.0, abs=1e-16)
    assert fit.params.sigma_w == pytest.approx(0.0, abs=1e-16)
    assert 5.0 <= fit.params.gamma <= 15.0


def test_staged_restricted_h_runs_at_table6_frequencies():
    data = load_annual()
    gammas = {}
    for h in (26, 12, 4, 1):
        fit = estimate_bky(data, start=COLD_START, h=h, method="staged")
        assert fit.h == h
        assert np.isfinite(fit.params.gamma), h
        gammas[h] = float(fit.params.gamma)
    assert 6.0 <= gammas[12] <= 12.0


@pytest.mark.slow
def test_no_vol_gmm_from_cold_start():
    data = load_annual()
    fit = estimate_bky(
        data,
        start=COLD_START,
        stochastic_vol=False,
        h_grid=(8, 9, 10, 11, 12),
    )
    assert fit.params.nu == pytest.approx(0.0, abs=1e-12)
    assert fit.params.sigma_w == pytest.approx(0.0, abs=1e-12)
    assert fit.h in {6, 7, 8, 9, 10, 11, 12}
    assert 5.0 <= fit.params.gamma <= 15.0
    assert fit.gmm.J_pvalue is not None
    # Paper p=0.00. QR-stabilized Lemma 4.2 on this vintage is
    # conservative; the restriction is nu = sigma_w = 0.


@pytest.mark.slow
def test_annual_h1_gmm_from_cold_start():
    data = load_annual()
    fit = estimate_bky(data, start=COLD_START, h=1)
    assert fit.h == 1
    assert fit.params.gamma > 11.0
    assert fit.gmm.J_pvalue is not None
    # Paper p=0.00. The annual spec still inflates gamma; the
    # QR-stabilized J-test on this vintage need not fall below 5%.


@pytest.mark.slow
def test_restricted_h_gmm_gamma_ranking():
    data = load_annual()
    gammas = {}
    for h in (26, 12, 4):
        fit = estimate_bky(data, start=COLD_START, h=h)
        assert fit.h == h
        gammas[h] = float(fit.params.gamma)
        if h == 12:
            assert 6.0 <= fit.params.gamma <= 12.0
    assert gammas[26] < gammas[12] < gammas[4]
