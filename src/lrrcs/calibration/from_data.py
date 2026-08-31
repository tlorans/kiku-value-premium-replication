"""
Calibrate cash-flow dynamics *only* to time-series moments.

Critical discipline of the paper: never target cross-sectional return premia.
`calibrate_claim` implements the recipe for one claim, and
`calibrate_claims` runs it over a whole cross-section.
"""
from __future__ import annotations
import numpy as np
from typing import Dict
from ..model.params import ClaimParams
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


def _calibrate_one(dc, innov, dd, *, window, scale, default_phi_sigma, label=""):
    """One claim's parameters. Body kept verbatim from the pre-0.7.0 loop.

    Deliberately not tidied. The inline moving average is not
    ``expected_growth_proxy`` (which raises on a short series where this
    returns all-NaN), and the statement order is what the published
    numbers were produced by.
    """
    dd = np.asarray(dd, dtype=float).ravel()
    if len(dd) != len(dc):
        raise ValueError(f"Length mismatch{label}: dd has {len(dd)}, dc has {len(dc)}")

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

    return ClaimParams(mu=mu, phi=phi, phi_sigma=phi_sigma, alpha=alpha)


def calibrate_claim(
    dc: np.ndarray,
    dd: np.ndarray,
    *,
    frequency: str = "annual",
    window: int = 2,
    default_phi_sigma: float = 7.5,
) -> ClaimParams:
    """Calibrate one claim from consumption growth and its cash-flow growth.

    Returns never enter. There is no argument that could accept one, so
    the premium the model later produces is a prediction rather than a
    fit. This is the paper's identification discipline.

    Parameters
    ----------
    dc : array-like
        Consumption growth.
    dd : array-like
        The claim's cash-flow growth, same length as ``dc``.
    frequency : {"annual", "monthly"}
        Frequency of the series. Annual input is scaled to the monthly
        parameters the solver expects.
    window : int
        Length of the moving average that proxies expected growth
        (the paper uses two years).
    default_phi_sigma : float
        Fallback volatility loading when the residual is degenerate.

    Returns
    -------
    ClaimParams

    Examples
    --------
    ```python
    import lrrcs as lrr
    value = lrr.calibrate_claim(dc, dd_value)
    model = lrr.LongRunRisksModel(claims={"value": value})
    ```
    """
    dc = np.asarray(dc, dtype=float).ravel()
    return _calibrate_one(
        dc,
        _consumption_innovation(dc),
        dd,
        window=window,
        scale=12.0 if frequency == "annual" else 1.0,
        default_phi_sigma=default_phi_sigma,
    )


def calibrate_claims(
    dc: np.ndarray,
    claims: Dict[str, np.ndarray],
    *,
    frequency: str = "annual",
    window: int = 2,
    default_phi_sigma: float = 7.5,
) -> Dict[str, ClaimParams]:
    """Calibrate a whole cross-section, one :func:`calibrate_claim` each.

    Returns never enter, here either.

    Examples
    --------
    ```python
    import lrrcs as lrr
    claims = lrr.calibrate_claims(dc, {"value": dd_v, "growth": dd_g,
                                       "market": dd_m})
    model = lrr.LongRunRisksModel(claims=claims)
    print(model.solve().compare("value", "growth", market="market").summary())
    ```
    """
    if not claims:
        raise ValueError("calibrate_claims needs at least one growth series.")
    dc = np.asarray(dc, dtype=float).ravel()
    innov = _consumption_innovation(dc)
    scale = 12.0 if frequency == "annual" else 1.0
    return {
        name: _calibrate_one(
            dc, innov, dd, window=window, scale=scale,
            default_phi_sigma=default_phi_sigma,
            label=f" for claim {name!r}",
        )
        for name, dd in claims.items()
    }


def calibrate_claims_from_targets(
    mean_annual_growth: Dict[str, float],
    long_run_leverage: Dict[str, float],
    short_run_vol_loading: Dict[str, float],
    corr_with_consumption: Dict[str, float],
) -> Dict[str, ClaimParams]:
    """Construct ClaimParams from the economic targets the paper matches."""
    out = {}
    for name in mean_annual_growth:
        mu_monthly = mean_annual_growth[name] / 12.0
        out[name] = ClaimParams(
            mu=mu_monthly,
            phi=long_run_leverage[name],
            phi_sigma=short_run_vol_loading[name],
            alpha=corr_with_consumption[name],
        )
    return out

