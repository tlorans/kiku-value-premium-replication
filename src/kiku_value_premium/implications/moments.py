"""
Section 5 of Kiku (2006) – Asset pricing implications
=====================================================

Computes the asset-pricing moments reported in Tables VII–X of the paper:
expected returns, risk-free rate, risk premia, volatilities, Sharpe ratios,
CAPM betas, and the ranking of price–dividend ratios.

Uses the stationary distribution of the Markov chain together with an
additional short-run Gauss–Hermite integral so that both long-run and
short-run risks enter the moments.
"""
from __future__ import annotations
import numpy as np
from ..model.solver import ModelSolver, HAS_NUMBA, njit
from ..model.params import get_default_params


@njit(cache=True)
def _accumulate_moments(
    z_c, z_g, z_v, z_m, Pi, x, sig,
    mu_c, mu_g, phi_g, phi_sigma_g, alpha_g,
    mu_v, phi_v, phi_sigma_v, alpha_v,
    mu_m, phi_m, phi_sigma_m, alpha_m,
    delta, theta, psi,
    eta_nodes, eta_weights
):
    n = z_c.shape[0]
    n_q = eta_nodes.shape[0]

    E_Rf_inv = np.zeros(n)
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

            ug = alpha_g * eta
            uv = alpha_v * eta
            um = alpha_m * eta

            ddg = mu_g + phi_g * xi + phi_sigma_g * si * ug
            ddv = mu_v + phi_v * xi + phi_sigma_v * si * uv
            ddm = mu_m + phi_m * xi + phi_sigma_m * si * um

            for j in range(n):
                p = Pi[i, j]
                if p < 1e-18:
                    continue
                weight = p * w

                rc = dc + np.log(1.0 + np.exp(z_c[j])) - zci
                m = (theta * np.log(delta)
                     - (theta / psi) * dc
                     + (theta - 1.0) * rc)
                M = np.exp(m)

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
    Compute the full set of asset-pricing moments from a solved ModelSolver.

    Returns a dictionary with annualised means, volatilities, Sharpe ratios,
    CAPM betas, mean log price–dividend ratios, and the value premium.
    """
    if not solver.converged or solver.z_c is None:
        raise RuntimeError("Call solver.solve() before computing moments.")

    p = solver.p
    # Require the classic three portfolios for the moment calculation
    for name in ("growth", "value", "market"):
        if name not in solver.z:
            raise KeyError(f"Equity claim '{name}' has not been solved.")

    z_c = np.ascontiguousarray(solver.z_c, dtype=np.float64)
    z_g = np.ascontiguousarray(solver.z["growth"], dtype=np.float64)
    z_v = np.ascontiguousarray(solver.z["value"], dtype=np.float64)
    z_m = np.ascontiguousarray(solver.z["market"], dtype=np.float64)
    Pi = np.ascontiguousarray(solver.grid.Pi, dtype=np.float64)
    x = np.ascontiguousarray(solver.grid.x_grid, dtype=np.float64)
    sig = np.ascontiguousarray(np.sqrt(solver.grid.s2_grid), dtype=np.float64)
    pi = solver.stationary

    dg = p.dividends["growth"]
    dv = p.dividends["value"]
    dm = p.dividends["market"]

    (E_Rf_inv, E_Rg, E_Rv, E_Rm,
     E_Rg2, E_Rv2, E_Rm2, E_Rg_Rm, E_Rv_Rm) = _accumulate_moments(
        z_c, z_g, z_v, z_m, Pi, x, sig,
        float(p.cons.mu),
        float(dg.mu), float(dg.phi), float(dg.phi_sigma), float(dg.alpha),
        float(dv.mu), float(dv.phi), float(dv.phi_sigma), float(dv.alpha),
        float(dm.mu), float(dm.phi), float(dm.phi_sigma), float(dm.alpha),
        float(solver.delta), float(solver.theta), float(solver.psi),
        solver.eta_nodes, solver.eta_weights
    )

    # Unconditional moments via the stationary distribution
    e_rf_inv = float(np.dot(pi, E_Rf_inv))
    Rf = 1.0 / e_rf_inv if e_rf_inv > 1e-18 else np.inf
    Rg = np.dot(pi, E_Rg)
    Rv = np.dot(pi, E_Rv)
    Rm = np.dot(pi, E_Rm)

    # Annualise (monthly → annual)
    mean_Rg = (Rg ** 12 - 1) * 100
    mean_Rv = (Rv ** 12 - 1) * 100
    mean_Rm = (Rm ** 12 - 1) * 100
    mean_Rf = (Rf ** 12 - 1) * 100

    value_premium = mean_Rv - mean_Rg

    # Approximate volatilities and betas (simplified)
    vol_g = np.sqrt(max(np.dot(pi, E_Rg2) - Rg**2, 0)) * np.sqrt(12) * 100
    vol_v = np.sqrt(max(np.dot(pi, E_Rv2) - Rv**2, 0)) * np.sqrt(12) * 100
    vol_m = np.sqrt(max(np.dot(pi, E_Rm2) - Rm**2, 0)) * np.sqrt(12) * 100

    # CAPM betas (cov / var)
    cov_gm = np.dot(pi, E_Rg_Rm) - Rg * Rm
    cov_vm = np.dot(pi, E_Rv_Rm) - Rv * Rm
    var_m = max(np.dot(pi, E_Rm2) - Rm**2, 1e-12)
    beta_g = cov_gm / var_m
    beta_v = cov_vm / var_m

    mean_pd = {
        "growth": float(np.dot(pi, z_g)),
        "value":  float(np.dot(pi, z_v)),
        "market": float(np.dot(pi, z_m)),
    }

    return {
        "mean_return": {"growth": mean_Rg, "value": mean_Rv, "market": mean_Rm},
        "mean_rf": mean_Rf,
        "value_premium": value_premium,
        "volatility": {"growth": vol_g, "value": vol_v, "market": vol_m},
        "sharpe": {
            "growth": (mean_Rg - mean_Rf) / vol_g if vol_g > 0 else np.nan,
            "value":  (mean_Rv - mean_Rf) / vol_v if vol_v > 0 else np.nan,
            "market": (mean_Rm - mean_Rf) / vol_m if vol_m > 0 else np.nan,
        },
        "capm_beta": {"growth": beta_g, "value": beta_v},
        "mean_log_pd": mean_pd,
        "log_pd_value_minus_growth": mean_pd["value"] - mean_pd["growth"],
    }


def print_asset_pricing_moments(moments: dict) -> None:
    """Pretty-print the asset-pricing moments in the style of Tables VII–X."""
    print("=" * 60)
    print("Asset-pricing moments (annualised)")
    print("=" * 60)
    print(f"Risk-free rate          : {moments['mean_rf']:6.2f} %")
    print(f"Value premium           : {moments['value_premium']:6.2f} %")
    print()
    print(f"{'Portfolio':12s} {'E[R] %':>8s} {'Vol %':>8s} {'Sharpe':>8s} {'CAPM β':>8s} {'log(P/D)':>9s}")
    print("-" * 60)
    for name in ("growth", "value", "market"):
        er = moments["mean_return"][name]
        vol = moments["volatility"][name]
        sh = moments["sharpe"][name]
        beta = moments["capm_beta"].get(name, np.nan)
        pd = moments["mean_log_pd"][name]
        print(f"{name:12s} {er:8.2f} {vol:8.2f} {sh:8.2f} {beta:8.2f} {pd:9.2f}")
    print()
    print(f"log(P/D) Value − Growth : {moments['log_pd_value_minus_growth']:6.2f}")
