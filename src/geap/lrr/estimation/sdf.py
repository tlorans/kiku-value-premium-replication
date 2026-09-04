"""Permanent / transitory split of the log SDF (BKY 2016 JME eq. 32)."""
from __future__ import annotations

import numpy as np

from .solution import BKYParams, solve_loglinear


def sdf_loadings(params: BKYParams) -> dict:
    """Eq. 32 loadings λ1…λ4 on η, e, and the permanent / transitory w sums."""
    p = params
    sol = solve_loglinear(p)
    k1 = sol.kappa_c1
    theta = p.theta
    a2 = sol.A_c2
    den_nu = 1.0 - p.nu
    return {
        "lambda1": p.gamma,
        "lambda2": (1.0 - 1.0 / p.psi) * p.phi_e / (1.0 - k1 * p.rho),
        "lambda3": (theta - 1.0) * (k1 - 1.0) / den_nu * a2,
        "lambda4": -(theta - 1.0) * (k1 * p.nu - 1.0) / den_nu * a2,
    }


def sdf_component_vols(params: BKYParams, horizon_periods: int) -> dict:
    """Unconditional stdev of the H-period innovation into accumulated log SDF.

    ``total`` is the stdev of Σ_{j=0}^{H-1} m_{t+1+j} − E_t of that sum.
    ``growth_perm`` and ``vol_perm`` are the stdevs of the H-period increments
    of the Beveridge–Nelson permanent growth and volatility components.
    """
    h = int(horizon_periods)
    if h < 1:
        raise ValueError("horizon_periods must be a positive integer")
    p = params
    sol = solve_loglinear(p)
    lam = sol.Lambda
    g1 = sol.Gamma[1]
    g2 = sol.Gamma[2]
    sig = p.sigma
    sw = p.sigma_w
    rho = p.rho
    nu = p.nu

    nfut = np.arange(h, 0, -1) - 1
    s_rho = np.where(nfut > 0, (1.0 - rho**nfut) / (1.0 - rho), 0.0)
    s_nu = np.where(nfut > 0, (1.0 - nu**nfut) / (1.0 - nu), 0.0)
    load_e = -lam[1] + g1 * p.phi_e * s_rho
    load_w = -lam[2] + g2 * s_nu
    var_eta = h * (lam[0] * sig) ** 2
    var_e = float(np.sum((load_e * sig) ** 2))
    var_w = float(np.sum((load_w * sw) ** 2))
    total = float(np.sqrt(var_eta + var_e + var_w))

    perm_eta = lam[0] * sig
    perm_e = (-lam[1] + g1 * p.phi_e / (1.0 - rho)) * sig
    perm_w = (-lam[2] + g2 / (1.0 - nu)) * sw
    growth_perm = float(np.sqrt(h * (perm_eta**2 + perm_e**2)))
    vol_perm = float(np.sqrt(h * perm_w**2))
    return {"total": total, "growth_perm": growth_perm, "vol_perm": vol_perm}
