"""
Step 3 of Kiku’s recipe – Calibrate cash-flow dynamics *only* to time-series moments
====================================================================================

Critical discipline of the paper: never target cross-sectional return premia.
Only match the observed time-series properties of consumption and of the
portfolios’ cash flows (especially the differential exposure to the long-run
risk factor).

The key object estimated here is the long-run leverage φ (equation 19 of the paper):

    Δd_t = d₀ + φ̃ · MA(Δc, window=2) + ε_t

`calibrate_from_data` implements the full recipe for any set of portfolios
(industries, climate-sorted portfolios, quality factors, …).
"""
from __future__ import annotations
import numpy as np
from typing import Dict, Optional, Union
from .model.params import DividendParams, ModelParams, get_default_params


# Exact values from Table II (bottom panel)
TABLE_II_DIVIDENDS = {
    "growth": dict(mu=0.0009, phi=2.6, phi_sigma=8.4, alpha=0.27),
    "value":  dict(mu=0.0019, phi=6.2, phi_sigma=7.4, alpha=0.15),
    "market": dict(mu=0.0012, phi=2.8, phi_sigma=7.5, alpha=0.55),
}

RESIDUAL_CORRELATIONS = {
    ("growth", "value"): 0.20,
    ("growth", "market"): 0.80,
    ("value", "market"): 0.45,
}


def get_table_ii_dividends() -> Dict[str, DividendParams]:
    """Return the exact DividendParams used in the paper (Table II)."""
    return {name: DividendParams(**kwargs) for name, kwargs in TABLE_II_DIVIDENDS.items()}


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
    n = len(dc)
    if n <= window:
        raise ValueError("Series too short for the requested window")

    ma = np.full(n, np.nan)
    for t in range(window, n):
        ma[t] = np.mean(dc[t - window : t])

    mask = ~np.isnan(ma)
    y = dd[mask]
    x = ma[mask]
    # simple OLS with intercept
    x_demean = x - x.mean()
    y_demean = y - y.mean()
    phi = float(np.dot(x_demean, y_demean) / np.dot(x_demean, x_demean))
    return phi


def _consumption_innovation(dc: np.ndarray) -> np.ndarray:
    """Rough proxy for the short-run consumption innovation."""
    dc = np.asarray(dc, dtype=float).ravel()
    # residual from an AR(1)
    if len(dc) < 3:
        return dc - dc.mean()
    rho = np.corrcoef(dc[:-1], dc[1:])[0, 1]
    innov = np.empty_like(dc)
    innov[0] = 0.0
    innov[1:] = dc[1:] - rho * dc[:-1]
    return innov


def calibrate_from_data(
    dc: np.ndarray,
    dd_dict: Dict[str, np.ndarray],
    frequency: str = "annual",
    window: int = 2,
    default_phi_sigma: float = 7.5,
) -> Dict[str, DividendParams]:
    """
    Full data-driven calibration of DividendParams for an arbitrary set of portfolios.

    Implements the exact recipe of Step 3:

    1. μ   = mean(dd)   (converted to monthly if frequency="annual")
    2. φ   = long-run leverage via equation (19)
    3. α   ≈ correlation of residual with consumption innovation
    4. φ_σ left at a sensible default (user can fine-tune)

    Parameters
    ----------
    dc : array
        Consumption growth series.
    dd_dict : dict
        Mapping portfolio name → dividend-growth series (same length/frequency as dc).
    frequency : {"annual", "monthly"}
        Frequency of the supplied series.
    window : int
        Window for the moving average in equation (19). Paper uses 2.

    Returns
    -------
    dict of DividendParams, one entry per portfolio.
    """
    dc = np.asarray(dc, dtype=float).ravel()
    innov = _consumption_innovation(dc)
    scale = 12.0 if frequency == "annual" else 1.0

    out: Dict[str, DividendParams] = {}
    for name, dd in dd_dict.items():
        dd = np.asarray(dd, dtype=float).ravel()
        if len(dd) != len(dc):
            raise ValueError(f"Length mismatch for portfolio '{name}'")

        # 1. mean growth → monthly μ
        mu = float(np.mean(dd)) / scale

        # 2. long-run leverage via eq. 19
        phi = estimate_long_run_leverage(dc, dd, window=window)

        # 3. residual correlation with consumption innovation
        ma = np.full(len(dc), np.nan)
        for t in range(window, len(dc)):
            ma[t] = np.mean(dc[t - window : t])
        mask = ~np.isnan(ma)
        resid = dd[mask] - (dd[mask].mean() + phi * (ma[mask] - ma[mask].mean()))
        innov_m = innov[mask]
        if np.std(resid) > 1e-12 and np.std(innov_m) > 1e-12:
            alpha = float(np.corrcoef(resid, innov_m)[0, 1])
            alpha = float(np.clip(alpha, -0.99, 0.99))
        else:
            alpha = float(np.corrcoef(dd, dc)[0, 1]) if np.std(dd) > 0 else 0.0
            alpha = float(np.clip(alpha, -0.99, 0.99))

        # 4. φ_σ – sensible default (user may fine-tune)
        phi_sigma = default_phi_sigma

        out[name] = DividendParams(
            mu=mu,
            phi=phi,
            phi_sigma=phi_sigma,
            alpha=alpha,
        )
    return out


def calibrate_dividend_params_from_targets(
    mean_annual_growth: Dict[str, float],
    long_run_leverage: Dict[str, float],
    short_run_vol_loading: Dict[str, float],
    corr_with_consumption: Dict[str, float],
) -> Dict[str, DividendParams]:
    """Construct DividendParams from the economic targets the paper matches."""
    out = {}
    for name in mean_annual_growth:
        mu_monthly = mean_annual_growth[name] / 12.0
        out[name] = DividendParams(
            mu=mu_monthly,
            phi=long_run_leverage[name],
            phi_sigma=short_run_vol_loading[name],
            alpha=corr_with_consumption[name],
        )
    return out


def print_calibration_summary(dividends: Dict[str, DividendParams]) -> None:
    """Pretty-print the calibrated long-run leverages and other parameters."""
    print("Portfolio          μ (m)     φ (long-run)   φ_σ      α")
    print("-" * 55)
    for name, d in dividends.items():
        print(f"{name:18s} {d.mu:8.5f}  {d.phi:8.3f}     {d.phi_sigma:6.2f}  {d.alpha:6.2f}")
