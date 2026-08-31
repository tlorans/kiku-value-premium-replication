"""
Table VII of Kiku (2006) – sample statistics by simulation
==========================================================

The paper's model column is not a population moment: it is the average,
across 1000 artificial samples, of statistics estimated on 74 years of
annual data, each year aggregated from 12 simulated months. This module
reproduces that object exactly:

1. simulate the *discretized* economy — the Markov chain over (x, σ²)
   that the Tauchen–Hussey solution actually prices — at a monthly
   frequency, drawing the continuous Gaussian innovations η and v for
   realized consumption and dividend growth,
2. read prices off the solved valuation functions z(x, σ²) state by
   state (no interpolation: the chain is the model),
3. compound monthly returns to annual, aggregate dividends within the
   year (annual P/D = year-end price over the year's dividends),
4. estimate the Table VII statistics on each 74-year sample,
5. report the cross-sample mean and standard deviation.

Annual CAPM betas — the source of the paper's β_Value/β_Growth = 0.92 —
are OLS slopes of annual excess returns on the annual market excess
return, sample by sample.
"""
from __future__ import annotations
import numpy as np
from ..model.solver import ModelSolver
from ..model.legs import resolve_legs
from .moments import residual_correlation


def simulate_table_vii(
    solver: ModelSolver | None = None,
    n_samples: int = 1000,
    years: int = 74,
    seed: int = 0,
    burn_in_years: int = 5,
    long: str | None = None,
    short: str | None = None,
    market: str | None = None,
) -> dict:
    """Model-implied Table VII: cross-sample means (and SDs) of annual stats.

    Parameters
    ----------
    solver : ModelSolver, optional
        A solved model. Defaults to the Table II calibration on the
        paper grid (30 × 4), solved on the spot.
    n_samples, years : int
        Number of artificial samples and their length in years
        (paper: 1000 × 74).
    seed : int
        Seed of the random generator (one stream for all samples).
    burn_in_years : int
        Extra initial years discarded so states start near the
        stationary distribution.

    Returns
    -------
    dict with, per claim, the cross-sample mean of: annual expected
    return ``mean_return`` (%), return volatility ``volatility`` (%),
    ``sharpe``, annual CAPM beta ``capm_beta``, annual mean P/D level
    ``mean_pd_level`` and mean log P/D ``mean_log_pd``; the risk-free
    rate ``mean_rf`` (%); the value (long-short) premium; the beta
    ratio ``beta_ratio``; and ``*_se`` entries holding cross-sample
    standard deviations of the return means.

    Notes
    -----
    Internal engine behind ``LongRunRisksModel.simulate()``; the results
    object presents these numbers as attributes.
    """
    if solver is None:
        solver = ModelSolver().solve()
    if not solver.converged:
        raise RuntimeError("Call solver.solve() before simulating.")

    p = solver.p
    long_key, short_key, market_key = resolve_legs(
        solver.z, long=long, short=short, market=market
    )
    if market_key is None:
        raise KeyError(
            "No market claim. Pass market='...' or include a series named 'market'."
        )
    names = list(solver.z)
    g = solver.grid
    rng = np.random.default_rng(seed)

    n_assets = len(names)
    corr = np.eye(n_assets)
    for a in range(n_assets):
        for b in range(a + 1, n_assets):
            corr[a, b] = corr[b, a] = residual_correlation(p, names[a], names[b])
    chol_v = np.linalg.cholesky(corr)

    alphas = np.array([p.dividends[nm].alpha for nm in names])
    resid_scale = np.sqrt(np.maximum(1.0 - alphas**2, 0.0))
    mus = np.array([p.dividends[nm].mu for nm in names])
    phis = np.array([p.dividends[nm].phi for nm in names])
    phi_sigmas = np.array([p.dividends[nm].phi_sigma for nm in names])

    T = (years + burn_in_years) * 12
    burn = burn_in_years * 12
    S = n_samples

    # per-state pricing objects (the chain is the model — no interpolation)
    z_states = {nm: np.asarray(solver.z[nm]) for nm in names}
    log_rf_states = np.log(solver.risk_free())
    x_states = g.x_grid
    sig_states = np.sqrt(g.s2_grid)
    cum_Pi = np.cumsum(g.Pi, axis=1)
    cum_Pi[:, -1] = 1.0  # guard against rounding

    # --- simulate the Markov chain, vectorised across samples --------------
    stationary = solver.stationary
    state = np.searchsorted(np.cumsum(stationary), rng.random(S))
    state = np.minimum(state, g.n_states - 1)

    n_keep = years * 12
    monthly_R = {nm: np.empty((n_keep, S)) for nm in names}
    monthly_rf = np.empty((n_keep, S))
    monthly_logD = {nm: np.empty((n_keep, S)) for nm in names}
    monthly_z = {nm: np.empty((n_keep, S)) for nm in names}
    # dividend levels per asset (monthly units); prices follow as D·e^z
    log_D = {nm: np.zeros(S) for nm in names}

    for t in range(T):
        eta = rng.standard_normal(S)
        v = rng.standard_normal((S, n_assets)) @ chol_v.T
        u = alphas[None, :] * eta[:, None] + resid_scale[None, :] * v

        x_now = x_states[state]
        sig_now = sig_states[state]
        state_next = (cum_Pi[state] < rng.random(S)[:, None]).sum(axis=1)

        k = t - burn
        for a, nm in enumerate(names):
            dd = mus[a] + phis[a] * x_now + phi_sigmas[a] * sig_now * u[:, a]
            log_D[nm] = log_D[nm] + dd
            if k >= 0:
                z_next = z_states[nm][state_next]
                monthly_R[nm][k] = np.exp(
                    dd + np.logaddexp(0.0, z_next) - z_states[nm][state]
                )
                monthly_logD[nm][k] = log_D[nm]
                monthly_z[nm][k] = z_next
        if k >= 0:
            monthly_rf[k] = np.exp(log_rf_states[state])

        state = state_next

    # --- aggregate to annual ----------------------------------------------
    def annual_gross(monthly):
        return np.exp(
            np.log(monthly).reshape(years, 12, S).sum(axis=1)
        )

    ann_R = {nm: annual_gross(monthly_R[nm]) for nm in names}
    ann_rf = annual_gross(monthly_rf)

    ann_pd = {}
    for nm in names:
        lD = monthly_logD[nm].reshape(years, 12, S)
        zz = monthly_z[nm].reshape(years, 12, S)
        # year-end price over the year's total dividends
        price_end = np.exp(lD[:, -1, :] + zz[:, -1, :])
        div_year = np.exp(lD).sum(axis=1)
        ann_pd[nm] = price_end / div_year

    # --- per-sample statistics --------------------------------------------
    stats_mean = {nm: (ann_R[nm] - 1.0).mean(axis=0) * 100 for nm in names}
    stats_vol = {nm: (ann_R[nm] - 1.0).std(axis=0, ddof=1) * 100 for nm in names}
    rf_mean = (ann_rf - 1.0).mean(axis=0) * 100

    excess = {nm: (ann_R[nm] - ann_rf) for nm in names}
    stats_sharpe = {
        nm: (excess[nm].mean(axis=0) / excess[nm].std(axis=0, ddof=1) if years > 1
             else np.full(S, np.nan))
        for nm in names
    }

    ex_m = excess[market_key]
    ex_m_dev = ex_m - ex_m.mean(axis=0)
    var_m = (ex_m_dev**2).mean(axis=0)
    betas = {}
    for nm in names:
        ex_a = excess[nm]
        cov = (ex_m_dev * (ex_a - ex_a.mean(axis=0))).mean(axis=0)
        betas[nm] = cov / var_m

    pd_mean = {nm: ann_pd[nm].mean(axis=0) for nm in names}
    log_pd_mean = {nm: np.log(ann_pd[nm]).mean(axis=0) for nm in names}

    def cross(d):
        return {nm: float(np.mean(d[nm])) for nm in d}

    def cross_sd(d):
        if n_samples < 2:
            return {nm: float("nan") for nm in d}
        return {nm: float(np.std(d[nm], ddof=1)) for nm in d}

    out = {
        "n_samples": n_samples,
        "years": years,
        "long": long_key,
        "short": short_key,
        "market": market_key,
        "mean_return": cross(stats_mean),
        "mean_return_se": cross_sd(stats_mean),
        "volatility": cross(stats_vol),
        "volatility_se": cross_sd(stats_vol),
        "sharpe": cross(stats_sharpe),
        "mean_rf": float(np.mean(rf_mean)),
        "mean_rf_se": (float(np.std(rf_mean, ddof=1))
                       if n_samples > 1 else float("nan")),
        "capm_beta": cross(betas),
        "beta_ratio": float(np.mean(betas[long_key] / betas[short_key])),
        "mean_pd_level": cross(pd_mean),
        "mean_log_pd": cross(log_pd_mean),
        "mean_log_pd_se": cross_sd(log_pd_mean),
    }
    out["value_premium"] = out["mean_return"][long_key] - out["mean_return"][short_key]
    out["long_short_premium"] = out["value_premium"]
    return out

