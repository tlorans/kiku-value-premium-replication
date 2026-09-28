"""Table 7: size and book-to-market claims at the Table 2 states."""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd
from scipy.stats import chi2

from ...gmm import estimate
from ...gmm.weighting import hansen_j_general, invvar_weights, newey_west
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
from .solution import BKYParams, LogLinearSolution, solve_loglinear
from .states import extract_states

_CLAIM_NAMES = ("small", "large", "growth", "value")
# The paper's per-portfolio moment set (p. 66): mean and volatility of
# dividend growth, its correlation with consumption growth, the risk
# premium, return volatility, mean and volatility of the price-dividend
# ratio, and the market beta.
_CLAIM_MOMENTS = (
    "mean_dd",
    "vol_dd",
    "corr_dc_dd",
    "mean_excess",
    "vol_rd",
    "mean_zd",
    "vol_zd",
    "beta_mkt",
)
# Table 3's orthogonality conditions for the market, applied to the
# claim's own dividend residual u_j at the market-extracted x. Section
# 5.3 does not list them, so they are an option.
_CLAIM_ORTHOGONALITY = ("e_u", "e_u_x")
# Newey-West lags, as in the market estimation.
_CLAIM_HAC_LAGS = 1


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
    claims: dict[str, BKYParams] | None = None,
) -> dict[str, dict[str, float]]:
    """Model CAPM beta and alpha (%) of small–large and value–growth."""
    from .simulate import simulate_claim_returns

    market = market or TABLE_2_LRR
    claims = dict(claims) if claims is not None else table7_claims(market)
    claims["market"] = market
    rets = simulate_claim_returns(claims, h, years=years, seed=seed)
    rf = rets["rf"]
    rm = rets["market"] - rf
    prem = table7_premia(market, h, claims=claims)
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


def _sample_beta(y: np.ndarray, x: np.ndarray) -> float:
    ok = np.isfinite(y) & np.isfinite(x)
    if ok.sum() < 3:
        return float("nan")
    xd = x[ok] - x[ok].mean()
    yd = y[ok] - y[ok].mean()
    return float(np.dot(xd, yd) / np.dot(xd, xd))


def _claim_targets(
    dd: np.ndarray,
    ret: np.ndarray,
    z: np.ndarray,
    dc: np.ndarray,
    rf: np.ndarray,
    rm: np.ndarray | None = None,
) -> dict[str, float]:
    """Sample values of the section 5.3 moments, each on its own years.

    Table 3's definitions: the premium is the mean simple excess return
    E[R_j - R_f], and return volatility is that of the log return
    r_j = log R_j.
    """
    ok = np.isfinite(dd) & np.isfinite(dc)
    okz = np.isfinite(z)
    okr = np.isfinite(ret)
    out = {
        "mean_dd": float(np.nanmean(dd)),
        "vol_dd": float(np.nanstd(dd[np.isfinite(dd)], ddof=1)),
        "corr_dc_dd": float(np.corrcoef(dc[ok], dd[ok])[0, 1]) if ok.sum() > 2 else 0.0,
        "mean_excess": float(np.nanmean(ret - rf)),
        "vol_rd": float(np.std(np.log1p(ret[okr]), ddof=1)),
        "mean_zd": float(np.nanmean(z)),
        "vol_zd": float(np.nanstd(z[okz], ddof=1)),
    }
    if rm is not None:
        out["beta_mkt"] = _sample_beta(ret - rf, rm - rf)
    return out


def _model_beta(
    sol_j: LogLinearSolution,
    p_j: BKYParams,
    sol_m: LogLinearSolution,
    p_m: BKYParams,
    *,
    same_shock: bool = False,
) -> float:
    """Decision-frequency CAPM beta of claim ``j`` on the market claim.

    Returns load on the two states through ``B_d`` and on the three
    shocks through ``beta_d``; ``rho_d`` is the correlation of the
    claim's own dividend shock with the consumption shock. The ratio of
    covariance to market variance at the decision frequency is the
    moment the second stage targets; annual sums of iid innovations keep
    the same ratio.
    """
    var_x = p_m.phi_e**2 * p_m.sigma**2 / max(1.0 - p_m.rho**2, 1e-12)
    var_s = p_m.sigma_w**2 / max(1.0 - p_m.nu**2, 1e-12)
    s2 = p_m.sigma**2
    sw2 = p_m.sigma_w**2
    bu_j, be_j, bw_j = sol_j.beta_d
    bu_m, be_m, bw_m = sol_m.beta_d
    # Two claims' own dividend shocks are correlated only through the
    # consumption shock, so corr(u_j, u_m) = rho_j rho_m. ``same_shock``
    # is the market on itself, which shares one shock. This is a flag
    # rather than a parameter comparison so the objective stays smooth
    # when a claim starts at the market's cash-flow vector.
    corr_u = 1.0 if same_shock else p_j.rho_d * p_m.rho_d
    cov = (
        float(sol_j.B_d[1]) * float(sol_m.B_d[1]) * var_x
        + float(sol_j.B_d[2]) * float(sol_m.B_d[2]) * var_s
        + bu_j * bu_m * corr_u * s2
        + be_j * be_m * s2
        + bw_j * bw_m * sw2
    )
    var = (
        float(sol_m.B_d[1]) ** 2 * var_x
        + float(sol_m.B_d[2]) ** 2 * var_s
        + bu_m**2 * s2
        + be_m**2 * s2
        + bw_m**2 * sw2
    )
    return float(cov / var) if var > 0.0 else float("nan")


def _unpack_claim(theta: np.ndarray, market: BKYParams) -> BKYParams:
    return replace(
        market,
        mu_d=float(theta[0]),
        phi_d=float(theta[1]),
        phi_d_sigma=float(theta[2]),
        rho_d=float(theta[3]),
    )


# The optimiser sees (1e3 μ_j, φ_j, log ϕ_j, atanh ρ_j). These are the
# only bounds the model requires. ρ_j is a correlation, so |ρ_j| < 1.
# (ϕ_j, u_j, ρ_j) and (-ϕ_j, -u_j, -ρ_j) are one model, so ϕ_j > 0 is a
# sign normalisation. μ_j and φ_j are free.
def _to_opt(theta: np.ndarray) -> np.ndarray:
    mu, phi, vphi, rho = (float(v) for v in theta)
    rho = min(max(rho, -0.999999), 0.999999)
    return np.array([1e3 * mu, phi, np.log(max(vphi, 1e-8)), np.arctanh(rho)])


def _from_opt(t: np.ndarray) -> np.ndarray:
    t = np.asarray(t, dtype=float)
    return np.array([t[0] / 1e3, t[1], np.exp(t[2]), np.tanh(t[3])])


@dataclass
class ClaimMoments:
    """Observation-level eq. 31 moment conditions of one claim.

    Preferences, consumption, and the market cash-flow vector are held
    at ``market``, and ``x`` is the expected-growth state extracted from
    the market's price-dividend ratio and the risk-free rate. Each
    column of :meth:`conditions` has mean zero when the model moment
    equals its sample counterpart, following Table 3's definitions: the
    premium is E[R_j - R_f] in simple returns, and return volatility is
    that of the log return. The model premium is ``h`` times the
    per-period premium of the log-linear solution, which is how BKY
    print it (6.70 percent for the market at Table 2, and each Table 7
    model premium to within 0.06 at the printed vectors).

    ``common_years=True`` evaluates every moment on the years all its
    series are available. ``False`` evaluates each moment on its own
    years: its column is zero outside them and scaled by ``T / T_i``, so
    the column mean is the own-year mean.
    """

    name: str
    market: BKYParams
    h: int
    market_sol: LogLinearSolution
    dc: np.ndarray
    rf: np.ndarray
    rm: np.ndarray
    dd: np.ndarray
    ret: np.ndarray
    z: np.ndarray
    x_lag: np.ndarray
    keys: tuple[str, ...]
    common_years: bool = True

    def _masks(self) -> dict[str, np.ndarray]:
        f = np.isfinite
        dd = f(self.dd)
        ret = f(self.ret) & f(self.rf)
        z = f(self.z)
        u = dd & f(self.x_lag)
        masks = {
            "mean_dd": dd,
            "vol_dd": dd,
            "corr_dc_dd": dd & f(self.dc),
            "mean_excess": ret,
            "vol_rd": ret,
            "mean_zd": z,
            "vol_zd": z,
            "beta_mkt": ret & f(self.rm),
            "e_u": u,
            "e_u_x": u,
        }
        masks = {k: masks[k] for k in self.keys}
        if self.common_years:
            common = np.logical_and.reduce(list(masks.values()))
            masks = {k: common for k in masks}
        return masks

    @property
    def rows(self) -> np.ndarray:
        """Rows of the panel that :meth:`conditions` returns."""
        masks = self._masks()
        if self.common_years:
            return next(iter(masks.values()))
        return np.ones(self.dc.size, dtype=bool)

    def conditions(self, p: BKYParams) -> np.ndarray:
        sol = solve_loglinear(p)
        m = model_moments(p, self.h, sol=sol)
        vol_dc = model_moments(self.market, self.h, sol=self.market_sol)["vol_dc"]
        masks = self._masks()

        def mean_on(v: np.ndarray, key: str) -> float:
            return float(np.mean(v[masks[key]]))

        r = np.log1p(self.ret)
        re = self.ret - self.rf
        rme = self.rm - self.rf
        y_x, _, _ = _flow_loadings(self.h, p.rho, p.phi_e, p.sigma, p.phi_d, p.phi_d_sigma)
        u = self.dd - p.mu_d * self.h - y_x * self.x_lag
        cols: dict[str, np.ndarray] = {}
        for key in self.keys:
            if key == "mean_dd":
                col = self.dd - m["mean_dd"]
            elif key == "vol_dd":
                col = (self.dd - m["mean_dd"]) ** 2 - m["vol_dd"] ** 2
            elif key == "corr_dc_dd":
                col = (self.dc - mean_on(self.dc, key)) * (self.dd - mean_on(self.dd, key)) - (
                    m["corr_dc_dd"] * vol_dc * m["vol_dd"]
                )
            elif key == "mean_excess":
                col = re - m["mean_excess"]
            elif key == "vol_rd":
                col = (r - mean_on(r, key)) ** 2 - m["vol_rd"] ** 2
            elif key == "mean_zd":
                col = self.z - m["mean_zd"]
            elif key == "vol_zd":
                col = (self.z - m["mean_zd"]) ** 2 - m["vol_zd"] ** 2
            elif key == "beta_mkt":
                beta = _model_beta(sol, p, self.market_sol, self.market)
                dre = re - mean_on(re, key)
                drm = rme - mean_on(rme, key)
                col = dre * drm - beta * drm**2
            elif key == "e_u":
                col = u
            elif key == "e_u_x":
                col = u * self.x_lag
            else:
                raise KeyError(key)
            cols[key] = np.where(masks[key], col, np.nan)
        g = np.column_stack([cols[k] for k in self.keys])
        if self.common_years:
            return g[self.rows]
        n_own = np.array([masks[k].sum() for k in self.keys], dtype=float)
        return np.where(np.isfinite(g), g, 0.0) * (g.shape[0] / n_own)

    def criterion(self, p: BKYParams) -> tuple[float, np.ndarray, np.ndarray]:
        """Eq. 31 at ``p``: the objective, g_T, and the CUE weights there."""
        g = self.conditions(p)
        W = invvar_weights(g, lags=_CLAIM_HAC_LAGS)
        g_T = g.mean(axis=0)
        return float(g_T @ W @ g_T), g_T, W


def claim_moments(
    panel: pd.DataFrame,
    name: str,
    market_params: BKYParams | None = None,
    h: int = 11,
    *,
    orthogonality: bool = False,
    common_years: bool = True,
) -> ClaimMoments:
    """The eq. 31 moment conditions of one claim at the market states."""
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
    dd, ret, z = _align_claim(panel, name, years)
    # Annual dividend growth loads on x at the start of its two-year
    # window, as in the market's E[u].
    x_lag = np.full(years.size, np.nan)
    x_lag[2:] = states.x[:-2]
    keys = _CLAIM_MOMENTS + (_CLAIM_ORTHOGONALITY if orthogonality else ())
    return ClaimMoments(
        name=name,
        market=market,
        h=int(h),
        market_sol=sol,
        dc=annual["dc"].to_numpy(dtype=float),
        rf=annual["rf"].to_numpy(dtype=float),
        rm=annual["rm"].to_numpy(dtype=float),
        dd=dd,
        ret=ret,
        z=z,
        x_lag=x_lag,
        keys=keys,
        common_years=common_years,
    )


@dataclass
class ClaimFit:
    """Eq. 31 estimate of one claim's cash-flow vector."""

    name: str
    params: BKYParams
    moments: tuple[str, ...]
    nobs: int
    objective: float
    g: np.ndarray
    W: np.ndarray
    J: float
    J_df: int
    J_pvalue: float

    def contributions(self) -> dict[str, float]:
        """Each moment's term g_i^2 W_ii of the objective."""
        terms = self.g**2 * np.diag(self.W)
        return {k: float(v) for k, v in zip(self.moments, terms)}


def _claim_starts(market: BKYParams) -> list[np.ndarray]:
    """The market's cash-flow vector and three spread-out generic starts.

    None of them is a printed Table 7 vector.
    """
    mu = market.mu_d
    return [
        np.array([mu, market.phi_d, market.phi_d_sigma, market.rho_d]),
        np.array([mu, 2.0, 3.0, 0.2]),
        np.array([mu, 8.0, 8.0, 0.5]),
        np.array([mu, 12.0, 10.0, 0.2]),
    ]


def _hansen_j(cm: ClaimMoments, theta: np.ndarray) -> tuple[float, int, float]:
    """Hansen (1982) Lemma 4.2 J with a raw-parameter Jacobian."""
    p = _unpack_claim(theta, cm.market)
    g = cm.conditions(p)
    g_T = g.mean(axis=0)
    W = invvar_weights(g, lags=_CLAIM_HAC_LAGS)
    d = np.zeros((g_T.size, theta.size))
    for j in range(theta.size):
        step = 1e-5 * max(abs(float(theta[j])), 1e-3)
        bumped = np.array(theta, dtype=float)
        bumped[j] += step
        d[:, j] = (cm.conditions(_unpack_claim(bumped, cm.market)).mean(axis=0) - g_T) / step
    s = newey_west(g, lags=_CLAIM_HAC_LAGS)
    j_stat, j_df = hansen_j_general(g_T, d, W, s, int(g.shape[0]))
    return j_stat, j_df, float(chi2.sf(j_stat, j_df))


def fit_claim(cm: ClaimMoments, *, maxiter: int = 3000) -> ClaimFit:
    """Minimise eq. 31 for one claim from each start; the lowest wins."""
    n_rows = int(cm.rows.sum())
    k = len(cm.keys)
    penalty = np.ones((n_rows, k)) * 10.0 + (np.arange(n_rows) / max(n_rows, 1))[:, None]

    def moments(t):
        try:
            g = cm.conditions(_unpack_claim(_from_opt(t), cm.market))
        except Exception:
            return penalty
        return g if np.all(np.isfinite(g)) else penalty

    best = None
    for start in _claim_starts(cm.market):
        res = estimate(
            moments,
            _to_opt(start),
            W="cue_invvar",
            hac_lags=_CLAIM_HAC_LAGS,
            options={"maxiter": maxiter, "xatol": 1e-7, "fatol": 1e-12, "adaptive": True},
        )
        if best is None or res.objective < best.objective:
            best = res
    theta = _from_opt(best.theta)
    params = _unpack_claim(theta, cm.market)
    objective, g_T, W = cm.criterion(params)
    j_stat, j_df, j_p = _hansen_j(cm, theta)
    return ClaimFit(
        name=cm.name,
        params=params,
        moments=cm.keys,
        nobs=n_rows,
        objective=objective,
        g=g_T,
        W=W,
        J=j_stat,
        J_df=j_df,
        J_pvalue=j_p,
    )


def fit_table7_claims(
    panel: pd.DataFrame,
    market_params: BKYParams | None = None,
    h: int = 11,
    *,
    orthogonality: bool = False,
    common_years: bool = True,
) -> dict[str, ClaimFit]:
    """BKY eq. 31, claim by claim, at the market states (section 5.3).

    The moments are section 5.3's eight, with Table 3's definitions and
    time aggregation at ``h``. ``orthogonality=True`` adds E[u_j] and
    E[u_j x], and ``common_years=False`` evaluates each moment on its
    own years; see :class:`ClaimMoments`. The weighting matrix is the
    diagonal inverse of the Newey-West covariance of the moment
    conditions, updated continuously.
    """
    return {
        name: fit_claim(
            claim_moments(
                panel, name, market_params, h,
                orthogonality=orthogonality, common_years=common_years,
            )
        )
        for name in _CLAIM_NAMES
    }


def estimate_table7_claims(
    panel: pd.DataFrame,
    market_params: BKYParams | None = None,
    h: int = 11,
    *,
    orthogonality: bool = False,
    common_years: bool = True,
) -> dict[str, BKYParams]:
    """Second-stage cash-flow vectors of the size and B/M claims.

    The parameter vectors of :func:`fit_table7_claims`.
    """
    fits = fit_table7_claims(
        panel, market_params, h,
        orthogonality=orthogonality, common_years=common_years,
    )
    return {name: fit.params for name, fit in fits.items()}


def table7_contributions(
    panel: pd.DataFrame,
    claims: dict[str, BKYParams],
    market_params: BKYParams | None = None,
    h: int = 11,
    *,
    orthogonality: bool = False,
    common_years: bool = True,
) -> pd.DataFrame:
    """Eq. 31 at given cash-flow vectors, such as the printed Table 7 ones.

    One row per claim and moment: the moment condition g_i, its CUE
    weight W_ii, its term g_i^2 W_ii, and that term's share of the
    claim's objective.
    """
    rows = []
    for name, p in claims.items():
        cm = claim_moments(
            panel, name, market_params, h,
            orthogonality=orthogonality, common_years=common_years,
        )
        objective, g_T, W = cm.criterion(p)
        w = np.diag(W)
        for key, gi, wi in zip(cm.keys, g_T, w):
            term = float(gi**2 * wi)
            rows.append(
                {
                    "claim": name,
                    "moment": key,
                    "g": float(gi),
                    "w": float(wi),
                    "term": term,
                    "share": term / objective if objective > 0 else float("nan"),
                }
            )
    return pd.DataFrame(rows)


