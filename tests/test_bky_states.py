"""Recover (x, σ²) from the affine maps for z_d and r_f."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from geap.lrr.estimation import states as states_mod
from geap.lrr.estimation.goldens import TABLE_2_LRR
from geap.lrr.estimation.solution import solve_loglinear
from geap.lrr.estimation.states import _annual_map, extract_states


def _simulate_monthly_states(n: int = 400, seed: int = 0):
    p = TABLE_2_LRR
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    s2 = np.full(n, p.sigma**2)
    for t in range(1, n):
        e = rng.normal()
        w = rng.normal()
        x[t] = p.rho * x[t - 1] + p.phi_e * np.sqrt(max(s2[t - 1], 1e-16)) * e
        s2[t] = p.sigma**2 * (1.0 - p.nu) + p.nu * s2[t - 1] + p.sigma_w * w
        s2[t] = max(s2[t], 1e-10)
    return x, s2


def test_extracted_states_recover_a_simulated_path():
    p = TABLE_2_LRR
    sol = solve_loglinear(p)
    x, s2 = _simulate_monthly_states()
    z = sol.A_d0 + sol.A_d1 * x + sol.A_d2 * s2
    rf = sol.F[0] + sol.F[1] * x + sol.F[2] * s2
    hat = extract_states(z, rf, sol)
    assert np.all(hat.sigma2 > 0)
    assert np.corrcoef(hat.x, x)[0, 1] > 0.95
    assert np.corrcoef(hat.sigma2, s2)[0, 1] > 0.95


def test_extracted_variance_is_positive_when_the_linear_solve_goes_negative():
    sol = solve_loglinear(TABLE_2_LRR)
    z = np.array([sol.mean_zd])
    # A very high risk-free observation pushes σ² the wrong way.
    rf = np.array([sol.F[0] + 0.05])
    hat = extract_states(z, rf, sol)
    assert hat.sigma2[0] > 0.0


def test_no_kalman_constants():
    src = Path(states_mod.__file__).read_text(encoding="utf-8")
    assert "1e-4" not in src
    assert "1e-8" not in src
    for line in src.splitlines():
        code = line.split("#", 1)[0]
        for sep in "=,()+-*/[]{}:":
            code = code.replace(sep, " ")
        tokens = code.split()
        assert "kx" not in tokens
        assert "ks" not in tokens


def test_grid_extraction_recovers_a_simulated_path():
    p = TABLE_2_LRR
    sol = solve_loglinear(p)
    x, s2 = _simulate_monthly_states()
    a0, a1, a2, f0, f1, f2 = _annual_map(sol, p, 1)
    z = a0 + a1 * x + a2 * s2
    rf = f0 + f1 * x + f2 * s2
    hat = extract_states(z, rf, sol, params=p, h=1, ar=True)
    assert np.all(hat.sigma2 > 0)
    assert np.corrcoef(hat.x, x)[0, 1] > 0.95
    assert np.corrcoef(hat.sigma2, s2)[0, 1] > 0.95


def test_h_one_annual_map_is_the_decision_frequency_map():
    p = TABLE_2_LRR
    sol = solve_loglinear(p)
    a0, a1, a2, f0, f1, f2 = _annual_map(sol, p, 1)
    assert a0 == pytest.approx(sol.A_d0)
    assert a1 == pytest.approx(sol.A_d1)
    assert a2 == pytest.approx(sol.A_d2)
    assert f0 == pytest.approx(float(sol.F[0]))
    assert f1 == pytest.approx(float(sol.F[1]))
    assert f2 == pytest.approx(float(sol.F[2]))


def test_annual_rf_map_is_the_same_date_eq23_scaling():
    """Extraction uses eq. 23 at the sampling date: r_f^a ≈ h F' Y_t."""
    p = TABLE_2_LRR
    sol = solve_loglinear(p)
    h = 11
    _a0, a1, a2, f0, f1, f2 = _annual_map(sol, p, h)
    assert a1 == pytest.approx(sol.A_d1)
    assert a2 == pytest.approx(sol.A_d2)
    assert f1 == pytest.approx(h * float(sol.F[1]))
    assert f2 == pytest.approx(h * float(sol.F[2]))
    mean = f0 + f2 * p.sigma**2
    assert mean == pytest.approx(
        h * (float(sol.F[0]) + float(sol.F[2]) * p.sigma**2)
    )


def test_ar_penalty_pulls_toward_prediction():
    p = TABLE_2_LRR
    sol = solve_loglinear(p)
    sol.A_d2 = 1e-6
    sol.F = np.array(sol.F, copy=True)
    sol.F[2] = 1e-6
    a0, a1, a2, f0, f1, f2 = _annual_map(sol, p, 1)
    s2_bar = p.sigma**2
    x0, s20 = 0.0, s2_bar
    x1, s21 = 0.0, 10.0 * s2_bar
    z = np.array([a0 + a1 * x0 + a2 * s20, a0 + a1 * x1 + a2 * s21])
    rf = np.array([f0 + f1 * x0 + f2 * s20, f0 + f1 * x1 + f2 * s21])
    cls = extract_states(z, rf, sol, params=p, h=1, ar=False)
    hat = extract_states(z, rf, sol, params=p, h=1, ar=True)
    s2_pred = s2_bar * (1.0 - p.nu) + p.nu * hat.sigma2[0]
    assert abs(hat.sigma2[1] - s2_pred) < abs(cls.sigma2[1] - s2_pred)
    assert hat.sigma2[1] > 0.0

