"""Package tests for price_from_loadings (Issue 5)."""
import lrrcs as lrr


def test_price_from_loadings_exported():
    assert "price_from_loadings" in lrr.__all__
    assert callable(lrr.price_from_loadings)


def test_price_from_loadings_monotone_in_loading():
    lo = lrr.price_from_loadings(0.5)
    hi = lrr.price_from_loadings(1.5)
    # Elasticity and x-news compensation rise with the loading; the claim
    # anchors at the same default linearization point in both calls.
    assert hi["A1"] > lo["A1"]
    assert hi["premium_lr"] > lo["premium_lr"]
    assert hi["mean_log_pd"] == lo["mean_log_pd"] == 3.30
    # Loading straddles 1/psi = 0.667: below it the ratio moves against
    # long-run news (hedge), above it, with the news.
    assert lo["A1"] < 0.0 < hi["A1"]


def test_price_from_loadings_returns_expected_keys():
    out = lrr.price_from_loadings(2.6)
    for key in ("loading", "A1", "A2", "premium_lr", "mean_log_pd", "g_eff", "gordon_return"):
        assert key in out, key
    assert out["loading"] == 2.6
    # Growth channel is internally consistent: gordon = g_eff + D/P.
    import math
    assert math.isclose(out["gordon_return"], out["g_eff"] + math.exp(-out["mean_log_pd"]), rel_tol=1e-9)
