"""Observation-level GMM moments: sample analogs minus model implications."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .aggregation import _flow_loadings, model_moments, var_sigma2
from .solution import BKYParams, solve_loglinear
from .states import extract_states

# Paper Table 3 order (JME p. 61). mean_dc is not a GMM column; μ_c is
# identified from E(η) after state extraction.
MOMENT_NAMES = (
    "vol_dc",
    "ac1_dc",
    "ac2_dc",
    "vol_dd",
    "ac1_dd",
    "corr_dc_dd",
    "e_eta",
    "e_u",
    "e_eta_x",
    "e_eta2_s2",
    "vol_eta2",
    "ac1_eta2",
    "mean_zd",
    "vol_zd",
    "ac1_zd",
    "mean_excess",
    "vol_rd",
    "mean_rf",
    "corr_rd_zd",
    "corr_dc_zd",
)

_BURN_IN = 3


def _acov_series(x: np.ndarray, lag: int) -> np.ndarray:
    y = np.asarray(x, dtype=float)
    z = np.full_like(y, np.nan)
    if lag < y.size:
        z[lag:] = (y[lag:] - np.nanmean(y)) * (y[:-lag] - np.nanmean(y))
    return z


def _eta2_model(params: BKYParams, h: int) -> tuple[float, float, float]:
    """vol(η^{a2}), AC1(η^{a2}), and Var(η^{a2}) from the aggregated residual.

    The residual after stripping x_{t-2h} is a Working-weighted sum of e and
    η shocks. Fourth moments are Gaussian 2σ^4 plus a stochastic-vol term
    Var(σ²) that inherits persistence ν^h.
    """
    _, c_e, c_eta = _flow_loadings(
        h, params.rho, params.phi_e, params.sigma, 1.0, 1.0,
        shift=0, n_periods=4 * h,
    )
    _, c1_e, c1_eta = _flow_loadings(
        h, params.rho, params.phi_e, params.sigma, 1.0, 1.0,
        shift=h, n_periods=4 * h,
    )
    var_eta = float(c_e @ c_e + c_eta @ c_eta)
    cov_eta = float(c_e @ c1_e + c_eta @ c1_eta)
    var_g = 2.0 * var_eta * var_eta
    acov_g = 2.0 * cov_eta * cov_eta
    vs = float(var_sigma2(params))
    if params.sigma_w > 0.0 and abs(params.nu) < 1.0:
        nu_h = float(params.nu) ** int(h)
    else:
        nu_h = 0.0
    var = var_g + vs
    acov = acov_g + nu_h * vs
    vol = float(np.sqrt(max(var, 0.0)))
    ac1 = float(acov / var) if var > 0.0 else 0.0
    return vol, ac1, float(var)


def observation_moments(
    data: pd.DataFrame,
    params: BKYParams,
    h: int,
) -> np.ndarray:
    """``(T-3, k)`` moments whose column means are the Table 3 discrepancies.

    Built from the annual panel, not from published moment values.
    ``E[Δd] = h μ_d`` is not a Table 3 moment; μ_d is identified from
    prices and from ``E(u)`` after state extraction. The first three
    rows are burn-in for lagged state residuals and AC1(η²).
    """
    sol = solve_loglinear(params)
    model = model_moments(params, h, sol=sol)
    _, ac1_eta2, var_eta2 = _eta2_model(params, h)
    dc = data["dc"].to_numpy(dtype=float)
    dd = data["dd"].to_numpy(dtype=float)
    z = data["log_pd"].to_numpy(dtype=float)
    rf = data["rf"].to_numpy(dtype=float)
    rm = data["rm"].to_numpy(dtype=float)
    excess = rm - rf
    T = dc.size
    hat = extract_states(z, rf, sol, params=params, h=h)
    mean_c = np.nanmean(dc)
    mean_d = np.nanmean(dd)
    mean_z = np.nanmean(z)
    mean_r = np.nanmean(rm)
    c_x, _, _ = _flow_loadings(h, params.rho, params.phi_e, params.sigma, 1.0, 1.0)
    y_x, _, _ = _flow_loadings(
        h, params.rho, params.phi_e, params.sigma, params.phi_d, params.phi_d_sigma
    )

    cols = []
    cols.append((dc - model["mean_dc"]) ** 2 - model["vol_dc"] ** 2)
    cols.append(_acov_series(dc, 1) - model["ac1_dc"] * model["vol_dc"] ** 2)
    cols.append(_acov_series(dc, 2) - model["ac2_dc"] * model["vol_dc"] ** 2)
    cols.append((dd - model["mean_dd"]) ** 2 - model["vol_dd"] ** 2)
    cols.append(_acov_series(dd, 1) - model["ac1_dd"] * model["vol_dd"] ** 2)
    cols.append(
        (dc - mean_c) * (dd - mean_d)
        - model["corr_dc_dd"] * model["vol_dc"] * model["vol_dd"]
    )
    eta = np.full(T, np.nan)
    u = np.full(T, np.nan)
    # Annual Δc_τ loads on x at the start of the two-year window (τ-2).
    eta[2:] = dc[2:] - params.mu_c * h - c_x * hat.x[:-2]
    u[2:] = dd[2:] - params.mu_d * h - y_x * hat.x[:-2]
    cols.append(eta)
    cols.append(u)
    xlag2 = np.full(T, np.nan)
    xlag2[2:] = hat.x[:-2]
    cols.append(eta * xlag2)
    eta2 = eta**2
    s2_lag = np.full(T, np.nan)
    s2_lag[2:] = hat.sigma2[:-2]
    cols.append(eta2 - s2_lag)
    eta2_mean = np.nanmean(eta2)
    eta2_d = eta2 - eta2_mean
    cols.append(eta2_d**2 - var_eta2)
    ac_eta2 = np.full(T, np.nan)
    ac_eta2[3:] = eta2_d[3:] * eta2_d[2:-1] - ac1_eta2 * var_eta2
    cols.append(ac_eta2)
    cols.append(z - model["mean_zd"])
    cols.append((z - model["mean_zd"]) ** 2 - model["vol_zd"] ** 2)
    cols.append(_acov_series(z, 1) - model["ac1_zd"] * model["vol_zd"] ** 2)
    cols.append(excess - model["mean_excess"])
    cols.append((rm - mean_r) ** 2 - model["vol_rd"] ** 2)
    cols.append(rf - model["mean_rf"])
    rd_z = np.full(T, np.nan)
    rd_z[1:] = (rm[1:] - mean_r) * (z[:-1] - mean_z)
    cols.append(rd_z - model["corr_rd_zd"] * model["vol_rd"] * model["vol_zd"])
    dc_z = np.full(T, np.nan)
    dc_z[1:] = (dc[1:] - mean_c) * (z[:-1] - mean_z)
    cols.append(dc_z - model["corr_dc_zd"] * model["vol_dc"] * model["vol_zd"])
    g = np.column_stack(cols)
    if g.shape[0] > _BURN_IN:
        g = g[_BURN_IN:]
    return g
