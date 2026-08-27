import numpy as np
import pytest

from lrrcs.calibration.expected_growth import expected_growth_proxy
from lrrcs.calibration.leverage import estimate_long_run_leverage


def test_expected_growth_proxy_window_2():
    out = expected_growth_proxy([1, 2, 3, 4], window=2)
    assert isinstance(out, np.ndarray)
    np.testing.assert_allclose(out, [np.nan, np.nan, 1.5, 2.5], equal_nan=True)


def test_expected_growth_proxy_rejects_bad_window():
    with pytest.raises(ValueError):
        expected_growth_proxy([1.0, 2.0, 3.0], window=0)


def test_expected_growth_proxy_rejects_short_series():
    with pytest.raises(ValueError):
        expected_growth_proxy([1.0, 2.0], window=2)


def test_expected_growth_proxy_polars_series_returns_ndarray():
    import polars as pl

    out = expected_growth_proxy(pl.Series("dc", [1.0, 2.0, 3.0, 4.0]), window=2)
    assert isinstance(out, np.ndarray)
    np.testing.assert_allclose(out, [np.nan, np.nan, 1.5, 2.5], equal_nan=True)


def test_leverage_still_recovers_known_phi_via_proxy():
    rng = np.random.default_rng(2)
    n = 80
    dc = rng.normal(0.02, 0.03, size=n)
    ma = expected_growth_proxy(dc, window=2)
    dd = 0.01 + 2.16 * np.nan_to_num(ma, nan=0.0) + rng.normal(0, 0.05, size=n)
    phi = estimate_long_run_leverage(dc, dd, window=2)
    assert abs(phi - 2.16) < 0.4
