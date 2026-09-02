"""External habit: Campbell and Cochrane (1999)."""
from __future__ import annotations

import numpy as np
import pytest

import geap
from geap.base import AssetPricingModel, AssetPricingResults


def test_campbell_cochrane_model_is_on_the_root():
    assert hasattr(geap, "CampbellCochraneModel")
    assert "CampbellCochraneModel" in geap.__all__


def test_campbell_cochrane_model_is_an_asset_pricing_model():
    model = geap.CampbellCochraneModel()
    assert isinstance(model, AssetPricingModel)
    res = model.solve()
    assert isinstance(res, AssetPricingResults)


def test_default_claims_are_equity_and_bill():
    assert geap.CampbellCochraneModel().claims == ("equity", "bill")


def test_steady_state_surplus_matches_the_paper():
    """Steady-state surplus Sbar is about 0.057 in Campbell and Cochrane (1999)."""
    model = geap.CampbellCochraneModel()
    assert model.sbar == pytest.approx(np.log(model.Sbar))
    assert model.Sbar == pytest.approx(0.057, abs=0.005)


def test_sensitivity_at_steady_state():
    model = geap.CampbellCochraneModel()
    lam = model.sensitivity(model.sbar)
    assert lam == pytest.approx(1.0 / model.Sbar - 1.0, rel=1e-10)


def test_gamma_is_two():
    assert geap.CampbellCochraneModel().gamma == pytest.approx(2.0)


def test_risk_free_rate_stays_near_the_target():
    """b = 0 makes the bill nearly constant at 0.94 percent a year."""
    rf = geap.CampbellCochraneModel().solve().expected_returns["bill"]
    assert 0.0 < rf < 3.0


def test_habit_produces_a_sizeable_equity_premium_at_gamma_2():
    """The point of habit: γ = 2 prices a postwar-sized premium, unlike power utility."""
    habit = geap.CampbellCochraneModel().solve().compare("equity", "bill").premium
    power = geap.PowerUtilityModel(gamma=2).solve().compare("equity", "bill").premium
    assert habit > 3.0
    assert habit > power + 2.0


def test_replace_does_not_mutate():
    model = geap.CampbellCochraneModel()
    other = model.replace(gamma=5)
    assert model.gamma == 2.0
    assert other.gamma == 5.0
    assert other is not model


def test_simulate_is_reproducible():
    model = geap.CampbellCochraneModel()
    a = model.simulate(n_samples=20, years=40, seed=3)
    b = model.simulate(n_samples=20, years=40, seed=3)
    assert a.compare("equity", "bill").premium == pytest.approx(
        b.compare("equity", "bill").premium
    )


def test_summary_and_to_frame():
    res = geap.CampbellCochraneModel().solve()
    text = res.summary().as_text()
    assert "equity" in text
    assert "bill" in text
    frame = res.to_frame()
    assert "expected_return" in frame.columns
