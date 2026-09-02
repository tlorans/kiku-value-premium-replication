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
to annual) come from :mod:`geap.lrr.implications.simulation` instead.
"""
from __future__ import annotations
import numpy as np
from ..solver import ModelSolver

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
    d = solver.p.claims[name]
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
    da, db = p.claims[name_a], p.claims[name_b]
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


def population_moments(solver: ModelSolver) -> dict:
    """Population return moments for every claim of a solved model.

    Role free: this describes the claims, it does not decide which of
    them make a spread. Betas need a reference claim, so instead of
    picking one it returns the pairwise return covariance; the results
    object divides a column of it by that claim's variance.

    Returns
    -------
    dict
        ``mean_return``, ``volatility``, ``mean_log_pd`` and ``sharpe``
        per claim (annualized, percent); ``mean_rf``; and ``covariance``,
        a nested dict of monthly gross-return covariances.

    Notes
    -----
    Internal engine behind ``LongRunRisksModel.solve()``.
    """
    if not solver.converged or solver.z_c is None:
        raise RuntimeError("Call solver.solve() before computing moments.")

    pi = solver.stationary
    names = list(solver.z)

    Rf_states = solver.risk_free()
    e_rf_inv = float(np.dot(pi, 1.0 / Rf_states))
    Rf = 1.0 / e_rf_inv
    mean_Rf = (Rf ** 12 - 1) * 100

    stats = {name: claim_stats(solver, name, pi) for name in names}

    # Pairwise covariance of monthly gross returns. The diagonal repeats
    # claim_stats' own second moment, so a beta against claim m is
    # cov[a][m] / cov[m][m] -- the expression compute_asset_pricing_moments
    # used for its two legs, now available for every claim.
    covariance: dict[str, dict[str, float]] = {}
    for a in names:
        covariance[a] = {}
        for b in names:
            E_ab = float(np.dot(pi, _second_moment_by_state(solver, a, b)))
            covariance[a][b] = E_ab - stats[a]["gross"] * stats[b]["gross"]

    mean_return = {n: stats[n]["mean_return"] for n in names}
    volatility = {n: stats[n]["volatility"] for n in names}

    return {
        "claims": names,
        "mean_return": mean_return,
        "mean_rf": mean_Rf,
        "volatility": volatility,
        "sharpe": {
            n: (mean_return[n] - mean_Rf) / volatility[n]
            if volatility[n] > 0 else np.nan
            for n in names
        },
        "mean_log_pd": {n: stats[n]["mean_log_pd"] for n in names},
        "covariance": covariance,
    }
