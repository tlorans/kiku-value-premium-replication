"""
Compute returns, risk-free rate and the key asset-pricing moments of Tables VII–X
from the solved valuation functions z_c, z_i on the discrete Markov chain.

Uses the stationary distribution of Π together with an additional short-run
Gauss-Hermite integral so that both long-run and short-run risks enter the
moments.
"""
from __future__ import annotations
import numpy as np
from .solver import ModelSolver, HAS_NUMBA, njit
from .params import get_default_params


@njit(cache=True)
def _accumulate_moments(
    z_c, z_g, z_v, z_m, Pi, x, sig,
    mu_c, mu_g, phi_g, phi_sigma_g, alpha_g,
    mu_v, phi_v, phi_sigma_v, alpha_v,
    mu_m, phi_m, phi_sigma_m, alpha_m,
    delta, theta, psi,
    eta_nodes, eta_weights
):
    """
    For every current state i accumulate the probability-weighted
    one-period gross returns and the SDF, so that unconditional
    moments can be formed with the stationary distribution.
    Returns arrays of shape (n_states,) of conditional expectations
    E[R | i], E[R² | i], E[M | i], etc.
    """
    n = z_c.shape[0]
    n_q = eta_nodes.shape[0]

    # conditional expectations
    E_Rf_inv = np.zeros(n)          # E[M | i] = 1/Rf(i)
    E_Rg = np.zeros(n)
    E_Rv = np.zeros(n)
    E_Rm = np.zeros(n)
    E_Rg2 = np.zeros(n)
    E_Rv2 = np.zeros(n)
    E_Rm2 = np.zeros(n)
    E_Rg_Rm = np.zeros(n)
    E_Rv_Rm = np.zeros(n)

    for i in range(n):
        xi = x[i]
        si = sig[i]
        zci = z_c[i]
        zgi = z_g[i]
        zvi = z_v[i]
        zmi = z_m[i]

        for q in range(n_q):
            eta = eta_nodes[q]
            w = eta_weights[q]
            dc = mu_c + xi + si * eta

            # residual innovations
            ug = alpha_g * eta
            uv = alpha_v * eta
            um = alpha_m * eta

            ddg = mu_g + phi_g * xi + phi_sigma_g * si * ug
            ddv = mu_v + phi_v * xi + phi_sigma_v * si * uv
            ddm = mu_m + phi_m * xi + phi_sigma_m * si * um

            # loop over next states
            for j in range(n):
                p = Pi[i, j]
                if p < 1e-18:
                    continue
                weight = p * w

                # wealth return and SDF
                rc = dc + np.log(1.0 + np.exp(z_c[j])) - zci
                m = (theta * np.log(delta)
                     - (theta / psi) * dc
                     + (theta - 1.0) * rc)
                M = np.exp(m)

                # equity gross returns
                Rg = np.exp(ddg) * (1.0 + np.exp(z_g[j])) / np.exp(zgi)
                Rv = np.exp(ddv) * (1.0 + np.exp(z_v[j])) / np.exp(zvi)
                Rm = np.exp(ddm) * (1.0 + np.exp(z_m[j])) / np.exp(zmi)

                E_Rf_inv[i] += weight * M
                E_Rg[i] += weight * Rg
                E_Rv[i] += weight * Rv
                E_Rm[i] += weight * Rm
                E_Rg2[i] += weight * Rg * Rg
                E_Rv2[i] += weight * Rv * Rv
                E_Rm2[i] += weight * Rm * Rm
                E_Rg_Rm[i] += weight * Rg * Rm
                E_Rv_Rm[i] += weight * Rv * Rm

    return (E_Rf_inv, E_Rg, E_Rv, E_Rm,
            E_Rg2, E_Rv2, E_Rm2, E_Rg_Rm, E_Rv_Rm)


def compute_asset_pricing_moments(solver: ModelSolver):
    """
    Given a solved ModelSolver, compute the unconditional asset-pricing
    moments that correspond to the paper’s Tables VII–X.

    Returns a dict with annualised figures (×12 for means, ×√12 for vols).
    """
    if solver.z_c is None or not solver.z:
        raise RuntimeError("Call solver.solve() before computing moments")

    if solver.stationary is None:
        solver._stationary_dist()

    p = solver.p
    c = p.cons
    g = p.dividends["growth"]
    v = p.dividends["value"]
    mkt = p.dividends["market"]

    Pi = np.ascontiguousarray(solver.grid.Pi, dtype=np.float64)
    x = np.ascontiguousarray(solver.grid.x_grid, dtype=np.float64)
    sig = np.ascontiguousarray(np.sqrt(solver.grid.s2_grid), dtype=np.float64)
    z_c = np.ascontiguousarray(solver.z_c, dtype=np.float64)
    z_g = np.ascontiguousarray(solver.z["growth"], dtype=np.float64)
    z_v = np.ascontiguousarray(solver.z["value"], dtype=np.float64)
    z_m = np.ascontiguousarray(solver.z["market"], dtype=np.float64)

    (E_Rf_inv, E_Rg, E_Rv, E_Rm,
     E_Rg2, E_Rv2, E_Rm2, E_Rg_Rm, E_Rv_Rm) = _accumulate_moments(
        z_c, z_g, z_v, z_m, Pi, x, sig,
        float(c.mu),
        float(g.mu), float(g.phi), float(getattr(g, "phi_sigma", 0.0)), float(getattr(g, "alpha", 0.0)),
        float(v.mu), float(v.phi), float(getattr(v, "phi_sigma", 0.0)), float(getattr(v, "alpha", 0.0)),
        float(mkt.mu), float(mkt.phi), float(getattr(mkt, "phi_sigma", 0.0)), float(getattr(mkt, "alpha", 0.0)),
        float(solver.delta), float(solver.theta), float(solver.psi),
        solver.eta_nodes, solver.eta_weights
    )

    pi = solver.stationary

    # Unconditional moments (monthly)
    mean_Rf_inv = float(pi @ E_Rf_inv)
    Rf = 1.0 / max(mean_Rf_inv, 1e-12)
    mean_Rg = float(pi @ E_Rg)
    mean_Rv = float(pi @ E_Rv)
    mean_Rm = float(pi @ E_Rm)

    # Second moments for vols and betas
    mean_Rg2 = float(pi @ E_Rg2)
    mean_Rv2 = float(pi @ E_Rv2)
    mean_Rm2 = float(pi @ E_Rm2)
    mean_Rg_Rm = float(pi @ E_Rg_Rm)
    mean_Rv_Rm = float(pi @ E_Rv_Rm)

    var_Rg = max(mean_Rg2 - mean_Rg**2, 0.0)
    var_Rv = max(mean_Rv2 - mean_Rv**2, 0.0)
    var_Rm = max(mean_Rm2 - mean_Rm**2, 0.0)

    # CAPM betas (monthly)
    beta_g = (mean_Rg_Rm - mean_Rg * mean_Rm) / max(var_Rm, 1e-18)
    beta_v = (mean_Rv_Rm - mean_Rv * mean_Rm) / max(var_Rm, 1e-18)

    # Annualise (simple ×12 / √12)
    ann = 12.0
    sqrt_ann = np.sqrt(ann)

    pd = solver.mean_pd()

    moments = {
        "Rf_monthly": Rf,
        "Rf_annual": Rf ** 12 - 1.0,          # exact compounding
        "E_R_growth_annual": mean_Rg ** 12 - 1.0,
        "E_R_value_annual": mean_Rv ** 12 - 1.0,
        "E_R_market_annual": mean_Rm ** 12 - 1.0,
        "premium_growth": (mean_Rg ** 12 - 1.0) - (Rf ** 12 - 1.0),
        "premium_value": (mean_Rv ** 12 - 1.0) - (Rf ** 12 - 1.0),
        "premium_market": (mean_Rm ** 12 - 1.0) - (Rf ** 12 - 1.0),
        "value_premium": (mean_Rv ** 12 - mean_Rg ** 12),
        "vol_growth_annual": np.sqrt(var_Rg) * sqrt_ann,
        "vol_value_annual": np.sqrt(var_Rv) * sqrt_ann,
        "vol_market_annual": np.sqrt(var_Rm) * sqrt_ann,
        "sharpe_growth": ((mean_Rg - Rf) / max(np.sqrt(var_Rg), 1e-12)) * sqrt_ann,
        "sharpe_value": ((mean_Rv - Rf) / max(np.sqrt(var_Rv), 1e-12)) * sqrt_ann,
        "sharpe_market": ((mean_Rm - Rf) / max(np.sqrt(var_Rm), 1e-12)) * sqrt_ann,
        "beta_growth": beta_g,
        "beta_value": beta_v,
        "mean_log_pd": pd,
        "log_pd_value_minus_growth": pd["value"] - pd["growth"],
    }
    return moments


def print_asset_pricing_moments(moments: dict):
    """Pretty-print the moments against the paper’s Table VII targets."""
    print("\n=== Asset-pricing moments from the numerical solution (Tables VII–X) ===")
    print(f"Risk-free rate (annual):     {moments['Rf_annual']*100:6.2f}%")
    print(f"E[R] Growth (annual):        {moments['E_R_growth_annual']*100:6.2f}%")
    print(f"E[R] Value  (annual):        {moments['E_R_value_annual']*100:6.2f}%")
    print(f"E[R] Market (annual):        {moments['E_R_market_annual']*100:6.2f}%")
    print(f"Value premium:               {moments['value_premium']*100:6.2f}%")
    print(f"  (paper target ≈ 5.3%)")
    print(f"Vol Growth / Value / Market: "
          f"{moments['vol_growth_annual']*100:5.1f}% / "
          f"{moments['vol_value_annual']*100:5.1f}% / "
          f"{moments['vol_market_annual']*100:5.1f}%")
    print(f"Sharpe Growth / Value / Mkt: "
          f"{moments['sharpe_growth']:5.2f} / "
          f"{moments['sharpe_value']:5.2f} / "
          f"{moments['sharpe_market']:5.2f}")
    print(f"CAPM β Growth / Value:       "
          f"{moments['beta_growth']:5.2f} / {moments['beta_value']:5.2f}")
    print(f"  (paper notes that model β_Value < β_Growth, reproducing CAPM failure)")
    print(f"Mean log PD (G / V / M):     "
          f"{moments['mean_log_pd']['growth']:.3f} / "
          f"{moments['mean_log_pd']['value']:.3f} / "
          f"{moments['mean_log_pd']['market']:.3f}")
    print(f"log-PD Value – Growth:       {moments['log_pd_value_minus_growth']:.3f}")
    print("  (paper Table VII ≈ –0.55)")
