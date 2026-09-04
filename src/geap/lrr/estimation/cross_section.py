"""Table 7: size and book-to-market claims at the Table 2 states."""
from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd
from scipy.optimize import minimize

from .aggregation import _flow_loadings, model_moments
from .data import load_annual
from .goldens import (
    TABLE_2_LRR,
    TABLE_2_LRR_H,
    TABLE_7_MU,
    TABLE_7_PHI,
    TABLE_7_PHI_SIGMA,
    TABLE_7_RHO,
)
from .solution import BKYParams, solve_loglinear
from .states import extract_states

_CLAIM_NAMES = ("small", "large", "growth", "value")
_CLAIM_MOMENTS = (
    "mean_dd",
    "vol_dd",
    "corr_dc_dd",
    "mean_excess",
    "vol_rd",
    "mean_zd",
    "vol_zd",
)
# vol_dd is noisy on the small and value legs. Mean P/D and the premium
# identify long-run leverage φ_j; E[u] and E[u x] use market-extracted x.
_CLAIM_WEIGHTS = {
    "vol_dd": 0.2,
    "corr_dc_dd": 1.5,
    "mean_excess": 3.0,
    "mean_zd": 3.0,
    "vol_zd": 1.5,
}
_CLAIM_BOUNDS = (
    (0.0, 0.02),
    (0.5, 20.0),
    (0.5, 20.0),
    (0.0, 0.90),
)


def table7_claims(market: BKYParams | None = None) -> dict[str, BKYParams]:
    """Market preferences and consumption, portfolio-specific cash-flows."""
    market = market or TABLE_2_LRR
    out = {}
    for name in _CLAIM_NAMES:
        out[name] = replace(
            market,
            mu_d=TABLE_7_MU[name],
            phi_d=TABLE_7_PHI[name],
            phi_d_sigma=TABLE_7_PHI_SIGMA[name],
            rho_d=TABLE_7_RHO[name],
        )
    return out


def _period_premium(p: BKYParams) -> float:
    sol = solve_loglinear(p)
    lam = sol.Lambda
    _bu, be, bw = sol.beta_d
    b_eta = p.phi_d_sigma * p.rho_d
    return float(
        lam[0] * p.sigma**2 * b_eta
        + lam[1] * p.sigma**2 * be
        + lam[2] * p.sigma_w**2 * bw
    )


def table7_premia(
    market: BKYParams | None = None,
    h: int = TABLE_2_LRR_H,
    *,
    claims: dict[str, BKYParams] | None = None,
) -> dict[str, float]:
    """Model risk premia in annual percent."""
    claims = claims if claims is not None else table7_claims(market)
    return {name: 100.0 * h * _period_premium(p) for name, p in claims.items()}


def table7_capm(
    market: BKYParams | None = None,
    h: int = TABLE_2_LRR_H,
    *,
    years: int = 2000,
    seed: int = 0,
) -> dict[str, dict[str, float]]:
    """Model CAPM beta and alpha (%) of small–large and value–growth."""
    from .simulate import simulate_claim_returns

    market = market or TABLE_2_LRR
    claims = table7_claims(market)
    claims["market"] = market
    rets = simulate_claim_returns(claims, h, years=years, seed=seed)
    rf = rets["rf"]
    rm = rets["market"] - rf
    prem = table7_premia(market, h)
    mkt_prem = 100.0 * h * _period_premium(market)
    out = {}
    for spread, long, short in (
        ("small_large", "small", "large"),
        ("value_growth", "value", "growth"),
    ):
        y = (rets[long] - rets[short]) * 100.0
        x = rm * 100.0
        xd = x - x.mean()
        yd = y - y.mean()
        beta = float(np.dot(xd, yd) / np.dot(xd, xd))
        alpha = float((prem[long] - prem[short]) - beta * mkt_prem)
        out[spread] = {"beta_model": beta, "alpha_model": alpha}
    return out


def cross_section_sample(panel: pd.DataFrame) -> pd.DataFrame:
    """Mean return, dividend growth, and log P/D by claim."""
    rows = []
    for claim, g in panel.groupby("claim"):
        rows.append(
            {
                "claim": claim,
                "ret_mean": float(np.nanmean(g["ret"]) * 100.0),
                "dg_mean": float(np.nanmean(g["dgrowth"]) * 100.0),
                "log_pd": float(np.nanmean(np.log(g["pd"].to_numpy(dtype=float)))),
            }
        )
    return pd.DataFrame(rows)


def table7_sample_premia(panel: pd.DataFrame) -> dict[str, float]:
    """Mean annual percent return by claim."""
    out: dict[str, float] = {}
    for claim, g in panel.groupby("claim"):
        out[str(claim)] = float(np.nanmean(g["ret"]) * 100.0)
    return out


def table7_sample_capm(
    panel: pd.DataFrame, market_annual: pd.DataFrame
) -> dict[str, dict[str, float]]:
    """Sample CAPM beta and alpha (%) of small–large and value–growth."""
    wide = panel.pivot(index="year", columns="claim", values="ret")
    mkt = market_annual.set_index("year")
    common = wide.index.intersection(mkt.index)
    rm_ex = (mkt.loc[common, "rm"] - mkt.loc[common, "rf"]).to_numpy(dtype=float)
    out: dict[str, dict[str, float]] = {}
    for spread, long, short in (
        ("small_large", "small", "large"),
        ("value_growth", "value", "growth"),
    ):
        y = (wide.loc[common, long] - wide.loc[common, short]).to_numpy(dtype=float)
        xd = rm_ex - rm_ex.mean()
        yd = y - y.mean()
        beta = float(np.dot(xd, yd) / np.dot(xd, xd))
        alpha = float((y.mean() - beta * rm_ex.mean()) * 100.0)
        out[spread] = {"beta_data": beta, "alpha_data": alpha}
    return out


def _align_claim(
    panel: pd.DataFrame, name: str, years: np.ndarray
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    g = panel.loc[panel["claim"] == name].set_index("year").reindex(years)
    dd = g["dgrowth"].to_numpy(dtype=float)
    ret = g["ret"].to_numpy(dtype=float)
    pd_raw = g["pd"].to_numpy(dtype=float)
    z = np.log(np.clip(pd_raw, 1e-8, None))
    return dd, ret, z


def _claim_targets(
    dd: np.ndarray, ret: np.ndarray, z: np.ndarray, dc: np.ndarray, rf: np.ndarray
) -> dict[str, float]:
    ok = np.isfinite(dd) & np.isfinite(dc)
    okz = np.isfinite(z)
    okr = np.isfinite(ret)
    return {
        "mean_dd": float(np.nanmean(dd)),
        "vol_dd": float(np.nanstd(dd[np.isfinite(dd)], ddof=1)),
        "corr_dc_dd": float(np.corrcoef(dc[ok], dd[ok])[0, 1]) if ok.sum() > 2 else 0.0,
        "mean_excess": float(np.nanmean(ret - rf)),
        "vol_rd": float(np.nanstd(ret[okr], ddof=1)),
        "mean_zd": float(np.nanmean(z)),
        "vol_zd": float(np.nanstd(z[okz], ddof=1)),
    }


def _unpack_claim(theta: np.ndarray, market: BKYParams) -> BKYParams:
    return replace(
        market,
        mu_d=float(theta[0]),
        phi_d=float(theta[1]),
        phi_d_sigma=float(theta[2]),
        rho_d=float(theta[3]),
    )


def _claim_sse(
    theta: np.ndarray,
    *,
    market: BKYParams,
    h: int,
    target: dict[str, float],
    dd: np.ndarray,
    x: np.ndarray,
) -> float:
    p = _unpack_claim(theta, market)
    try:
        model = model_moments(p, h)
    except Exception:
        return 1e6
    sse = 0.0
    for key in _CLAIM_MOMENTS:
        scale = max(abs(target[key]), 0.01)
        weight = _CLAIM_WEIGHTS.get(key, 1.0)
        sse += weight * ((model[key] - target[key]) / scale) ** 2
    y_x, _, _ = _flow_loadings(
        h, p.rho, p.phi_e, p.sigma, p.phi_d, p.phi_d_sigma
    )
    u = dd[2:] - p.mu_d * h - y_x * x[:-2]
    ok = np.isfinite(u) & np.isfinite(x[:-2])
    if ok.any():
        sse += 2.0 * (float(np.nanmean(u[ok])) / 0.05) ** 2
        sse += 2.0 * (float(np.nanmean(u[ok] * x[:-2][ok])) / 0.0005) ** 2
    return float(sse)


def estimate_table7_claims(
    panel: pd.DataFrame,
    market_params: BKYParams | None = None,
    h: int = 11,
) -> dict[str, BKYParams]:
    """Second-stage cash-flow estimates for size and B/M claims.

    Preferences, consumption, and the market cash-flow vector stay at
    ``market_params``. States are extracted from the market annual
    ``log_pd`` and ``rf``. Each claim's ``(μ_j, φ_j, ϕ_j, ρ_j)`` starts
    at the market's ``(μ_d, φ_d, ϕ_d, ρ_d)``.
    """
    market = market_params or TABLE_2_LRR
    annual = load_annual().set_index("year")
    sol = solve_loglinear(market)
    states = extract_states(
        annual["log_pd"].to_numpy(dtype=float),
        annual["rf"].to_numpy(dtype=float),
        sol,
        params=market,
        h=h,
    )
    years = annual.index.to_numpy()
    dc = annual["dc"].to_numpy(dtype=float)
    rf = annual["rf"].to_numpy(dtype=float)
    start = np.array(
        [market.mu_d, market.phi_d, market.phi_d_sigma, market.rho_d],
        dtype=float,
    )
    out: dict[str, BKYParams] = {}
    for name in _CLAIM_NAMES:
        dd, ret, z = _align_claim(panel, name, years)
        target = _claim_targets(dd, ret, z, dc, rf)

        def objective(theta, _dd=dd, _target=target):
            return _claim_sse(
                theta, market=market, h=h, target=_target, dd=_dd, x=states.x
            )

        res = minimize(
            objective,
            start,
            method="L-BFGS-B",
            bounds=list(_CLAIM_BOUNDS),
            options={"maxiter": 400, "ftol": 1e-12},
        )
        out[name] = _unpack_claim(res.x, market)
    return out
