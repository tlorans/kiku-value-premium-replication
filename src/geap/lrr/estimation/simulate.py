"""Simulate decision-frequency paths and time-aggregate them to annual."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .solution import BKYParams, solve_loglinear


def simulate_annual(
    params: BKYParams,
    h: int,
    years: int,
    *,
    seed: int = 0,
    burn_in: int = 50,
) -> pd.DataFrame:
    """Annual ``dc, dd, rm, log_pd, rf`` from a monthly (decision-frequency) path.

    Consumption and dividends are aggregated by summing levels within
    each year of ``h`` periods, matching the paper's time-aggregation
    convention.
    """
    rng = np.random.default_rng(seed)
    sol = solve_loglinear(params)
    n = (years + burn_in) * h
    x = np.zeros(n + 1)
    s2 = np.full(n + 1, params.sigma**2)
    dc = np.zeros(n)
    dd = np.zeros(n)
    eta = rng.standard_normal(n)
    e = rng.standard_normal(n)
    w = rng.standard_normal(n)
    u = params.rho_d * eta + np.sqrt(max(1.0 - params.rho_d**2, 0.0)) * rng.standard_normal(n)
    for t in range(n):
        sig = np.sqrt(max(s2[t], 1e-16))
        dc[t] = params.mu_c + x[t] + sig * eta[t]
        dd[t] = params.mu_d + params.phi_d * x[t] + params.phi_d_sigma * sig * u[t]
        x[t + 1] = params.rho * x[t] + params.phi_e * sig * e[t]
        s2[t + 1] = (
            params.sigma**2 * (1.0 - params.nu)
            + params.nu * s2[t]
            + params.sigma_w * w[t]
        )
        s2[t + 1] = max(s2[t + 1], 1e-10)
    # Drop burn-in.
    start = burn_in * h
    dc = dc[start:]
    dd = dd[start:]
    x = x[start : start + years * h]
    s2 = s2[start : start + years * h]
    # Level aggregation.
    c = np.exp(np.cumsum(dc))
    d = np.exp(np.cumsum(dd))
    rows = []
    for y in range(years):
        sl = slice(y * h, (y + 1) * h)
        c_year = c[sl].sum()
        d_year = d[sl].sum()
        if y == 0:
            dc_a = np.nan
            dd_a = np.nan
            c_prev = c_year
            d_prev = d_year
        else:
            dc_a = float(np.log(c_year / c_prev))
            dd_a = float(np.log(d_year / d_prev))
            c_prev = c_year
            d_prev = d_year
        z_m = sol.A_d0 + sol.A_d1 * x[sl][-1] + sol.A_d2 * s2[sl][-1]
        rf_a = float(np.sum(sol.F[0] + sol.F[1] * x[sl] + sol.F[2] * s2[sl]))
        rd_a = float(
            np.sum(
                sol.B_d[0]
                + sol.B_d[1] * x[sl]
                + sol.B_d[2] * s2[sl]
            )
        )
        rows.append(
            {
                "year": y + 1,
                "dc": dc_a,
                "dd": dd_a,
                "rm": rd_a,
                "log_pd": float(z_m - np.log(h) - 0.5 * params.mu_d * (h - 1)),
                "rf": rf_a,
            }
        )
    return pd.DataFrame(rows).iloc[1:].reset_index(drop=True)


def simulate_claim_returns(
    claims: dict[str, BKYParams],
    h: int,
    years: int,
    *,
    seed: int = 0,
    burn_in: int = 40,
) -> dict[str, np.ndarray]:
    """Annual log returns for several claims that share (x, σ², η, e, w)."""
    rng = np.random.default_rng(seed)
    market = next(iter(claims.values()))
    n = (years + burn_in) * h
    x = np.zeros(n + 1)
    s2 = np.full(n + 1, market.sigma**2)
    eta = rng.standard_normal(n)
    e = rng.standard_normal(n)
    w = rng.standard_normal(n)
    sols = {name: solve_loglinear(p) for name, p in claims.items()}
    own = {
        name: p.rho_d * eta
        + np.sqrt(max(1.0 - p.rho_d**2, 0.0)) * rng.standard_normal(n)
        for name, p in claims.items()
    }
    for t in range(n):
        sig = np.sqrt(max(s2[t], 1e-16))
        x[t + 1] = market.rho * x[t] + market.phi_e * sig * e[t]
        s2[t + 1] = (
            market.sigma**2 * (1.0 - market.nu)
            + market.nu * s2[t]
            + market.sigma_w * w[t]
        )
        s2[t + 1] = max(s2[t + 1], 1e-10)
    start = burn_in * h
    x = x[start : start + years * h]
    s2 = s2[start : start + years * h]
    e = e[start : start + years * h]
    w = w[start : start + years * h]
    eta = eta[start : start + years * h]
    out: dict[str, np.ndarray] = {}
    rf = np.empty(years)
    for y in range(years):
        sl = slice(y * h, (y + 1) * h)
        rf[y] = float(np.sum(sols[next(iter(sols))].F[0] + sols[next(iter(sols))].F[1] * x[sl] + sols[next(iter(sols))].F[2] * s2[sl]))
    out["rf"] = rf
    for name, p in claims.items():
        sol = sols[name]
        bu, be, bw = sol.beta_d
        u = own[name][start : start + years * h]
        r = np.empty(years)
        for y in range(years):
            sl = slice(y * h, (y + 1) * h)
            sig = np.sqrt(np.maximum(s2[sl], 1e-16))
            r[y] = float(
                np.sum(
                    sol.B_d[0]
                    + sol.B_d[1] * x[sl]
                    + sol.B_d[2] * s2[sl]
                    + bu * sig * u[sl]
                    + be * sig * e[sl]
                    + bw * p.sigma_w * w[sl]
                )
            )
        out[name] = r
    return out
