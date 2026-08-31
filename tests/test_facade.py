"""The statsmodels-style surface: model, solve, summary, simulate.

These tests pin the contract the documentation teaches, and the
continuity band that guards against the facade quietly changing a
default over the reused engines.
"""
import inspect
import re

import numpy as np
import pytest

import lrrcs as lrr


@pytest.fixture(scope="module")
def model():
    return lrr.LongRunRisksModel()


@pytest.fixture(scope="module")
def grid(model):
    return model.solve(n_x=15, n_s=4)


# -- specification ------------------------------------------------------
def test_default_model_is_the_table_ii_calibration(model):
    assert model.params == lrr.ModelParams()


def test_keyword_overrides_leave_the_rest_alone():
    model = lrr.LongRunRisksModel(gamma=7.5, psi=0.5)
    assert model.params.prefs.gamma == 7.5
    assert model.params.prefs.psi == 0.5
    assert model.params.prefs.delta == 0.999
    assert model.params.claims["value"].phi == 6.2


def test_partial_claim_override_merges_onto_the_calibration():
    """The counterfactual idiom: change one number, keep the rest."""
    model = lrr.LongRunRisksModel(claims={"value": {"phi": 2.6}})
    value = model.params.claims["value"]
    assert value.phi == 2.6
    assert value.mu == 0.0019 and value.phi_sigma == 7.4 and value.alpha == 0.15
    assert model.params.claims["growth"].phi == 2.6


def test_the_model_never_mutates_the_params_it_was_given():
    params = lrr.ModelParams()
    lrr.LongRunRisksModel(params, gamma=2.0, claims={"value": {"phi": 1.0}})
    assert params.prefs.gamma == 10.0
    assert params.claims["value"].phi == 6.2


def test_new_claim_names_replace_the_cross_section():
    model = lrr.LongRunRisksModel(
        claims={
            "high": dict(mu=0.0019, phi=6.2, phi_sigma=7.4, alpha=0.15),
            "low": dict(mu=0.0009, phi=2.6, phi_sigma=8.4, alpha=0.27),
            "market": dict(mu=0.0012, phi=2.8, phi_sigma=7.5, alpha=0.55),
        },
    )
    assert set(model.params.claims) == {"high", "low", "market"}


def test_partial_spec_for_an_unknown_claim_is_rejected():
    with pytest.raises(TypeError, match="needs all of"):
        lrr.LongRunRisksModel(claims={"brand_new": {"phi": 3.0}})


def test_replace_builds_a_new_model():
    base = lrr.LongRunRisksModel(gamma=10.0)
    other = base.replace(gamma=5.0)
    assert other.params.prefs.gamma == 5.0
    assert base.params.prefs.gamma == 10.0


def test_residual_corr_accepts_pairs_of_names():
    model = lrr.LongRunRisksModel(
        claims={
            "high": dict(mu=0.0019, phi=6.2, phi_sigma=7.4, alpha=0.15),
            "low": dict(mu=0.0009, phi=2.6, phi_sigma=8.4, alpha=0.27),
            "market": dict(mu=0.0012, phi=2.8, phi_sigma=7.5, alpha=0.55),
        },
        residual_corr={("high", "low"): 0.2},
    )
    from lrrcs.implications import residual_correlation

    assert residual_correlation(model.params, "high", "low") == 0.2
    assert residual_correlation(model.params, "high", "market") == 0.0


# -- signatures the documentation relies on ------------------------------
def test_solve_and_simulate_defaults():
    solve = inspect.signature(lrr.LongRunRisksModel.solve).parameters
    assert solve["method"].default == "grid"
    assert solve["n_x"].default == 30
    assert solve["n_s"].default == 4

    sim = inspect.signature(lrr.LongRunRisksModel.simulate).parameters
    assert sim["n_samples"].default == 1000
    assert sim["years"].default == 74
    assert sim["seed"].default == 0


def test_cross_method_options_are_rejected():
    model = lrr.LongRunRisksModel()
    with pytest.raises(ValueError, match="analytical"):
        model.solve(method="grid", pd_anchor=3.0)
    with pytest.raises(ValueError, match="grid"):
        model.solve(method="analytical", n_x=40)
    with pytest.raises(ValueError, match="method must be"):
        model.solve(method="montecarlo")


# -- results contract ----------------------------------------------------
def test_grid_results_expose_moments_by_claim(grid):
    assert list(grid.expected_returns.index) == ["growth", "value", "market"]
    for attr in ("expected_returns", "volatility", "sharpe_ratios",
                 "mean_log_pd", "price_dividend"):
        series = getattr(grid, attr)
        assert set(series.index) == {"growth", "value", "market"}, attr
        assert series.notna().all(), attr
    assert isinstance(grid.risk_free, float)
    betas = grid.capm_betas("market")
    assert set(betas.index) == {"growth", "value", "market"}
    assert betas.notna().all()
    cmp = grid.compare("value", "growth", market="market")
    assert cmp.premium == pytest.approx(
        grid.expected_returns["value"] - grid.expected_returns["growth"]
    )
    assert cmp.log_pd_spread == pytest.approx(
        grid.mean_log_pd["value"] - grid.mean_log_pd["growth"]
    )


def test_grid_results_expose_the_solved_grid(grid):
    assert grid.z_c.shape == (grid.n_x * grid.n_s,)
    assert set(grid.z) == {"growth", "value", "market"}
    assert grid.stationary.sum() == pytest.approx(1.0)
    assert grid.x_nodes.shape == (grid.n_x,)
    assert grid.s2_nodes.shape == (grid.n_s,)
    states = grid.states()
    assert len(states) == grid.n_x * grid.n_s
    assert "z_value" in states.columns


def test_analytical_results_are_in_percent(model):
    res = model.solve(method="analytical")
    # The paper's long-run piece is well under a percent a year.
    assert 0.0 < res.long_run_premium["value"] < 5.0
    assert res.compare("value", "growth").premium == pytest.approx(
        res.long_run_premium["value"] - res.long_run_premium["growth"]
    )
    assert res.Lambda_eta == res.risk_prices["eta"]


def test_to_frame_has_one_row_per_claim(grid):
    frame = grid.to_frame()
    assert len(frame) == 3
    assert set(frame["claim"]) == {"growth", "value", "market"}


def test_pd_anchor_overrides_the_linearization_point(model):
    res = model.solve(method="analytical", pd_anchor=3.30)
    assert set(res.mean_log_pd) == {3.30}


# -- summaries -----------------------------------------------------------
def _numbers(text):
    return [float(t) for t in re.findall(r"-?\d+\.\d+", text)]


def test_grid_summary_reports_the_attributes(grid):
    text = grid.summary().as_text()
    for name in grid.claims:
        assert name in text
    numbers = _numbers(text)
    # Every headline number in the table is the attribute, formatted.
    assert round(grid.risk_free, 2) in numbers
    for name in grid.claims:
        assert round(grid.expected_returns[name], 2) in numbers
        assert round(grid.volatility[name], 2) in numbers


def test_summary_prints_and_stringifies(grid):
    summary = grid.summary()
    assert str(summary) == summary.as_text()
    assert repr(summary) == summary.as_text()
    assert "<pre>" in summary._repr_html_()


def test_paper_column_only_for_the_paper_calibration(model):
    paper = model.simulate(n_samples=5, years=20, seed=0).summary().as_text()
    assert "Paper" in paper
    tweaked = (
        lrr.LongRunRisksModel(gamma=7.5)
        .simulate(n_samples=5, years=20, seed=0)
        .summary()
        .as_text()
    )
    assert "Paper" not in tweaked


# -- simulation ----------------------------------------------------------
def test_simulation_is_deterministic_in_the_seed(model):
    first = model.simulate(n_samples=5, years=20, seed=3).summary().as_text()
    second = model.simulate(n_samples=5, years=20, seed=3).summary().as_text()
    assert first == second


def test_a_model_without_a_market_can_still_simulate():
    """Pre-0.7.0 this raised: simulation demanded a claim named market."""
    model = lrr.LongRunRisksModel(
        claims={"mine": lrr.ClaimParams.from_loading(2.6)}
    )
    sim = model.simulate(n_samples=5, years=20, seed=0)
    assert np.isfinite(sim.expected_returns["mine"])
    # A lone claim is its own reference, so its beta is one.
    assert sim.capm_betas("mine")["mine"] == pytest.approx(1.0)


def test_value_premium_matches_the_pre_facade_band():
    """Continuity guard: every earlier release put this at 5.3791042785."""
    sim = lrr.LongRunRisksModel().simulate(n_samples=300, years=74, seed=0)
    cmp = sim.compare("value", "growth", market="market")
    assert 4.5 < cmp.premium < 6.5
    assert cmp.premium == pytest.approx(5.3791042785, abs=1e-9)


def test_beta_ratio_is_the_mean_of_per_sample_ratios():
    """Not the ratio of the mean betas: the two differ by about 0.008."""
    sim = lrr.LongRunRisksModel().simulate(n_samples=300, years=74, seed=0)
    cmp = sim.compare("value", "growth", market="market")
    assert cmp.beta_ratio == pytest.approx(0.8118025654055882, abs=1e-9)
    betas = sim.capm_betas("market")
    naive = betas["value"] / betas["growth"]
    assert abs(cmp.beta_ratio - naive) > 1e-3


def test_simulate_cashflows_has_one_row_per_series(model):
    frame = model.simulate_cashflows(n_sims=3, years=20, seed=1).set_index("series")
    assert set(frame.index) == {"consumption", "growth", "value", "market"}
    assert frame.loc["consumption", "corr_with_consumption"] == 1.0


# -- calibration ---------------------------------------------------------
def test_calibration_never_takes_returns():
    for fn in (lrr.calibrate_claim, lrr.calibrate_claims):
        assert "returns" not in inspect.signature(fn).parameters, fn.__name__


def test_calibrated_claims_build_a_model():
    rng = np.random.default_rng(4)
    n = 60
    dc = rng.normal(0.02, 0.03, size=n)
    dd_long = 0.03 + 0.8 * dc + rng.normal(0, 0.04, size=n)
    dd_short = 0.01 + 0.2 * dc + rng.normal(0, 0.04, size=n)
    dd_market = 0.02 + 0.5 * dc + rng.normal(0, 0.03, size=n)

    model = lrr.LongRunRisksModel(claims=lrr.calibrate_claims(
        dc, {"long": dd_long, "short": dd_short, "market": dd_market}
    ))
    assert set(model.params.claims) == {"long", "short", "market"}
    # Preferences still come from the paper unless overridden.
    assert model.params.prefs.gamma == 10.0


def _growth_series(n=74, seed=42):
    rng = np.random.default_rng(seed)
    x = np.zeros(n)
    for t in range(1, n):
        x[t] = 0.6 * x[t - 1] + 0.01 * rng.standard_normal()
    dc = 0.02 + x + 0.015 * rng.standard_normal(n)
    return (
        dc,
        0.025 + 3.5 * x + 0.12 * rng.standard_normal(n),
        0.015 + 0.4 * x + 0.18 * rng.standard_normal(n),
        0.020 + 1.5 * x + 0.10 * rng.standard_normal(n),
    )


def test_custom_claim_names_need_no_role_argument():
    """Naming your own cross-section is now just naming the dict keys."""
    dc, high, low, market = _growth_series()
    model = lrr.LongRunRisksModel(claims=lrr.calibrate_claims(
        dc, {"quality": high, "junk": low, "market": market}
    ))
    assert set(model.params.claims) == {"quality", "junk", "market"}
    res = model.solve(method="analytical")
    assert np.isfinite(res.compare("quality", "junk").premium)


def test_calibrating_one_claim_equals_calibrating_the_set():
    """The seam that makes calibration composable: no cross-claim coupling."""
    dc, high, low, market = _growth_series()
    series = {"quality": high, "junk": low, "market": market}
    batch = lrr.calibrate_claims(dc, series)
    for name, dd in series.items():
        assert lrr.calibrate_claim(dc, dd) == batch[name], name
