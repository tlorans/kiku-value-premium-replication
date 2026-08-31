import numpy as np

import lrrcs as lrr
from lrrcs.calibration import calibrate_from_data
from lrrcs.model import resolve_legs


def test_resolve_legs_paper_aliases():
    long_k, short_k, mkt = resolve_legs({"growth": 1, "value": 2, "market": 3})
    assert (long_k, short_k, mkt) == ("value", "growth", "market")


def test_resolve_legs_long_short_keys():
    long_k, short_k, mkt = resolve_legs({"long": 1, "short": 2, "market": 3})
    assert (long_k, short_k, mkt) == ("long", "short", "market")


def test_resolve_legs_explicit_override():
    long_k, short_k, mkt = resolve_legs(
        {"robust": 1, "weak": 2, "mkt": 3},
        long="robust",
        short="weak",
        market="mkt",
    )
    assert (long_k, short_k, mkt) == ("robust", "weak", "mkt")


def test_calibrate_from_data_long_short_kwargs():
    rng = np.random.default_rng(4)
    n = 40
    dc = rng.normal(0.02, 0.03, size=n)
    dd_long = 0.03 + 0.8 * dc + rng.normal(0, 0.04, size=n)
    dd_short = 0.01 + 0.2 * dc + rng.normal(0, 0.04, size=n)
    dd_m = 0.02 + 0.5 * dc + rng.normal(0, 0.03, size=n)
    out = calibrate_from_data(
        dc, frequency="annual", window=2, long=dd_long, short=dd_short, market=dd_m
    )
    assert set(out) == {"long", "short", "market"}
    assert out["long"].mu > out["short"].mu


def _long_short_model(**kwargs):
    """The paper calibration under long/short/market names."""
    paper = lrr.ModelParams()
    return lrr.LongRunRisksModel(
        claims={
            "short": paper.dividends["growth"],
            "long": paper.dividends["value"],
            "market": paper.dividends["market"],
        },
        **kwargs,
    )


def test_model_resolves_long_short_names():
    model = _long_short_model()
    assert model.legs == ("long", "short", "market")

    res = model.solve(method="analytical")
    assert res.long_run_premium["long"] > res.long_run_premium["short"]
    assert "Long-short premium" in res.summary().as_text()

    grid = model.solve(n_x=15, n_s=4)
    assert grid.expected_returns["long"] > grid.expected_returns["short"]
    assert grid.value_premium == grid.long_short_premium


def test_model_accepts_explicit_leg_names():
    paper = lrr.ModelParams()
    model = lrr.LongRunRisksModel(
        claims={
            "weak": paper.dividends["growth"],
            "robust": paper.dividends["value"],
            "mkt": paper.dividends["market"],
        },
        long="robust",
        short="weak",
        market="mkt",
    )
    assert model.legs == ("robust", "weak", "mkt")
    res = model.solve(method="analytical")
    assert res.value_premium > 0


def test_paper_keys_still_work():
    res = lrr.LongRunRisksModel().solve(method="analytical")
    assert res.long_run_premium["value"] > res.long_run_premium["growth"]
    assert "Value premium" in res.summary().as_text()
