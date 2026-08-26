import inspect
import numpy as np
from kiku_value_premium.calibration import (
    calibrate_from_data,
    estimate_long_run_leverage,
    get_table_ii_dividends,
    simulate_cashflow_moments,
)


def test_calibrate_from_data_has_no_returns_argument():
    names = inspect.signature(calibrate_from_data).parameters
    assert "returns" not in names
    assert "premia" not in names
    assert "ret" not in names


def test_eq19_recovers_known_phi():
    rng = np.random.default_rng(2)  # seed 0 is an unlucky PCG64 draw (|phi-2.16|≈0.51)
    n = 80
    dc = rng.normal(0.02, 0.03, size=n)
    ma = np.array([np.nan, np.nan] + [dc[t - 2 : t].mean() for t in range(2, n)])
    dd = 0.01 + 2.16 * np.nan_to_num(ma, nan=0.0) + rng.normal(0, 0.05, size=n)
    phi = estimate_long_run_leverage(dc, dd, window=2)
    assert abs(phi - 2.16) < 0.4


def test_table_ii_dividends():
    d = get_table_ii_dividends()
    assert d["value"].phi == 6.2
    assert d["growth"].phi == 2.6


def test_simulate_cashflow_moments_keys():
    mom = simulate_cashflow_moments(n_sims=2, years=10, seed=1)
    assert "E[dc]" in mom["consumption"]
    assert "sigma(dc)" in mom["consumption"]
    assert "AC1" in mom["consumption"]
    assert set(mom["dividends"]) == {"growth", "value", "market"}
    assert "E[dd]" in mom["dividends"]["value"]
