"""Recover latent (x_t, σ²_t) from observed log P/D and the risk-free rate."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .solution import BKYParams, LogLinearSolution

_SIGMA2_FLOOR = 1e-10
_N_GRID = 41
_SD_SPAN = 4.0
# Empirical compromise: raw λ=1/qx AR dominates the affine residual.
_AR_BAND = 0.5
_LAMBDA_X = 1.0
_LAMBDA_S = 1.0


@dataclass
class ExtractedStates:
    x: np.ndarray
    sigma2: np.ndarray


def _annual_map(
    sol: LogLinearSolution, params: BKYParams | None, h: int
) -> tuple[float, float, float, float, float, float]:
    """Observation intercepts and slopes at the sampling frequency.

    ``h=1`` is the decision-frequency map (JME eq. 23). For ``h>1`` the
    observed series are annual: P/D is year-end affine minus the trailing
    dividend log-sum, and the risk-free rate is the same-date eq. 23 map
    with ``F`` scaled by ``h``. Unconditional moments in
    ``aggregation._rf_moments`` use the geometric intra-year sum; those
    are a different object from this invert.
    """
    A1, A2 = sol.A_d1, sol.A_d2
    F1, F2 = float(sol.F[1]), float(sol.F[2])
    A0 = sol.A_d0
    F0 = float(sol.F[0])
    if params is not None and h > 1:
        A0 = A0 - np.log(float(h)) - 0.5 * params.mu_d * (h - 1)
        F0, F1, F2 = h * F0, h * F1, h * F2
    return float(A0), float(A1), float(A2), float(F0), float(F1), float(F2)


def _uncond_var_x(params: BKYParams) -> float:
    den = max(1.0 - float(params.rho) ** 2, 1e-12)
    return max((float(params.phi_e) * float(params.sigma)) ** 2 / den, 1e-16)


def _uncond_var_s2(params: BKYParams) -> float:
    if abs(float(params.nu)) >= 1.0:
        return 1e-20
    den = max(1.0 - float(params.nu) ** 2, 1e-12)
    return max(float(params.sigma_w) ** 2 / den, 1e-30)


def _axis(
    pred: float,
    obs: float,
    half_width: float,
    n: int,
    floor: float | None = None,
) -> np.ndarray:
    """Linspace covering ``pred ± half_width`` and ``obs``, plus both as nodes."""
    lo = min(pred - half_width, obs)
    hi = max(pred + half_width, obs)
    if floor is not None:
        lo = max(lo, floor)
        hi = max(hi, floor)
        pred = max(pred, floor)
        obs = max(obs, floor)
    if hi <= lo:
        pad = half_width if half_width > 0.0 else (abs(lo) + 1.0) * 1e-6
        hi = lo + pad
    nodes = np.linspace(lo, hi, int(n))
    return np.unique(np.concatenate((nodes, np.array([pred, obs], dtype=float))))


def extract_states(
    log_pd: np.ndarray,
    rf: np.ndarray,
    sol: LogLinearSolution,
    *,
    params: BKYParams | None = None,
    h: int = 1,
    sigma2_floor: float = _SIGMA2_FLOOR,
    ar: bool = True,
) -> ExtractedStates:
    """Constrained least squares of JME eq. 23, with AR dynamics.

    Date by date the 2×2 map is inverted and ``σ²`` is projected onto
    ``(sigma2_floor, ∞)``. When ``ar`` and ``params`` are set, each later
    date is a 2-D grid search around the AR prediction and the CLS point
    (JME fn. 6). The score is the affine residual of eq. 23 plus an AR
    penalty on ``x`` and ``σ²`` scaled by the h-step innovation variances.
    The AR terms use the excess outside ``_AR_BAND`` unconditional sds of
    the prediction (zero inside that dead zone), which is what separates
    a well-fitting monthly invert from a far annual invert.
    """
    z = np.asarray(log_pd, dtype=float).ravel()
    r = np.asarray(rf, dtype=float).ravel()
    if z.shape != r.shape:
        raise ValueError("log_pd and rf must have the same length.")
    A0, A1, A2, F0, F1, F2 = _annual_map(sol, params, h)
    det = A1 * F2 - A2 * F1
    if abs(det) < 1e-18:
        raise RuntimeError("Affine state map is singular at these parameters.")
    dz = z - A0
    dr = r - F0
    x_obs = (F2 * dz - A2 * dr) / det
    s2_obs = (-F1 * dz + A1 * dr) / det
    s2_obs = np.maximum(s2_obs, sigma2_floor)
    if not ar or params is None or z.size == 0:
        return ExtractedStates(x=x_obs, sigma2=s2_obs)

    rho_h = float(params.rho) ** int(h)
    nu_h = float(params.nu) ** int(h)
    s2_bar = float(params.sigma) ** 2
    var_x = _uncond_var_x(params)
    var_s = _uncond_var_s2(params)
    sd_x = float(np.sqrt(var_x))
    sd_s = float(np.sqrt(var_s))
    qx = max((1.0 - rho_h**2) * var_x, 1e-16)
    qs = max((1.0 - nu_h**2) * var_s, 1e-30)
    band_x = _AR_BAND * sd_x
    band_s = _AR_BAND * sd_s
    x = np.empty_like(x_obs)
    s2 = np.empty_like(s2_obs)
    x[0] = x_obs[0]
    s2[0] = s2_obs[0]
    for t in range(1, z.size):
        x_pred = rho_h * x[t - 1]
        s2_pred = s2_bar * (1.0 - nu_h) + nu_h * s2[t - 1]
        xg = _axis(x_pred, float(x_obs[t]), _SD_SPAN * sd_x, _N_GRID)[:, np.newaxis]
        sg = _axis(
            s2_pred,
            float(s2_obs[t]),
            _SD_SPAN * sd_s,
            _N_GRID,
            floor=sigma2_floor,
        )[np.newaxis, :]
        ez = z[t] - A0 - A1 * xg - A2 * sg
        er = r[t] - F0 - F1 * xg - F2 * sg
        ax = np.maximum(np.abs(xg - x_pred) - band_x, 0.0)
        a_s = np.maximum(np.abs(sg - s2_pred) - band_s, 0.0)
        score = (
            ez * ez / (1.0 + A1 * A1 + A2 * A2)
            + er * er / (1.0 + F1 * F1 + F2 * F2)
            + _LAMBDA_X * (ax * ax) / qx
            + _LAMBDA_S * (a_s * a_s) / qs
        )
        i, j = np.unravel_index(int(np.argmin(score)), score.shape)
        x[t] = xg[i, 0]
        s2[t] = sg[0, j]
    return ExtractedStates(x=x, sigma2=s2)

