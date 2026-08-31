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
    """Correlation of the orthogonalised dividend residuals v_a, v_b.

    Pairs listed in ``params.residual_corr`` win; otherwise the paper's
    three portfolios use their ``residual_corr_*`` attributes and any
    other pair is uncorrelated.
    """
    if name_a == name_b:
        return 1.0
    pair = frozenset((name_a, name_b))
    custom = getattr(params, "residual_corr", None)
    if custom and pair in custom:
        return float(custom[pair])
    attr = _PAPER_RESIDUAL_PAIRS.get(pair)
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


def claim_stats(solver: ModelSolver, name: str, pi: np.ndarray) -> dict:
    """Annualized mean return, volatility, and mean log P/D for one claim.

    ``gross`` and ``second`` are the underlying monthly gross-return
    moments; the annualized figures are in percent.
    """
    R = float(np.dot(pi, _mean_return_by_state(solver, name)))
    R2 = float(np.dot(pi, _second_moment_by_state(solver, name, name)))
    return {
        "gross": R,
        "second": R2,
        "mean_return": (R ** 12 - 1) * 100,
        "volatility": np.sqrt(max(R2 - R**2, 0)) * np.sqrt(12) * 100,
        "mean_log_pd": float(np.dot(pi, solver.z[name])),
    }


def compute_asset_pricing_moments(
    solver: ModelSolver,
    long: str | None = None,
    short: str | None = None,
    market: str | None = None,
):
    """Moments for the long, short, and market claims of a solved model.

    Notes
    -----
    Internal engine behind ``LongRunRisksModel.solve()``; the results
    object presents these numbers as attributes.
    """
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

    stats = {name: claim_stats(solver, name, pi)
             for name in (short_key, long_key, market_key)}
    Rg = stats[short_key]["gross"]
    Rv = stats[long_key]["gross"]
    Rm = stats[market_key]["gross"]

    mean_Rg = stats[short_key]["mean_return"]
    mean_Rv = stats[long_key]["mean_return"]
    mean_Rm = stats[market_key]["mean_return"]
    mean_Rf = (Rf ** 12 - 1) * 100
    value_premium = mean_Rv - mean_Rg

    E_R2 = {name: stat["second"] for name, stat in stats.items()}
    vol_g = stats[short_key]["volatility"]
    vol_v = stats[long_key]["volatility"]
    vol_m = stats[market_key]["volatility"]

    cov_gm = float(np.dot(pi, _second_moment_by_state(solver, short_key, market_key))) - Rg * Rm
    cov_vm = float(np.dot(pi, _second_moment_by_state(solver, long_key, market_key))) - Rv * Rm
    var_m = max(E_R2[market_key] - Rm**2, 1e-12)
    beta_g = cov_gm / var_m
    beta_v = cov_vm / var_m

    mean_pd = {name: stat["mean_log_pd"] for name, stat in stats.items()}

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

