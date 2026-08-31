"""Bring your own claim: ClaimParams.from_loading."""
import math

import lrrcs as lrr


def _priced(loading):
    return lrr.LongRunRisksModel(
        claims={"claim": lrr.ClaimParams.from_loading(loading)}
    ).solve(method="analytical")


def test_from_loading_prices_a_single_claim():
    res = _priced(1.5)
    assert res.claims == ("claim",)
    for attr in ("A1", "A2", "long_run_premium", "mean_log_pd",
                 "expected_growth", "gordon_return"):
        assert "claim" in getattr(res, attr).index, attr


def test_from_loading_monotone_in_loading():
    lo, hi = _priced(0.5), _priced(1.5)
    # Elasticity and x-news compensation rise with the loading; the claim
    # anchors at the same default linearization point in both calls.
    assert hi.A1["claim"] > lo.A1["claim"]
    assert hi.long_run_premium["claim"] > lo.long_run_premium["claim"]
    assert hi.mean_log_pd["claim"] == lo.mean_log_pd["claim"] == 3.30
    # Loading straddles 1/psi = 0.667: below it the ratio moves against
    # long-run news (hedge), above it, with the news.
    assert lo.A1["claim"] < 0.0 < hi.A1["claim"]


def test_from_loading_growth_channel_is_consistent():
    res = _priced(2.6)
    anchor = res.mean_log_pd["claim"]
    # gordon = g_eff + D/P at the anchor, both annualized in percent.
    assert math.isclose(
        res.gordon_return["claim"],
        res.expected_growth["claim"] + math.exp(-anchor) * 100,
        rel_tol=1e-9,
    )


def test_from_loading_composes_with_preference_overrides():
    patient = lrr.LongRunRisksModel(
        claims={"claim": lrr.ClaimParams.from_loading(2.6)}, gamma=7.5
    )
    assert patient.params.prefs.gamma == 7.5
    assert patient.params.claims["claim"].phi == 2.6


def test_from_loading_is_just_a_claim():
    """It builds parameters, so several claims compose in one model."""
    model = lrr.LongRunRisksModel(claims={
        "high": lrr.ClaimParams.from_loading(1.5),
        "low": lrr.ClaimParams.from_loading(0.5),
    })
    res = model.solve(method="analytical")
    assert res.A1["high"] > res.A1["low"]
    assert res.compare("high", "low").premium > 0
