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
    assert model.legs == ("value", "growth", "market")


def test_keyword_overrides_leave_the_rest_alone():
    model = lrr.LongRunRisksModel(gamma=7.5, psi=0.5)
    assert model.params.prefs.gamma == 7.5
    assert model.params.prefs.psi == 0.5
    assert model.params.prefs.delta == 0.999
    assert model.params.dividends["value"].phi == 6.2


def test_partial_claim_override_merges_onto_the_calibration():
    """The counterfactual idiom: change one number, keep the rest."""
    model = lrr.LongRunRisksModel(claims={"value": {"phi": 2.6}})
    value = model.params.dividends["value"]
    assert value.phi == 2.6
    assert value.mu == 0.0019 and value.phi_sigma == 7.4 and value.alpha == 0.15
    assert model.params.dividends["growth"].phi == 2.6


def test_the_model_never_mutates_the_params_it_was_given():
    params = lrr.ModelParams()
    lrr.LongRunRisksModel(params, gamma=2.0, claims={"value": {"phi": 1.0}})
    assert params.prefs.gamma == 10.0
    assert params.dividends["value"].phi == 6.2


def test_new_claim_names_replace_the_cross_section():
    model = lrr.LongRunRisksModel(
        claims={
            "high": dict(mu=0.0019, phi=6.2, phi_sigma=7.4, alpha=0.15),
            "low": dict(mu=0.0009, phi=2.6, phi_sigma=8.4, alpha=0.27),
            "market": dict(mu=0.0012, phi=2.8, phi_sigma=7.5, alpha=0.55),
        },
        long="high",
        short="low",
    )
    assert set(model.params.dividends) == {"high", "low", "market"}
    assert model.legs == ("high", "low", "market")


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
        long="high",
        short="low",
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
                 "capm_betas", "mean_log_pd", "price_dividend"):
        series = getattr(grid, attr)
        assert set(series.index) == {"growth", "value", "market"}, attr
        assert series.notna().all(), attr
    assert isinstance(grid.risk_free, float)
    assert grid.value_premium == grid.long_short_premium
    assert grid.value_premium == pytest.approx(
        grid.expected_returns["value"] - grid.expected_returns["growth"]
    )
    assert grid.log_pd_spread == pytest.approx(
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
    assert res.value_premium == pytest.approx(
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
    assert round(grid.value_premium, 2) in numbers
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


def test_simulate_needs_a_market_claim():
    model = lrr.LongRunRisksModel.from_loading(2.6)
    with pytest.raises(ValueError, match="market"):
        model.simulate(n_samples=2, years=10)


def test_value_premium_matches_the_pre_facade_band():
    """Continuity guard: the 0.5.0 pipeline put this at 5.38."""
    sim = lrr.LongRunRisksModel().simulate(n_samples=300, years=74, seed=0)
    assert 4.5 < sim.value_premium < 6.5
    assert sim.value_premium == pytest.approx(5.38, abs=0.01)


def test_simulate_cashflows_has_one_row_per_series(model):
    frame = model.simulate_cashflows(n_sims=3, years=20, seed=1).set_index("series")
    assert set(frame.index) == {"consumption", "growth", "value", "market"}
    assert frame.loc["consumption", "corr_with_consumption"] == 1.0


# -- calibration ---------------------------------------------------------
def test_from_cashflows_never_takes_returns():
    assert "returns" not in inspect.signature(
        lrr.LongRunRisksModel.from_cashflows
    ).parameters


def test_from_cashflows_builds_a_model_from_growth_series():
    rng = np.random.default_rng(4)
    n = 60
    dc = rng.normal(0.02, 0.03, size=n)
    dd_long = 0.03 + 0.8 * dc + rng.normal(0, 0.04, size=n)
    dd_short = 0.01 + 0.2 * dc + rng.normal(0, 0.04, size=n)
    dd_market = 0.02 + 0.5 * dc + rng.normal(0, 0.03, size=n)

    model = lrr.LongRunRisksModel.from_cashflows(
        dc, long=dd_long, short=dd_short, market=dd_market
    )
    assert set(model.params.dividends) == {"long", "short", "market"}
    assert model.legs == ("long", "short", "market")
    # Preferences still come from the paper unless overridden.
    assert model.params.prefs.gamma == 10.0
