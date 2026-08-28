"""
Section 5 of Kiku (2006) – Asset pricing implications
=====================================================

Population moments of returns implied by a solved :class:`ModelSolver`,
computed state-by-state and averaged under the stationary distribution.

All Gaussian innovations (the short-run consumption shock η and each
claim's idiosyncratic dividend residual v) integrate in closed form, so
every expectation is a single matrix–vector product against the Markov
transition matrix. The full residual structure of dividends,

    u_a′ = α_a η′ + √(1 − α_a²) v_a′,     Corr(v_a′, v_b′) = ρ_ab,

enters both first and second moments; earlier versions dropped the
independent component √(1 − α²) v′, which dominates dividend volatility.

These are population *monthly* moments annualised geometrically. The
sample statistics of Table VII (1000 samples × 74 years, time-aggregated
to annual) come from :mod:`lrrcs.implications.simulation` instead.
"""
from __future__ import annotations
import numpy as np
from ..model.solver import ModelSolver
from ..model.legs import resolve_legs

_PAPER_RESIDUAL_PAIRS = {
    frozenset(("growth", "value")): "residual_corr_gv",
    frozenset(("growth", "market")): "residual_corr_gm",
    frozenset(("value", "market")): "residual_corr_vm",
}


def residual_correlation(params, name_a: str, name_b: str) -> float:
    """Correlation of the orthogonalised dividend residuals v_a, v_b."""
    if name_a == name_b:
        return 1.0
    attr = _PAPER_RESIDUAL_PAIRS.get(frozenset((name_a, name_b)))
    return float(getattr(params, attr)) if attr else 0.0


def _mean_return_by_state(solver: ModelSolver, name: str) -> np.ndarray:
    """E_i[R′] for one claim: E[e^{Δd′}] × Σ_j Π_ij (1 + e^{z_j}) / e^{z_i}."""
    d = solver.p.dividends[name]
    x = solver.grid.x_grid
    s2 = solver.grid.s2_grid
    z = solver.z[name]
    # Var(Δd′ | state) = φ_σ² σ² regardless of the α split of u′.
    drift = float(d.mu) + float(d.phi) * x + 0.5 * float(d.phi_sigma) ** 2 * s2
    payoff = solver.grid.Pi @ (1.0 + np.exp(z))
    return np.exp(drift) * payoff / np.exp(z)


def _second_moment_by_state(solver: ModelSolver, name_a: str,
                            name_b: str) -> np.ndarray:
    """E_i[R_a′ R_b′] with the full dividend covariance structure."""
    p = solver.p
    da, db = p.dividends[name_a], p.dividends[name_b]
    x = solver.grid.x_grid
    s2 = solver.grid.s2_grid
    za, zb = solver.z[name_a], solver.z[name_b]

    corr_u = (float(da.alpha) * float(db.alpha)
              + np.sqrt((1.0 - float(da.alpha) ** 2)
                        * (1.0 - float(db.alpha) ** 2))
              * residual_correlation(p, name_a, name_b))
    fa, fb = float(da.phi_sigma), float(db.phi_sigma)
    var_sum = fa * fa + fb * fb + 2.0 * fa * fb * corr_u

    drift = ((float(da.mu) + float(db.mu))
             + (float(da.phi) + float(db.phi)) * x
             + 0.5 * var_sum * s2)
    payoff = solver.grid.Pi @ ((1.0 + np.exp(za)) * (1.0 + np.exp(zb)))
    return np.exp(drift) * payoff / np.exp(za + zb)


def compute_asset_pricing_moments(
    solver: ModelSolver,
    long: str | None = None,
    short: str | None = None,
    market: str | None = None,
):
    """Moments for the long, short, and market claims of a solved model."""
    if not solver.converged or solver.z_c is None:
        raise RuntimeError("Call solver.solve() before computing moments.")

    p = solver.p
    long_key, short_key, market_key = resolve_legs(
        solver.z, long=long, short=short, market=market
    )
    if market_key is None:
        raise KeyError(
            "No market claim. Pass market='...' or include a series named 'market'."
        )

    pi = solver.stationary

    Rf_states = solver.risk_free()
    e_rf_inv = float(np.dot(pi, 1.0 / Rf_states))
    Rf = 1.0 / e_rf_inv

    E_R = {name: _mean_return_by_state(solver, name)
           for name in (short_key, long_key, market_key)}
    Rg = float(np.dot(pi, E_R[short_key]))
    Rv = float(np.dot(pi, E_R[long_key]))
    Rm = float(np.dot(pi, E_R[market_key]))

    mean_Rg = (Rg ** 12 - 1) * 100
    mean_Rv = (Rv ** 12 - 1) * 100
    mean_Rm = (Rm ** 12 - 1) * 100
    mean_Rf = (Rf ** 12 - 1) * 100
    value_premium = mean_Rv - mean_Rg

    E_R2 = {name: float(np.dot(pi, _second_moment_by_state(solver, name, name)))
            for name in (short_key, long_key, market_key)}
    vol_g = np.sqrt(max(E_R2[short_key] - Rg**2, 0)) * np.sqrt(12) * 100
    vol_v = np.sqrt(max(E_R2[long_key] - Rv**2, 0)) * np.sqrt(12) * 100
    vol_m = np.sqrt(max(E_R2[market_key] - Rm**2, 0)) * np.sqrt(12) * 100

    cov_gm = float(np.dot(pi, _second_moment_by_state(solver, short_key, market_key))) - Rg * Rm
    cov_vm = float(np.dot(pi, _second_moment_by_state(solver, long_key, market_key))) - Rv * Rm
    var_m = max(E_R2[market_key] - Rm**2, 1e-12)
    beta_g = cov_gm / var_m
    beta_v = cov_vm / var_m

    mean_pd = {
        short_key: float(np.dot(pi, solver.z[short_key])),
        long_key: float(np.dot(pi, solver.z[long_key])),
        market_key: float(np.dot(pi, solver.z[market_key])),
    }

    return {
        "mean_return": {short_key: mean_Rg, long_key: mean_Rv, market_key: mean_Rm},
        "mean_rf": mean_Rf,
        "value_premium": value_premium,
        "long_short_premium": value_premium,
        "long": long_key,
        "short": short_key,
        "market": market_key,
        "volatility": {short_key: vol_g, long_key: vol_v, market_key: vol_m},
        "sharpe": {
            short_key: (mean_Rg - mean_Rf) / vol_g if vol_g > 0 else np.nan,
            long_key: (mean_Rv - mean_Rf) / vol_v if vol_v > 0 else np.nan,
            market_key: (mean_Rm - mean_Rf) / vol_m if vol_m > 0 else np.nan,
        },
        "capm_beta": {short_key: beta_g, long_key: beta_v},
        "mean_log_pd": mean_pd,
        "log_pd_value_minus_growth": mean_pd[long_key] - mean_pd[short_key],
        "log_pd_long_minus_short": mean_pd[long_key] - mean_pd[short_key],
    }


def print_asset_pricing_moments(moments: dict) -> None:
    """Pretty-print the asset-pricing moments in the style of Tables VII–X."""
    long_key = moments.get("long", "value")
    short_key = moments.get("short", "growth")
    market_key = moments.get("market", "market")
    print("=" * 60)
    print("Asset-pricing moments (annualised)")
    print("=" * 60)
    print(f"Risk-free rate          : {moments['mean_rf']:6.2f} %")
    prem_label = (
        "Value premium"
        if {long_key, short_key} <= {"value", "growth"}
        else "Long-short premium"
    )
    print(f"{prem_label:23s}: {moments['value_premium']:6.2f} %")
    print()
    print(f"{'Portfolio':12s} {'E[R] %':>8s} {'Vol %':>8s} {'Sharpe':>8s} {'CAPM β':>8s} {'log(P/D)':>9s}")
    print("-" * 60)
    for name in (short_key, long_key, market_key):
        er = moments["mean_return"][name]
        vol = moments["volatility"][name]
        sh = moments["sharpe"][name]
        beta = moments["capm_beta"].get(name, float("nan"))
        pd = moments["mean_log_pd"][name]
        print(f"{name:12s} {er:8.2f} {vol:8.2f} {sh:8.2f} {beta:8.2f} {pd:9.2f}")
    print()
    print(f"log(P/D) {long_key} − {short_key} : {moments['log_pd_value_minus_growth']:6.2f}")
