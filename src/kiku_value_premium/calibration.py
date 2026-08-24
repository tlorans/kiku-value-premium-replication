"""
Calibration of DividendParams following Kiku (2006, Section 4.3).

Provides both the exact Table II values and a general data-driven procedure
that can be applied to *any* set of portfolios.

General recipe for an arbitrary portfolio with dividend-growth series dd and
consumption-growth series dc (same frequency):

1. μ   = mean(dd)          (scale by 1/12 if the series is annual and you want
                            a monthly parameter)
2. φ   = OLS coefficient from the paper’s regression (eq. 19)

       Δd_t = d0 + φ̃ · MA(Δc, window=2) + ε_t

3. α   ≈ Corr( residual from the regression , consumption innovation )
         or the simpler Corr(dd, dc) as a first approximation
4. φ_σ chosen so that the model residual volatility roughly matches the data
   residual volatility (or left as a free parameter for the user to fine-tune)

The helper `calibrate_from_data` implements this recipe automatically.
"""
from __future__ import annotations
import numpy as np
from typing import Dict, Optional, Union
from .params import DividendParams, ModelParams, get_default_params


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
    x_demean = x - x.mean()
    y_demean = y - y.mean()
    denom = np.dot(x_demean, x_demean)
    if denom < 1e-18:
        return 0.0
    return float(np.dot(x_demean, y_demean) / denom)


def _consumption_innovation(dc: np.ndarray) -> np.ndarray:
    """Simple AR(1) residual as a proxy for the consumption innovation η."""
    dc = np.asarray(dc, dtype=float).ravel()
    if len(dc) < 3:
        return dc - dc.mean()
    # AR(1)
    y = dc[1:]
    x = dc[:-1]
    x_d = x - x.mean()
    y_d = y - y.mean()
    rho = np.dot(x_d, y_d) / max(np.dot(x_d, x_d), 1e-18)
    resid = np.empty_like(dc)
    resid[0] = 0.0
    resid[1:] = y - (dc.mean() * (1 - rho) + rho * x)
    return resid


def calibrate_from_data(
    dc: np.ndarray,
    dd_dict: Dict[str, np.ndarray],
    frequency: str = "annual",
    window: int = 2,
    default_phi_sigma: float = 7.5,
) -> Dict[str, DividendParams]:
    """
    Calibrate DividendParams for *any* set of portfolios from observed series.

    Parameters
    ----------
    dc : array
        Consumption growth (annual or monthly).
    dd_dict : dict[str, array]
        Mapping portfolio name → dividend-growth series (same length & frequency as dc).
    frequency : {"annual", "monthly"}
        If "annual", the returned μ is divided by 12 so that it can be used
        directly as a monthly parameter in the model.
    window : int
        Lags for the moving-average regression that identifies φ (paper uses 2).
    default_phi_sigma : float
        Fallback value for φ_σ when residual volatility is hard to map.
        Users can override after inspection.

    Returns
    -------
    dict[str, DividendParams]
        Ready to be assigned to ModelParams.dividends.

    Example
    -------
    >>> from kiku_value_premium.calibration import calibrate_from_data
    >>> # dc_annual, dd_growth, dd_value are 1-d numpy arrays of the same length
    >>> params = calibrate_from_data(
    ...     dc_annual,
    ...     {"growth": dd_growth, "value": dd_value, "my_portfolio": dd_mine},
    ...     frequency="annual",
    ... )
    >>> print(params["value"].phi)   # estimated long-run leverage
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

        # 3. residual after the MA regression → correlation with consumption innovation
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

        # 4. φ_σ – rough mapping from residual volatility
        #    In the model residual vol ≈ φ_σ * σ * sqrt(1-α²).
        #    We leave a sensible default and let the user fine-tune.
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
    print()
    print("For arbitrary portfolios use:")
    print("  from kiku_value_premium.calibration import calibrate_from_data")
    print("  params = calibrate_from_data(dc, {'portA': dd_A, 'portB': dd_B})")
