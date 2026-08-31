"""
Calibrate cash-flow dynamics *only* to time-series moments.

Critical discipline of the paper: never target cross-sectional return premia.
`calibrate_from_data` implements the recipe for any set of portfolios.
"""
from __future__ import annotations
import numpy as np
from typing import Dict
from ..model.params import DividendParams
from .leverage import estimate_long_run_leverage


def _consumption_innovation(dc: np.ndarray) -> np.ndarray:
    """Rough proxy for the short-run consumption innovation."""
    dc = np.asarray(dc, dtype=float).ravel()
    if len(dc) < 3:
        return dc - dc.mean()
    if float(np.std(dc)) < 1e-15:
        return np.zeros_like(dc)
    rho = np.corrcoef(dc[:-1], dc[1:])[0, 1]
    if not np.isfinite(rho):
        rho = 0.0
    innov = np.empty_like(dc)
    innov[0] = 0.0
    innov[1:] = dc[1:] - rho * dc[:-1]
    return innov


def calibrate_from_data(
    dc: np.ndarray,
    dd_dict: Dict[str, np.ndarray] | None = None,
    frequency: str = "annual",
    window: int = 2,
    default_phi_sigma: float = 7.5,
    *,
    long: np.ndarray | None = None,
    short: np.ndarray | None = None,
    market: np.ndarray | None = None,
) -> Dict[str, DividendParams]:
    """Calibrate cash-flow ``DividendParams`` from consumption and dividend growth.

    Never targets cross-sectional return premia. Pass the high-return leg as
    ``long=`` and the low-return leg as ``short=``. Paper names ``value`` /
    ``growth`` in ``dd_dict`` remain valid aliases.

    Examples
    --------
    ```python
    import lrrcs as lrr
    div = lrr.calibrate_from_data(dc, long=dd_value, short=dd_growth, market=dd_mkt)
    ```
    """
    series: Dict[str, np.ndarray] = dict(dd_dict or {})
    if long is not None:
        series["long"] = long
    if short is not None:
        series["short"] = short
    if market is not None:
        series["market"] = market
    if not series:
        raise ValueError(
            "Provide dd_dict or at least one of long=, short=, market=."
        )

    dc = np.asarray(dc, dtype=float).ravel()
    innov = _consumption_innovation(dc)
    scale = 12.0 if frequency == "annual" else 1.0

    out: Dict[str, DividendParams] = {}
    for name, dd in series.items():
        dd = np.asarray(dd, dtype=float).ravel()
        if len(dd) != len(dc):
            raise ValueError(f"Length mismatch for portfolio '{name}'")

        mu = float(np.mean(dd)) / scale
        phi = estimate_long_run_leverage(dc, dd, window=window)

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

        sigma_resid = float(np.std(resid))
        sigma_innov = float(np.std(innov_m))
        if sigma_innov > 1e-12 and np.isfinite(sigma_resid):
            phi_sigma = sigma_resid / sigma_innov
        else:
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

