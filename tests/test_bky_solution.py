"""Log-linear BKY (2016) solution: A, F, Γ, λ, IES=1, z-bar fixed point."""
from __future__ import annotations

import numpy as np
import pytest

from geap.lrr.estimation import BKYParams, solve_loglinear


def table2_lrr() -> BKYParams:
    """JME Table 2, LRR column, at the decision frequency."""
    return BKYParams(
        gamma=9.67,
        psi=2.18,
        delta=0.9990,
        mu_c=0.0016,
        rho=0.9762,
        phi_e=0.0318,
        sigma=0.0070,
        nu=0.9984,
        sigma_w=2.12e-6,
        mu_d=0.0027,
        phi_d=4.51,
        phi_d_sigma=4.65,
        rho_d=0.51,
    )


def test_consumption_a1_matches_closed_form():
    sol = solve_loglinear(table2_lrr())
    expected = (1.0 - 1.0 / 2.18) / (1.0 - sol.kappa_c1 * 0.9762)
    assert sol.A_c1 == pytest.approx(expected, rel=1e-12)


def test_zbar_is_a_fixed_point():
    sol = solve_loglinear(table2_lrr())
    implied = sol.A_c0 + sol.A_c2 * (0.0070 ** 2)
    assert sol.mean_zc == pytest.approx(implied, abs=1e-10)


def test_kappa_c1_is_campbell_shiller():
    sol = solve_loglinear(table2_lrr())
    z = sol.mean_zc
    assert sol.kappa_c1 == pytest.approx(np.exp(z) / (1.0 + np.exp(z)), rel=1e-12)


def test_ies_one_sets_kappa_to_delta():
    p = table2_lrr()
    p.psi = 1.0
    sol = solve_loglinear(p)
    assert sol.kappa_c1 == pytest.approx(p.delta, rel=1e-10)
    assert sol.Gamma[1] == pytest.approx(-1.0, abs=1e-12)


def test_risk_free_mean_is_finite_and_positive_at_table2():
    sol = solve_loglinear(table2_lrr())
    rf = sol.F[0] + sol.F[2] * (0.0070 ** 2)
    assert np.isfinite(rf)
    # Monthly real rate around 1%/year / 11 ≈ 0.001
    assert -0.01 < rf < 0.02


def test_higher_risk_aversion_lowers_the_risk_free_rate():
    lo = solve_loglinear(table2_lrr())
    hi_params = table2_lrr()
    hi_params.gamma = 15.0
    hi = solve_loglinear(hi_params)
    rf_lo = lo.F[0] + lo.F[2] * (0.0070 ** 2)
    rf_hi = hi.F[0] + hi.F[2] * (0.0070 ** 2)
    assert rf_hi < rf_lo


def test_dividend_a1_is_leverage_over_ies():
    sol = solve_loglinear(table2_lrr())
    expected = (4.51 - 1.0 / 2.18) / (1.0 - sol.kappa_d1 * 0.9762)
    assert sol.A_d1 == pytest.approx(expected, rel=1e-12)


def test_lambda_eta_equals_gamma():
    sol = solve_loglinear(table2_lrr())
    assert sol.Lambda[0] == pytest.approx(9.67)
