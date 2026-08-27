"""Long-run leverage φ̃ via Kiku (2006) equation (19)."""
from __future__ import annotations
import numpy as np

from .expected_growth import expected_growth_proxy


def estimate_long_run_leverage(
    dc: np.ndarray,
    dd: np.ndarray,
    window: int = 2,
) -> float:
    """
    Estimate the long-run leverage coefficient φ̃ exactly as in the paper’s
    equation (19):

        Δd_t = d0 + φ̃ * MA(Δc, window) + ε_t

    Parameters
    ----------
    dc, dd : 1-d arrays of consumption and dividend growth (same frequency).
    window : number of lags to average (paper uses 2 years).

    Returns
    -------
    The OLS coefficient φ̃ on the moving average of lagged consumption growth.
    """
    dc = np.asarray(dc, dtype=float).ravel()
    dd = np.asarray(dd, dtype=float).ravel()
    if len(dc) != len(dd):
        raise ValueError("dc and dd must have the same length")
    ma = expected_growth_proxy(dc, window=window)
    mask = ~np.isnan(ma)
    y = dd[mask]
    x = ma[mask]
    x_demean = x - x.mean()
    y_demean = y - y.mean()
    phi = float(np.dot(x_demean, y_demean) / np.dot(x_demean, x_demean))
    return phi
