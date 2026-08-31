"""Comparison is an analysis step, not something the model has to know.

These tests replace the old test_legs.py: there is no leg resolution any
more, so what used to be pinned at construction is pinned here instead.
"""
import numpy as np
import pytest

import lrrcs as lrr
from lrrcs.calibration import calibrate_claims


@pytest.fixture(scope="module")
def paper():
    return lrr.LongRunRisksModel().solve(n_x=15, n_s=4)


def _renamed_paper_model(**names):
    """The paper calibration under caller-chosen claim names."""
    base = lrr.ModelParams().claims
    return lrr.LongRunRisksModel(claims={
        names["long"]: base["value"],
        names["short"]: base["growth"],
        names["market"]: base["market"],
    })


# -- the comparison itself ------------------------------------------------
def test_compare_reports_the_spread(paper):
    cmp = paper.compare("value", "growth", market="market")
    assert cmp.premium == pytest.approx(
        paper.expected_returns["value"] - paper.expected_returns["growth"]
    )
    assert cmp.log_pd_spread == pytest.approx(
        paper.mean_log_pd["value"] - paper.mean_log_pd["growth"]
    )
    assert cmp.volatility_spread == pytest.approx(
        paper.volatility["value"] - paper.volatility["growth"]
    )
    assert cmp.beta_ratio == pytest.approx(
        paper.capm_betas("market")["value"] / paper.capm_betas("market")["growth"]
    )


def test_compare_labels_the_paper_pair(paper):
    assert paper.compare("value", "growth").label == "Value premium"
    assert "Value premium" in paper.compare("value", "growth").summary().as_text()


def test_compare_labels_other_pairs_long_short():
    res = _renamed_paper_model(long="robust", short="weak", market="mkt").solve(
        n_x=15, n_s=4
    )
    cmp = res.compare("robust", "weak", market="mkt")
    assert cmp.label == "Long-short premium"
    assert "Long-short premium" in cmp.summary().as_text()
    assert cmp.premium > 0


def test_compare_works_without_a_market(paper):
    cmp = paper.compare("value", "growth")
    assert np.isfinite(cmp.premium)
    assert not np.isfinite(cmp.beta_ratio)
    assert cmp.betas.isna().all()


def test_compare_rejects_unknown_and_identical_claims(paper):
    with pytest.raises(KeyError, match="nope"):
        paper.compare("nope", "growth")
    with pytest.raises(KeyError, match="market="):
        paper.compare("value", "growth", market="nope")
    with pytest.raises(ValueError, match="two different claims"):
        paper.compare("value", "value")


def test_compare_to_frame_is_one_row(paper):
    frame = paper.compare("value", "growth", market="market").to_frame()
    assert len(frame) == 1
    for col in ("long", "short", "premium", "log_pd_spread", "beta_ratio"):
        assert col in frame.columns


def test_analytical_compare_uses_the_long_run_premium():
    res = lrr.LongRunRisksModel().solve(method="analytical")
    cmp = res.compare("value", "growth")
    assert cmp.premium == pytest.approx(
        res.long_run_premium["value"] - res.long_run_premium["growth"]
    )
    assert cmp.premium_measure == "long-run risk premium"
    # The log-linear solution has no return distribution.
    assert not np.isfinite(cmp.volatility_spread)
    assert not np.isfinite(cmp.beta_ratio)


# -- betas need a reference, and any claim can be it ----------------------
def test_betas_available_for_every_claim(paper):
    betas = paper.capm_betas("market")
    assert set(betas.index) == set(paper.claims)
    assert betas["market"] == 1.0
    # A claim that is neither long nor short still gets one, which the
    # pre-0.7.0 moments could not produce.
    assert np.isfinite(betas["growth"]) and np.isfinite(betas["value"])


def test_any_claim_can_serve_as_the_reference(paper):
    vs_value = paper.capm_betas("value")
    assert vs_value["value"] == 1.0
    assert np.isfinite(vs_value["market"])


def test_capm_betas_rejects_an_unknown_reference(paper):
    with pytest.raises(KeyError, match="market="):
        paper.capm_betas("nope")


# -- calibration to comparison, end to end --------------------------------
def test_calibrated_cross_section_compares_without_roles():
    rng = np.random.default_rng(4)
    n = 60
    dc = rng.normal(0.02, 0.03, size=n)
    series = {
        "quality": 0.03 + 0.8 * dc + rng.normal(0, 0.04, size=n),
        "junk": 0.01 + 0.2 * dc + rng.normal(0, 0.04, size=n),
        "market": 0.02 + 0.5 * dc + rng.normal(0, 0.03, size=n),
    }
    model = lrr.LongRunRisksModel(claims=calibrate_claims(dc, series))
    assert set(model.params.claims) == {"quality", "junk", "market"}
    res = model.solve(method="analytical")
    assert np.isfinite(res.compare("quality", "junk").premium)
