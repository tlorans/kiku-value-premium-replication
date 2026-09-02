"""Power-utility CCAPM: Mehra and Prescott (1985) two-state chain."""
from __future__ import annotations

import numpy as np
import pytest

import geap
from geap.base import AssetPricingModel, AssetPricingResults


def test_power_utility_model_is_on_the_root():
    assert hasattr(geap, "PowerUtilityModel")
    assert "PowerUtilityModel" in geap.__all__


def test_power_utility_model_is_an_asset_pricing_model():
    model = geap.PowerUtilityModel()
    assert isinstance(model, AssetPricingModel)
    res = model.solve()
    assert isinstance(res, AssetPricingResults)


def test_default_claims_are_equity_and_bill():
    model = geap.PowerUtilityModel()
    assert model.claims == ("equity", "bill")


def test_endowment_matches_mehra_prescott_moments():
    """μ = 0.018, σ = 0.036, ρ = −0.14 on the stationary chain."""
    model = geap.PowerUtilityModel()
    g = model.consumption_growth
    P = model.transition
    pi = model.stationary
    mean = float(pi @ (g - 1.0))
    centred = g - 1.0 - mean
    var = float(pi @ centred**2)
    # E[g_t g_{t+1}] path: π' (g-1) * P * (g-1)
    autocov = float((pi * centred) @ (P @ centred))
    rho = autocov / var
    assert mean == pytest.approx(0.018, abs=1e-12)
    assert np.sqrt(var) == pytest.approx(0.036, abs=1e-12)
    assert rho == pytest.approx(-0.14, abs=1e-12)


def test_default_preferences_are_at_the_edge_of_the_paper():
    model = geap.PowerUtilityModel()
    assert model.delta == pytest.approx(0.99)
    assert model.gamma == pytest.approx(10.0)


def test_solve_returns_percent_expected_returns():
    res = geap.PowerUtilityModel().solve()
    assert set(res.expected_returns.index) == {"equity", "bill"}
    # Gross returns near one become numbers like 1–20, not 0.01.
    assert 0.0 < res.expected_returns["bill"] < 30.0
    assert 0.0 < res.expected_returns["equity"] < 40.0


def test_equity_premium_is_an_order_of_magnitude_too_small():
    """The puzzle: γ = 10 still cannot produce the 6.2 point sample premium.

    Mehra and Prescott (1985) document 6.18 points on 1889–1978 data.
    At the edge of their plausible set the two-state economy produces
    a positive premium that is still less than half that figure, and
    it does so only by blowing up the bill (see the next test).
    """
    res = geap.PowerUtilityModel().solve()
    premium = res.compare("equity", "bill").premium
    sample = 6.18  # Mehra and Prescott, 1889–1978
    assert premium > 0.0
    assert premium < 0.5 * sample


def test_risk_free_rate_is_too_high_at_gamma_10():
    """The companion puzzle: high γ to chase the premium blows up the bill."""
    rf = geap.PowerUtilityModel().solve().expected_returns["bill"]
    assert rf > 5.0


def test_premium_rises_with_risk_aversion():
    low = geap.PowerUtilityModel(gamma=2).solve().compare("equity", "bill").premium
    high = geap.PowerUtilityModel(gamma=10).solve().compare("equity", "bill").premium
    assert high > low


def test_replace_does_not_mutate():
    model = geap.PowerUtilityModel()
    other = model.replace(gamma=2)
    assert model.gamma == 10.0
    assert other.gamma == 2.0
    assert other is not model


def test_levered_claim_has_a_higher_premium_than_equity():
    model = geap.PowerUtilityModel(claims={"high": {"phi": 3.0}})
    assert "high" in model.claims
    assert "equity" in model.claims
    res = model.solve()
    eq = res.compare("equity", "bill").premium
    hi = res.compare("high", "bill").premium
    assert hi > eq


def test_simulate_is_reproducible_and_near_the_population():
    model = geap.PowerUtilityModel()
    pop = model.solve().compare("equity", "bill").premium
    a = model.simulate(n_samples=200, years=200, seed=1)
    b = model.simulate(n_samples=200, years=200, seed=1)
    assert a.compare("equity", "bill").premium == pytest.approx(
        b.compare("equity", "bill").premium
    )
    sim = a.compare("equity", "bill").premium
    assert sim == pytest.approx(pop, abs=1.0)


def test_summary_and_to_frame():
    res = geap.PowerUtilityModel().solve()
    text = res.summary().as_text()
    assert "equity" in text
    assert "bill" in text
    frame = res.to_frame()
    assert "expected_return" in frame.columns or "expected_returns" in frame.columns
