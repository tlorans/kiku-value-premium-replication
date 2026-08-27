import numpy as np

from lrrcs.calibration import calibrate_from_data
from lrrcs.model import (
    ModelParams,
    get_table_ii_params,
    resolve_legs,
    solve_analytical,
    print_long_short_premium,
    ModelSolver,
)
from lrrcs.implications import compute_asset_pricing_moments


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


def test_analytical_and_moments_accept_long_short():
    paper = get_table_ii_params()
    params = ModelParams(
        prefs=paper.prefs,
        cons=paper.cons,
        dividends={
            "short": paper.dividends["growth"],
            "long": paper.dividends["value"],
            "market": paper.dividends["market"],
        },
    )
    sol = solve_analytical(params)
    assert sol.premium_lr["long"] > sol.premium_lr["short"]
    print_long_short_premium(sol)
    solver = ModelSolver(params, n_x=5, n_s=2, n_quad=3)
    solver.solve()
    mom = compute_asset_pricing_moments(solver)
    assert mom["long"] == "long" and mom["short"] == "short"
    assert mom["mean_return"]["long"] > mom["mean_return"]["short"]
    assert "value_premium" in mom and "long_short_premium" in mom


def test_paper_keys_still_work():
    sol = solve_analytical(get_table_ii_params())
    assert sol.premium_lr["value"] > sol.premium_lr["growth"]
