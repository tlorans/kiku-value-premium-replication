"""Hansen GMM: linear factor, generic estimate, power-utility SDF."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

import geap


def test_gmm_is_on_the_root_as_a_module():
    assert hasattr(geap, "gmm")
    assert "gmm" in geap.__all__
    assert not hasattr(geap, "estimate")
    assert hasattr(geap.gmm, "estimate")
    assert hasattr(geap.gmm, "linear_factor")
    assert hasattr(geap.gmm, "GMMResults")


def test_just_identified_lambda_matches_the_mean():
    fit = geap.gmm.linear_factor(np.array([0.08]), np.array([1.0]))
    assert fit.theta == pytest.approx(0.08)
    assert fit.g == pytest.approx(0.0, abs=1e-12)
    assert fit.n_params == 1
    assert fit.n_moments == 1
    assert fit.names == ("lambda",)


def test_overidentified_identity_w_is_ols_of_means_on_betas():
    mean_ret = np.array([0.08, 0.15])
    beta = np.array([1.0, 1.5])
    fit = geap.gmm.linear_factor(mean_ret, beta, W="identity")
    ols = float(np.linalg.lstsq(beta[:, None], mean_ret, rcond=None)[0][0])
    assert fit.theta[0] == pytest.approx(ols)
    assert 0.08 < fit.theta[0] < 0.10
    assert np.all(np.abs(fit.g) > 1e-12)
    assert fit.objective == pytest.approx(float(fit.g @ fit.g))
    assert fit.J_pvalue is None


def test_perfect_fit_when_means_lie_on_the_line():
    fit = geap.gmm.linear_factor(np.array([0.08, 0.12]), np.array([1.0, 1.5]))
    assert fit.theta[0] == pytest.approx(0.08)
    assert fit.g == pytest.approx(0.0, abs=1e-12)


def test_linear_factor_closed_form_matches_two_factor_ols():
    mean_ret = np.array([0.08, 0.12, 0.20])
    beta = np.array([[1.0, 0.5], [1.2, 0.2], [0.8, 1.0]])
    fit = geap.gmm.linear_factor(mean_ret, beta, W="identity")
    ols = np.linalg.lstsq(beta, mean_ret, rcond=None)[0]
    assert fit.theta == pytest.approx(ols)
    assert fit.n_params == 2
    assert fit.names == ("lambda0", "lambda1")


def test_estimate_on_sample_moments_matches_linear_factor():
    mean_ret = np.array([0.08, 0.15])
    beta = np.array([1.0, 1.5])

    def moments(theta):
        return mean_ret - theta[0] * beta

    fit = geap.gmm.estimate(moments, 0.09, W="identity", names=("lambda",))
    closed = geap.gmm.linear_factor(mean_ret, beta, W="identity")
    assert fit.theta[0] == pytest.approx(closed.theta[0], abs=1e-8)
    assert fit.nobs is None
    assert fit.J_pvalue is None


def test_sample_moments_cannot_form_two_step_w():
    def moments(theta):
        return np.array([0.08, 0.15]) - theta[0] * np.array([1.0, 1.5])

    with pytest.raises(ValueError, match="observation"):
        geap.gmm.estimate(moments, 0.09, steps=2)


def test_more_parameters_than_moments_raises():
    def moments(theta):
        return np.array([theta[0] + theta[1]])

    with pytest.raises(ValueError, match="moments"):
        geap.gmm.estimate(moments, [0.1, 0.2])


def test_j_test_rejects_a_third_asset_off_the_line():
    rng = np.random.default_rng(0)
    t = 4000
    lam = 0.08
    beta = np.array([1.0, 1.5, 2.0])
    noise = rng.normal(0.0, 0.03, size=(t, 3))
    on_line = lam * beta + noise
    off_line = on_line.copy()
    off_line[:, 2] += 0.06

    ok = geap.gmm.linear_factor(on_line, beta, W="identity", steps=2)
    bad = geap.gmm.linear_factor(off_line, beta, W="identity", steps=2)
    assert ok.J_df == 2
    assert ok.J_pvalue > 0.05
    assert bad.J_pvalue < 0.01
    assert bad.J > ok.J


def test_optimal_w_moves_toward_the_precise_asset():
    rng = np.random.default_rng(1)
    t = 8000
    precise = 0.08 + 0.004 * rng.standard_normal(t)
    noisy = 0.15 + 0.25 * rng.standard_normal(t)
    returns = np.column_stack([precise, noisy])
    beta = np.array([1.0, 1.5])

    ident = geap.gmm.linear_factor(returns, beta, W="identity", steps=1)
    opt = geap.gmm.linear_factor(returns, beta, W="identity", steps=2)
    assert abs(opt.theta[0] - 0.08) < abs(ident.theta[0] - 0.08)
    assert opt.se is not None
    assert opt.se.shape == (1,)
    assert ident.J_pvalue is None
    assert opt.J_pvalue is not None


def test_invvar_w_is_diagonal_of_inverse_variances():
    rng = np.random.default_rng(2)
    t = 2000
    returns = np.column_stack(
        [
            0.08 + 0.01 * rng.standard_normal(t),
            0.10 + 0.05 * rng.standard_normal(t),
        ]
    )
    beta = np.array([1.0, 1.0])
    fit = geap.gmm.linear_factor(returns, beta, W="invvar", steps=1)
    g0 = returns - fit.theta[0] * beta
    expected = np.diag(1.0 / g0.var(axis=0, ddof=1))
    assert fit.W == pytest.approx(expected, rel=1e-10)
    assert fit.J_pvalue is None


def test_power_utility_sdf_recovers_known_parameters():
    rng = np.random.default_rng(3)
    t = 3000
    delta, gamma = 0.99, 4.0
    growth = np.exp(0.018 + 0.02 * rng.standard_normal(t))
    m = geap.gmm.power_utility_sdf(delta, gamma, growth)
    rf = 1.0 / float(np.mean(m))
    excess = np.column_stack(
        [
            0.4 * (1.0 / m - rf),
            1.1 * (1.0 / m - rf),
        ]
    )

    def moments(theta):
        sdf = geap.gmm.power_utility_sdf(theta[0], theta[1], growth)
        pricing = geap.gmm.sdf_moments(sdf, excess)
        level = sdf * rf - 1.0
        return np.column_stack([pricing, level])

    fit = geap.gmm.estimate(
        moments,
        [0.95, 2.5],
        W="identity",
        steps=2,
        bounds=((1e-6, 1.0), (0.1, 20.0)),
        names=("delta", "gamma"),
    )
    assert fit.theta[0] == pytest.approx(delta, abs=0.03)
    assert fit.theta[1] == pytest.approx(gamma, abs=0.4)
    assert fit.names == ("delta", "gamma")
    assert fit.J_df == 1
    assert fit.J_pvalue > 0.01


def test_sdf_moments_are_m_times_excess_returns():
    m = np.array([0.98, 1.01, 0.99])
    re = np.array([[0.1, 0.2], [0.0, -0.1], [0.05, 0.05]])
    g = geap.gmm.sdf_moments(m, re)
    assert g.shape == (3, 2)
    assert g == pytest.approx(m[:, None] * re)


def test_summary_and_to_frame():
    fit = geap.gmm.linear_factor(np.array([0.08, 0.15]), np.array([1.0, 1.5]))
    text = fit.summary().as_text()
    assert "lambda" in text
    assert "GMM" in text
    frame = fit.to_frame()
    assert "theta" in frame.columns or "estimate" in frame.columns


def test_calibration_does_not_import_gmm():
    root = Path(__file__).resolve().parents[1] / "src" / "geap" / "lrr" / "calibration"
    for path in root.glob("*.py"):
        src = path.read_text(encoding="utf-8")
        assert "geap.gmm" not in src
        assert "from geap import gmm" not in src


def test_cue_invvar_rebuilds_w_at_the_estimate():
    rng = np.random.default_rng(4)
    t = 2000
    returns = np.column_stack(
        [
            0.08 + 0.01 * rng.standard_normal(t),
            0.10 + 0.05 * rng.standard_normal(t),
        ]
    )
    beta = np.array([1.0, 1.0])
    fit = geap.gmm.linear_factor(returns, beta, W="cue_invvar", steps=1)
    g0 = returns - fit.theta[0] * beta
    expected = np.diag(1.0 / g0.var(axis=0, ddof=1))
    assert fit.W == pytest.approx(expected, rel=1e-8)
    assert fit.steps == 1


def test_lemma42_j_is_defined_for_identity_weights():
    rng = np.random.default_rng(5)
    t = 3000
    lam = 0.08
    beta = np.array([1.0, 1.5, 2.0])
    noise = rng.normal(0.0, 0.03, size=(t, 3))
    re = lam * beta + noise
    fit = geap.gmm.linear_factor(re, beta, W="identity", steps=1, j_test=True)
    assert fit.J is not None
    assert fit.J_pvalue is not None
    assert fit.J_df == 2
    assert fit.J_pvalue > 0.01


def test_block_bootstrap_se_is_finite_on_a_mean():
    rng = np.random.default_rng(6)
    x = rng.normal(0.08, 0.02, size=80)

    def estimate_on(idx):
        return np.array([float(np.mean(x[idx]))])

    se, draws = geap.gmm.block_bootstrap(
        estimate_on, nobs=len(x), block_length=8, n_boot=30, rng=rng
    )
    assert se.shape == (1,)
    assert np.isfinite(se[0])
    assert se[0] > 0
    assert draws.shape == (30, 1)


def test_power_utility_model_sdf_on_the_chain_and_on_a_series():
    model = geap.PowerUtilityModel()
    chain = model.sdf()
    assert chain.shape == (2,)
    assert chain == pytest.approx(
        model.delta * model.consumption_growth ** (-model.gamma)
    )
    growth = np.array([1.02, 0.99, 1.01])
    series = model.sdf(growth)
    assert series == pytest.approx(model.delta * growth ** (-model.gamma))
