"""Shared model/results protocol: a second family can implement these ABCs."""
from __future__ import annotations

import pytest

import pandas as pd

from geap.base import (
    AssetPricingModel,
    AssetPricingResults,
    Comparison,
    Summary,
)


class _TinyModel(AssetPricingModel):
    def __init__(self, claims=("a", "b")):
        self._claims = tuple(claims)

    @property
    def claims(self):
        return self._claims

    def solve(self, method: str = "grid", **kwargs):
        return _TinyResults(self)

    def replace(self, **kwargs):
        claims = kwargs.get("claims", self._claims)
        return _TinyModel(claims=claims)


class _TinyResults(AssetPricingResults):
    method = "tiny"
    _premium_field = ("expected_returns", "expected return")

    def __init__(self, model):
        super().__init__(model)
        self.expected_returns = pd.Series({"a": 8.0, "b": 3.0})

    def summary(self) -> Summary:
        return Summary(["tiny"])

    def to_frame(self):
        return self.expected_returns.to_frame("expected_return")


def test_cannot_instantiate_model_abc():
    with pytest.raises(TypeError):
        AssetPricingModel()


def test_cannot_instantiate_results_abc():
    with pytest.raises(TypeError):
        AssetPricingResults()


def test_dummy_model_solves_to_results():
    model = _TinyModel()
    res = model.solve()
    assert isinstance(res, AssetPricingResults)
    assert res.claims == ("a", "b")
    assert res.method == "tiny"
    assert str(res.summary()) == "tiny"


def test_simulate_defaults_to_not_implemented():
    model = _TinyModel()
    with pytest.raises(NotImplementedError, match="simulate"):
        model.simulate()


def test_replace_returns_a_new_model():
    model = _TinyModel()
    other = model.replace(claims=("x",))
    assert other is not model
    assert other.claims == ("x",)
    assert model.claims == ("a", "b")


def test_comparison_does_not_require_lrr_attributes():
    """A family without P/D, volatility, or CAPM betas can still compare."""
    res = _TinyModel().solve()
    cmp = res.compare("a", "b")
    assert isinstance(cmp, Comparison)
    assert cmp.premium == pytest.approx(5.0)
    assert cmp.long == "a"
    assert cmp.short == "b"
    assert pd.isna(cmp.log_pd_spread)
    assert pd.isna(cmp.volatility_spread)
    assert pd.isna(cmp.beta_ratio)
    frame = cmp.to_frame()
    assert float(frame["premium"].iloc[0]) == pytest.approx(5.0)


def test_comparison_summary_survives_missing_optional_fields():
    text = _TinyModel().solve().compare("a", "b").summary().as_text()
    assert "5.00" in text
    assert "a" in text and "b" in text


def test_long_run_risks_model_is_an_asset_pricing_model():
    import geap

    model = geap.LongRunRisksModel()
    assert isinstance(model, AssetPricingModel)
    res = model.solve(method="analytical")
    assert isinstance(res, AssetPricingResults)
    assert res.claims == tuple(model.claims)
