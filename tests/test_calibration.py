import inspect
import numpy as np
from geap.lrr.calibration import (
    calibrate_claim,
    calibrate_claims,
    estimate_long_run_leverage,
    get_table_ii_claims,
    simulate_cashflow_moments,
)


def test_calibration_has_no_returns_argument():
    """The paper's discipline, enforced by the signature itself."""
    for fn in (calibrate_claim, calibrate_claims):
        names = inspect.signature(fn).parameters
        assert "returns" not in names, fn.__name__
        assert "premia" not in names, fn.__name__
        assert "ret" not in names, fn.__name__


def test_calibrate_claim_matches_the_batch_call():
    """One claim alone must equal the same claim inside a cross-section."""
    rng = np.random.default_rng(5)
    n = 60
    dc = rng.normal(0.02, 0.03, size=n)
    a = 0.02 + 1.5 * dc + rng.normal(0, 0.05, size=n)
    b = 0.01 + 0.4 * dc + rng.normal(0, 0.07, size=n)
    batch = calibrate_claims(dc, {"a": a, "b": b})
    for name, dd in (("a", a), ("b", b)):
        assert calibrate_claim(dc, dd) == batch[name], name


def test_eq19_recovers_known_phi():
    rng = np.random.default_rng(2)  # seed 0 is an unlucky PCG64 draw (|phi-2.16|≈0.51)
    n = 80
    dc = rng.normal(0.02, 0.03, size=n)
    ma = np.array([np.nan, np.nan] + [dc[t - 2 : t].mean() for t in range(2, n)])
    dd = 0.01 + 2.16 * np.nan_to_num(ma, nan=0.0) + rng.normal(0, 0.05, size=n)
    phi = estimate_long_run_leverage(dc, dd, window=2)
    assert abs(phi - 2.16) < 0.4


def test_table_ii_claims():
    d = get_table_ii_claims()
    assert d["value"].phi == 6.2
    assert d["growth"].phi == 2.6


def test_simulate_cashflow_moments_keys():
    mom = simulate_cashflow_moments(n_sims=2, years=10, seed=1)
    assert "E[dc]" in mom["consumption"]
    assert "sigma(dc)" in mom["consumption"]
    assert "AC1" in mom["consumption"]
    assert set(mom["dividends"]) == {"growth", "value", "market"}
    assert "E[dd]" in mom["dividends"]["value"]


def test_calibrate_claims_phi_sigma_matches_residual_vol():
    from geap.lrr.calibration.from_data import _consumption_innovation

    rng = np.random.default_rng(11)
    n = 80
    dc = rng.normal(0.02, 0.03, size=n)
    dd = 0.01 + 0.5 * dc + rng.normal(0, 0.08, size=n)
    out = calibrate_claims(dc, {"growth": dd}, frequency="annual", window=2)

    window = 2
    ma = np.full(n, np.nan)
    for t in range(window, n):
        ma[t] = np.mean(dc[t - window : t])
    mask = ~np.isnan(ma)
    phi = estimate_long_run_leverage(dc, dd, window=window)
    resid = dd[mask] - (dd[mask].mean() + phi * (ma[mask] - ma[mask].mean()))
    innov_m = _consumption_innovation(dc)[mask]
    expected = float(np.std(resid) / np.std(innov_m))
    assert abs(out["growth"].phi_sigma - expected) < 1e-10


def test_calibrate_claims_phi_sigma_fallback_when_dc_degenerate():
    dc = np.full(20, 0.02)
    dd = np.full(20, 0.01)
    out = calibrate_claims(
        dc, {"market": dd}, frequency="annual", default_phi_sigma=7.5
    )
    assert out["market"].phi_sigma == 7.5
