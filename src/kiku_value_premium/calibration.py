"""
Calibration of DividendParams following Kiku (2006, Section 4.3).

The paper chooses the dividend parameters so that the model matches:
1. Unconditional means of annual dividend growth
2. Volatilities of annual dividend growth
3. Correlations of annual Δd with annual Δc  →  α
4. Long-run consumption leverage estimated by the projection

       Δd_t = d0 + φ̃ * (Δc_{t-1} + Δc_{t-2})/2  + ε_t     (eq. 19)

   The regression coefficient φ̃ is the empirical counterpart of the model’s
   long-run loading φ. The paper sets φ_Growth = 2.6, φ_Value = 6.2,
   φ_Market = 2.8 to match the ranking and magnitude of these exposures.

5. Residual (orthogonal) correlations among the three dividend innovations.

This module exposes the exact Table II values and provides a transparent
helper that recovers an approximate φ from simulated or real data via the
same two-year MA regression used in the paper.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict, Optional
from .params import DividendParams, ModelParams, get_default_params


# Exact values from Table II (bottom panel)
TABLE_II_DIVIDENDS = {
    "growth": dict(mu=0.0009, phi=2.6, phi_sigma=8.4, alpha=0.27),
    "value":  dict(mu=0.0019, phi=6.2, phi_sigma=7.4, alpha=0.15),
    "market": dict(mu=0.0012, phi=2.8, phi_sigma=7.5, alpha=0.55),
}

# Residual correlations of the orthogonalized dividend shocks (paper p. 18)
RESIDUAL_CORRELATIONS = {
    ("growth", "value"): 0.20,
    ("growth", "market"): 0.80,
    ("value", "market"): 0.45,
}


def get_table_ii_dividends() -> Dict[str, DividendParams]:
    """Return the exact DividendParams used in the paper (Table II)."""
    return {
        name: DividendParams(**kwargs)
        for name, kwargs in TABLE_II_DIVIDENDS.items()
    }


def calibrate_dividend_params_from_targets(
    mean_annual_growth: Dict[str, float],
    long_run_leverage: Dict[str, float],
    short_run_vol_loading: Dict[str, float],
    corr_with_consumption: Dict[str, float],
) -> Dict[str, DividendParams]:
    """
    Construct DividendParams from the economic targets the paper matches.

    Parameters
    ----------
    mean_annual_growth :
        Desired E[Δd] at the annual frequency. The monthly μ is obtained by
        simple scaling (μ ≈ annual / 12).
    long_run_leverage :
        The φ coefficients (paper’s long-run risk exposures). In the data these
        are estimated by the projection onto a 2-year MA of consumption growth
        (equation 19).
    short_run_vol_loading :
        The φ_σ (ϕ in the paper) that govern exposure to high-frequency and
        volatility risks.
    corr_with_consumption :
        α = Corr(η, u) that matches the annual Corr(Δd, Δc).

    Returns
    -------
    dict of DividendParams ready to be inserted into ModelParams.
    """
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


def estimate_long_run_leverage(
    dc: np.ndarray,
    dd: np.ndarray,
    window: int = 2,
) -> float:
    """
    Estimate the long-run leverage coefficient φ̃ exactly as in the paper’s
    equation (19):

        Δd_t = d0 + φ̃ * MA(Δc, window) + ε_t

    where MA is the simple moving average of the previous `window` annual
    (or monthly) consumption-growth observations.

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

    # Moving average of the previous `window` observations of dc
    ma = np.full(n, np.nan)
    for t in range(window, n):
        ma[t] = np.mean(dc[t - window : t])

    # Restrict to observations where MA is defined
    mask = ~np.isnan(ma)
    y = dd[mask]
    x = ma[mask]
    # OLS: φ̃ = Cov(y,x) / Var(x)
    x_demean = x - x.mean()
    y_demean = y - y.mean()
    phi_hat = np.dot(x_demean, y_demean) / np.dot(x_demean, x_demean)
    return float(phi_hat)


def print_calibration_summary(params: Optional[ModelParams] = None) -> None:
    """Pretty-print the dividend calibration used by the package."""
    if params is None:
        params = get_default_params()
    print("DividendParams calibration (Kiku 2006, Table II & Section 4.3)")
    print("-" * 60)
    print(f"{'Asset':8s} {'μ (mo)':>8s} {'φ (LR)':>8s} {'φ_σ':>8s} {'α':>8s}")
    for name, d in params.dividends.items():
        print(f"{name:8s} {d.mu:8.4f} {d.phi:8.1f} {d.phi_sigma:8.1f} {d.alpha:8.2f}")
    print()
    print("How the parameters are chosen (paper):")
    print("  μ     – match E[annual Δd]")
    print("  φ     – match long-run leverage from the 2-year MA regression (eq. 19)")
    print("          Value firms have much higher φ (6.2) than growth firms (2.6)")
    print("  φ_σ   – match short-run / volatility risk exposures")
    print("  α     – match Corr(annual Δd, annual Δc)")
    print("  residual correlations among the three u-shocks are set to")
    print("          growth-value 0.20, growth-market 0.80, value-market 0.45")
