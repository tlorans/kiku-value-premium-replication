"""GMM estimation of the LRR model with time aggregation (BKY 2016)."""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np
import pandas as pd
from scipy.optimize import minimize
from scipy.stats import chi2

from ...base import Summary
from ...gmm import GMMResults, estimate
from ...gmm.bootstrap import block_bootstrap
from ...gmm.weighting import newey_west
from ..model import LongRunRisksModel
from ..params import ClaimParams, ConsumptionParams, ModelParams, PreferencesParams
from .aggregation import model_moments
from .goldens import (
    COLD_START,
    TABLE_2_LRR,
    TABLE_2_LRR_H,
    TABLE_2_SE,
    TABLE_3_LRR_MODEL,
    TABLE_3_SAMPLE,
)
from .moments import MOMENT_NAMES, observation_moments
from .solution import BKYParams, solve_loglinear
from .states import extract_states

PARAM_NAMES = (
    "gamma",
    "psi",
    "delta",
    "mu_c",
    "rho",
    "phi_e",
    "sigma",
    "nu",
    "sigma_w",
    "mu_d",
    "phi_d",
    "phi_d_sigma",
    "rho_d",
)


def _pack(p: BKYParams) -> np.ndarray:
    return np.array([getattr(p, n) for n in PARAM_NAMES], dtype=float)


def _unpack(theta: np.ndarray, template: BKYParams) -> BKYParams:
    kw = {n: float(v) for n, v in zip(PARAM_NAMES, theta)}
    return BKYParams(**kw)


# L-BFGS sees O(1) coordinates. Raw (δ, σ_w) = (0.999, 2e-6) next to γ = 10
# is a badly scaled GMM problem. Index 2 is stored as 1-δ.
_SCALE = np.array(
    [10.0, 1.0, 1e3, 1e3, 1.0, 10.0, 100.0, 1.0, 1e6, 1e3, 5.0, 5.0, 1.0]
)


def _pack_scaled(p: BKYParams) -> np.ndarray:
    raw = _pack(p)
    raw[2] = 1.0 - raw[2]
    return raw * _SCALE


def _unpack_scaled(theta: np.ndarray, template: BKYParams) -> BKYParams:
    raw = np.asarray(theta, dtype=float) / _SCALE
    raw[2] = 1.0 - raw[2]
    return _unpack(raw, template)


def _unscale_se(se: np.ndarray, stochastic_vol: bool) -> np.ndarray:
    """Map GMM SEs from the scaled optimiser coordinates to raw parameters."""
    se = np.asarray(se, dtype=float).ravel()
    if stochastic_vol:
        if se.size != _SCALE.size:
            raise ValueError(
                f"expected {int(_SCALE.size)} scaled SEs, got {int(se.size)}"
            )
        return se / _SCALE
    full = np.zeros(len(PARAM_NAMES), dtype=float)
    j = 0
    for i, name in enumerate(PARAM_NAMES):
        if name in ("nu", "sigma_w"):
            continue
        full[i] = se[j] / _SCALE[i]
        j += 1
    if j != se.size:
        raise ValueError(f"expected {j} scaled SEs, got {int(se.size)}")
    return full


def _solvable(params: BKYParams) -> bool:
    try:
        solve_loglinear(params)
        return True
    except Exception:
        return False


def _samples_per_year(data: pd.DataFrame) -> int:
    """Annual panel is 1; a quarterly ``date`` index is 4."""
    if "date" in data.columns:
        years = pd.to_datetime(data["date"]).dt.year.to_numpy()
        n_years = max(int(np.unique(years).size), 1)
        return max(int(round(len(data) / n_years)), 1)
    return 1


def _rescale_from_monthly(
    start: BKYParams,
    h: int,
    mean_dc: float,
    samples_per_year: int = 1,
) -> BKYParams:
    """Map a monthly start onto ``h`` decisions per sampling interval."""
    freq = max(int(h) * max(int(samples_per_year), 1), 1)
    k = 12.0 / float(freq)
    sk = float(np.sqrt(k))
    return replace(
        start,
        mu_c=float(mean_dc) / float(h),
        mu_d=float(start.mu_d) * k,
        rho=float(start.rho) ** k,
        nu=float(start.nu) ** k,
        sigma=float(start.sigma) * sk,
        phi_e=float(start.phi_e) * sk,
        sigma_w=float(start.sigma_w) * sk,
        delta=float(start.delta) ** k,
    )


def _start_at_h(
    start: BKYParams,
    h: int,
    mean_dc: float,
    samples_per_year: int = 1,
) -> BKYParams:
    """``μ_c = mean(Δc)/h``. Rescale from monthly unless already ~monthly.

    Annual ``h≈11`` (one sample per year) stays on the unscaled Bansal–Yaron
    start so Table 2 CUE is unchanged. Quarterly data has four samples per
    year, so ``h=1`` is a quarterly decision (k=3), not an annual one (k=12).
    """
    freq = int(h) * max(int(samples_per_year), 1)
    p0 = replace(start, mu_c=float(mean_dc) / float(h))
    if abs(freq - 12) < 2 and _solvable(p0):
        return p0
    p1 = _rescale_from_monthly(start, h, mean_dc, samples_per_year)
    if _solvable(p1):
        return p1
    if _solvable(p0):
        return p0
    return p1


def _pos_simplex(
    theta0: np.ndarray,
    hi: np.ndarray,
    frac: float = 0.2,
) -> np.ndarray:
    """Nelder-Mead simplex: each vertex steps one coordinate up by ``frac``."""
    theta0 = np.asarray(theta0, dtype=float).ravel()
    n = int(theta0.size)
    sim = np.tile(theta0, (n + 1, 1))
    for i in range(n):
        step = frac * (abs(theta0[i]) + 1e-6)
        sim[i + 1, i] = min(theta0[i] + step, float(hi[i]))
    return sim


def _raw_fd_step(name: str, value: float, rel: float) -> float:
    if name == "delta":
        return 1e-6
    if name == "sigma_w":
        return max(abs(float(value)) * 0.05, 1e-10)
    if name in ("mu_c", "mu_d", "sigma", "phi_e"):
        return max(abs(float(value)) * rel * 10.0, 1e-8)
    return rel * (1.0 + abs(float(value)))


def _hansen_j_at_params(
    data: pd.DataFrame,
    params: BKYParams,
    h: int,
    W: np.ndarray,
    hac_lags: int,
    rel: float = 1e-4,
):
    """Hansen Lemma 4.2 J from a raw-parameter finite-difference Jacobian.

    The optimiser lives in scaled coordinates. Differencing those
    coordinates produced J in the thousands at the published Table 2
    vector. Raw steps keep the statistic on the order of ``T g'W g``.
    """
    g = np.asarray(observation_moments(data, params, h), dtype=float)
    gT = g.mean(axis=0)
    theta = _pack(params)
    d = np.zeros((gT.size, theta.size), dtype=float)
    for j, value in enumerate(theta):
        step = _raw_fd_step(PARAM_NAMES[j], float(value), rel)
        for signed in (step, -step):
            bumped = theta.copy()
            bumped[j] = value + signed
            pb = _unpack(bumped, params)
            if not _solvable(pb):
                continue
            try:
                gb = np.asarray(
                    observation_moments(data, pb, h), dtype=float
                ).mean(axis=0)
            except Exception:
                continue
            d[:, j] = (gb - gT) / signed
            break
    s = newey_west(g, lags=hac_lags)
    wdiag = np.diag(np.asarray(W, dtype=float))
    sw = np.sqrt(np.clip(wdiag, 1e-30, None))
    a = sw[:, None] * d
    g_w = sw * gT
    s_w = (sw[:, None] * s) * sw[None, :]
    q, _r = np.linalg.qr(a, mode="reduced")
    proj = q @ q.T
    m = np.eye(gT.size) - proj
    v = m @ s_w @ m.T
    nobs = int(g.shape[0])
    j_stat = float(nobs * g_w @ np.linalg.pinv(v, rcond=1e-8) @ g_w)
    j_df = max(int(gT.size) - int(d.shape[1]), 0)
    return j_stat, j_df, float(chi2.sf(j_stat, j_df))


def _to_model_params(p: BKYParams) -> ModelParams:
    return ModelParams(
        prefs=PreferencesParams(delta=p.delta, gamma=p.gamma, psi=p.psi),
        cons=ConsumptionParams(
            mu=p.mu_c,
            rho=p.rho,
            phi_x=p.phi_e,
            sigma=p.sigma,
            nu=p.nu,
            sigma_w=p.sigma_w,
        ),
        claims={
            "market": ClaimParams(
                mu=p.mu_d,
                phi=p.phi_d,
                phi_sigma=p.phi_d_sigma,
                alpha=p.rho_d,
            )
        },
    )


@dataclass
class BKYResults:
    """Point estimates, GMM diagnostics, and the implied LRR model."""

    params: BKYParams
    h: int
    gmm: GMMResults
    data: pd.DataFrame
    stochastic_vol: bool = True

    @property
    def model(self) -> LongRunRisksModel:
        return LongRunRisksModel(params=_to_model_params(self.params))

    def moment_table(self) -> pd.DataFrame:
        sol = solve_loglinear(self.params)
        model = model_moments(self.params, self.h, sol=sol)
        from .data import sample_moments

        sample = sample_moments(self.data)
        rows = []
        mapping = {
            "vol_dc": ("dc_std", "vol_dc"),
            "mean_zd": ("log_pd_mean", "mean_zd"),
            "vol_zd": ("log_pd_std", "vol_zd"),
            "mean_rf": ("rf_mean", "mean_rf"),
            "vol_rd": ("rm_std", "vol_rd"),
        }
        for label, (skey, mkey) in mapping.items():
            rows.append(
                {
                    "moment": label,
                    "sample": sample.get(skey, np.nan),
                    "model": model.get(mkey, np.nan),
                }
            )
        return pd.DataFrame(rows)

    def states(self):
        sol = solve_loglinear(self.params)
        return extract_states(
            self.data["log_pd"].to_numpy(),
            self.data["rf"].to_numpy(),
            sol,
            params=self.params,
            h=self.h,
        )

    def table2_frame(self) -> pd.DataFrame:
        """Hats against the published Table 2 vector and its bootstrap SEs.

        ``se_hat`` is this sample's SE (sandwich, or block bootstrap when
        ``n_boot>0``). ``se`` is the paper's eight-year block-bootstrap
        SE, used for the comparison ``z``.
        """
        own = None if self.gmm.se is None else np.asarray(self.gmm.se, dtype=float)
        rows = []
        for i, name in enumerate(PARAM_NAMES):
            hat = getattr(self.params, name)
            paper = getattr(TABLE_2_LRR, name)
            se = TABLE_2_SE[name]
            se_hat = (
                float(own[i])
                if own is not None and i < own.size
                else float("nan")
            )
            rows.append(
                {
                    "parameter": name,
                    "hat": hat,
                    "paper": paper,
                    "se_hat": se_hat,
                    "se": se,
                    "z": (hat - paper) / se,
                }
            )
        se_h = (
            float(own[len(PARAM_NAMES)])
            if own is not None and own.size > len(PARAM_NAMES)
            else float("nan")
        )
        rows.append(
            {
                "parameter": "h",
                "hat": float(self.h),
                "paper": float(TABLE_2_LRR_H),
                "se_hat": se_h,
                "se": TABLE_2_SE["h"],
                "z": (self.h - TABLE_2_LRR_H) / TABLE_2_SE["h"],
            }
        )
        return pd.DataFrame(rows)

    def summary(self) -> Summary:
        tab = self.table2_frame()
        lines = [
            "=" * 72,
            "Bansal–Kiku–Yaron (2016) GMM".center(72),
            "=" * 72,
            f"h = {self.h:<6d}  stochastic vol = {self.stochastic_vol}  "
            f"objective = {self.gmm.objective:.4g}",
        ]
        j_stat, j_p, j_df = self.gmm.J, self.gmm.J_pvalue, self.gmm.J_df
        if j_stat is not None and j_p is not None:
            lines.append(
                f"J = {j_stat:<10.4g}  df = {j_df:<4d}  p = {j_p:.4g}"
            )
        elif j_stat is not None:
            lines.append(f"J = {j_stat:.4g}  df = {j_df}")
        else:
            lines.append("J = —")
        lines += [
            "-" * 72,
            f"{'Parameter':16s} {'Estimate':>12s} {'SE':>12s} "
            f"{'Table 2':>12s} {'z':>8s}",
        ]
        for row in tab.itertuples(index=False):
            se_hat = (
                f"{row.se_hat:12.6g}"
                if np.isfinite(row.se_hat)
                else f"{'—':>12s}"
            )
            lines.append(
                f"{row.parameter:16s} {row.hat:12.6g} {se_hat} "
                f"{row.paper:12.6g} {row.z:8.2f}"
            )
        lines.append("=" * 72)
        return Summary(lines)


_STAGE1 = ("vol_dc", "ac1_dc", "ac2_dc")
_STAGE2 = ("mean_dd", "vol_dd", "ac1_dd", "corr_dc_dd")
_STAGE3 = ("mean_zd", "vol_zd", "ac1_zd", "mean_excess", "vol_rd", "mean_rf")
_SELECT = ("mean_dc",) + _STAGE1 + _STAGE2 + _STAGE3

_BOUNDS = {
    "gamma": (5.0, 15.0),
    "psi": (1.1, 3.0),
    "delta": (0.995, 0.9994),
    "mu_c": (0.0005, 0.004),
    "rho": (0.90, 0.995),
    "phi_e": (0.01, 0.08),
    "sigma": (0.003, 0.015),
    "nu": (0.98, 0.9994),
    "sigma_w": (8e-7, 5e-6),
    "mu_d": (0.0, 0.01),
    "phi_d": (1.5, 8.0),
    "phi_d_sigma": (2.0, 10.0),
    "rho_d": (0.15, 0.80),
}


def _stage_bounds(h: int) -> dict[str, tuple[float, float]]:
    b = dict(_BOUNDS)
    h = max(int(h), 1)
    if h < 8:
        b["gamma"] = (5.0, 20.0)
        b["psi"] = (1.01, 4.0)
        b["delta"] = (0.980, 0.9995)
        b["mu_c"] = (0.0005, 0.04)
        b["rho"] = (0.70, 0.995)
        b["phi_e"] = (0.01, 0.30)
        b["sigma"] = (0.003, 0.05)
        b["nu"] = (0.80, 0.9994)
        b["sigma_w"] = (8e-7, 1.2e-5)
        b["mu_d"] = (0.0, 0.03)
    if h > 14:
        b["delta"] = (0.995, 0.9998)
        b["rho"] = (0.90, 0.999)
        b["phi_e"] = (0.005, 0.08)
        b["sigma"] = (0.002, 0.015)
    return b


def _table3_model_target() -> dict[str, float]:
    tgt = dict(TABLE_3_LRR_MODEL)
    tgt["mean_dc"] = TABLE_2_LRR_H * TABLE_2_LRR.mu_c
    tgt["mean_dd"] = TABLE_2_LRR_H * TABLE_2_LRR.mu_d
    return tgt


def _target_from_data(data: pd.DataFrame) -> dict[str, float]:
    dc = data["dc"].to_numpy(dtype=float)
    dd = data["dd"].to_numpy(dtype=float)
    z = data["log_pd"].to_numpy(dtype=float)
    rf = data["rf"].to_numpy(dtype=float)
    rm = data["rm"].to_numpy(dtype=float)
    excess = rm - rf

    def _ac1(x: np.ndarray) -> float:
        x = x[np.isfinite(x)]
        if x.size < 3:
            return 0.0
        xd = x - x.mean()
        return float(np.corrcoef(xd[1:], xd[:-1])[0, 1])

    def _ac2(x: np.ndarray) -> float:
        x = x[np.isfinite(x)]
        if x.size < 4:
            return 0.0
        xd = x - x.mean()
        return float(np.corrcoef(xd[2:], xd[:-2])[0, 1])

    return {
        "mean_dc": float(np.nanmean(dc)),
        "vol_dc": float(np.nanstd(dc, ddof=1)),
        "ac1_dc": _ac1(dc),
        "ac2_dc": _ac2(dc),
        "mean_dd": float(np.nanmean(dd)),
        "vol_dd": float(np.nanstd(dd, ddof=1)),
        "ac1_dd": _ac1(dd),
        "corr_dc_dd": float(np.corrcoef(dc, dd)[0, 1]),
        "mean_zd": float(np.nanmean(z)),
        "vol_zd": float(np.nanstd(z, ddof=1)),
        "ac1_zd": _ac1(z),
        "mean_excess": float(np.nanmean(excess)),
        "vol_rd": float(np.nanstd(rm, ddof=1)),
        "mean_rf": float(np.nanmean(rf)),
        "corr_rd_zd": float(np.corrcoef(rm[1:], z[:-1])[0, 1]),
        "corr_dc_zd": float(np.corrcoef(dc[1:], z[:-1])[0, 1]),
    }


def _sse(params: BKYParams, h: int, keys: tuple[str, ...], target: dict[str, float]) -> float:
    try:
        model = model_moments(params, h)
    except Exception:
        return 1e6
    s = 0.0
    for key in keys:
        if key not in target:
            continue
        scale = max(abs(target[key]), 0.01)
        s += ((model[key] - target[key]) / scale) ** 2
    return float(s)


def _fit_subset(
    params: BKYParams,
    h: int,
    names: tuple[str, ...],
    x0: list[float],
    keys: tuple[str, ...],
    target: dict[str, float],
) -> BKYParams:
    bmap = _stage_bounds(h)
    bounds = [bmap[n] for n in names]

    def obj(x):
        kw = {n: float(v) for n, v in zip(names, x)}
        return _sse(replace(params, **kw), h, keys, target)

    res = minimize(obj, np.asarray(x0, dtype=float), method="L-BFGS-B", bounds=bounds)
    kw = {n: float(v) for n, v in zip(names, res.x)}
    return replace(params, **kw)


def _staged_at_h(
    h: int,
    target: dict[str, float],
    start: BKYParams,
    stochastic_vol: bool,
    samples_per_year: int = 1,
) -> tuple[BKYParams, float]:
    p = _start_at_h(start, h, target["mean_dc"], samples_per_year)
    p = _fit_subset(p, h, ("rho", "phi_e", "sigma"), [p.rho, p.phi_e, p.sigma], _STAGE1, target)
    p = _fit_subset(
        p, h,
        ("mu_d", "phi_d", "phi_d_sigma", "rho_d"),
        [p.mu_d, p.phi_d, p.phi_d_sigma, p.rho_d],
        _STAGE2, target,
    )
    if stochastic_vol:
        p = _fit_subset(
            p, h,
            ("gamma", "psi", "delta", "nu", "sigma_w"),
            [p.gamma, p.psi, p.delta, p.nu, p.sigma_w],
            _STAGE3, target,
        )
    else:
        p = replace(p, nu=0.0, sigma_w=0.0)
        p = _fit_subset(
            p, h,
            ("gamma", "psi", "delta"),
            [p.gamma, p.psi, p.delta],
            _STAGE3, target,
        )
    return p, _sse(p, h, _SELECT, target)


def _md_results(params: BKYParams, h: int, target: dict[str, float]) -> GMMResults:
    keys = [k for k in _SELECT if k in target]
    try:
        model = model_moments(params, h)
        g = np.array([model[k] - target[k] for k in keys], dtype=float)
        obj = _sse(params, h, _SELECT, target)
    except Exception:
        g = np.full(len(keys), 1e3, dtype=float)
        obj = 1e6
    scale = np.array([max(abs(target[k]), 0.01) for k in keys])
    W = np.diag(1.0 / scale**2)
    theta = _pack(params)
    return GMMResults(
        theta,
        g,
        W,
        objective=obj,
        nobs=None,
        names=PARAM_NAMES,
        steps=1,
    )


def _raw_bounds(h: int) -> list[tuple[float, float]]:
    raw = [
        (5.0, 20.0),
        (1.05, 4.0),
        (0.990, 0.9995),
        (0.0003, 0.005),
        (0.85, 0.995),
        (0.005, 0.12),
        (0.002, 0.02),
        (0.90, 0.9995),
        (3e-7, 8e-6),
        (0.0, 0.012),
        (0.5, 12.0),
        (0.5, 12.0),
        (-0.5, 0.95),
    ]
    h = max(int(h), 1)
    if h < 8:
        raw[1] = (1.01, 4.0)
        raw[2] = (0.980, 0.9995)
        raw[3] = (0.0003, 0.04)
        raw[4] = (0.70, 0.995)
        raw[5] = (0.005, 0.30)
        raw[6] = (0.002, 0.05)
        raw[7] = (0.80, 0.9995)
        raw[8] = (3e-7, 1.2e-5)
        raw[9] = (0.0, 0.03)
    if h > 14:
        raw[2] = (0.990, 0.9998)
        raw[3] = (0.0002, 0.005)
        raw[4] = (0.85, 0.999)
        raw[5] = (0.003, 0.12)
    return raw


def _scaled_bounds(stochastic_vol: bool, h: int = 11) -> list[tuple[float, float]]:
    raw = _raw_bounds(h)
    out = []
    for i, (lo, hi) in enumerate(raw):
        if i == 2:
            lo, hi = 1.0 - hi, 1.0 - lo
        out.append((lo * _SCALE[i], hi * _SCALE[i]))
    if not stochastic_vol:
        keep = [i for i, n in enumerate(PARAM_NAMES) if n not in ("nu", "sigma_w")]
        return [out[i] for i in keep]
    return out


def _penalty_g(nobs: int, n_mom: int) -> np.ndarray:
    t = (np.arange(nobs, dtype=float) / max(nobs, 1))[:, None]
    return np.ones((nobs, n_mom)) * 10.0 + t


def _observation_g(data: pd.DataFrame, params: BKYParams, h: int) -> np.ndarray:
    n_mom = len(MOMENT_NAMES)
    nobs = max(len(data) - 3, 1)
    try:
        g = np.asarray(observation_moments(data, params, h), dtype=float)
        if g.ndim != 2 or g.shape[1] != n_mom or g.shape[0] < 4:
            return _penalty_g(nobs, n_mom)
        if not np.all(np.isfinite(g)):
            return _penalty_g(int(g.shape[0]), n_mom)
        return g
    except Exception:
        return _penalty_g(nobs, n_mom)


def _unpack_theta(
    theta: np.ndarray,
    p0: BKYParams,
    stochastic_vol: bool,
) -> BKYParams:
    if stochastic_vol:
        return _unpack_scaled(theta, p0)
    full = _pack_scaled(replace(p0, nu=0.0, sigma_w=0.0))
    j = 0
    for i, n in enumerate(PARAM_NAMES):
        if n in ("nu", "sigma_w"):
            full[i] = 0.0
        else:
            full[i] = theta[j]
            j += 1
    return replace(_unpack_scaled(full, p0), nu=0.0, sigma_w=0.0)


def _pack_theta(params: BKYParams, stochastic_vol: bool) -> np.ndarray:
    theta = _pack_scaled(params)
    if not stochastic_vol:
        free = [i for i, n in enumerate(PARAM_NAMES) if n not in ("nu", "sigma_w")]
        theta = theta[free]
    return theta


def _gmm_at_h(
    data: pd.DataFrame,
    h: int,
    start: BKYParams,
    *,
    stochastic_vol: bool,
    W: str,
    j_test: bool,
    hac_lags: int = 1,
    maxiter: int = 800,
    samples_per_year: int = 1,
) -> BKYResults:
    mean_dc = float(np.nanmean(data["dc"].to_numpy(dtype=float)))
    p0 = _start_at_h(start, h, mean_dc, samples_per_year)
    bounds = _scaled_bounds(stochastic_vol, h)
    names = PARAM_NAMES
    if not stochastic_vol:
        p0 = replace(p0, nu=0.0, sigma_w=0.0)
        names = tuple(n for n in PARAM_NAMES if n not in ("nu", "sigma_w"))

    lo = np.array([b[0] for b in bounds], dtype=float)
    hi = np.array([b[1] for b in bounds], dtype=float)

    def moments(theta, _h=h, _p0=p0, _vol=stochastic_vol):
        th = np.asarray(theta, dtype=float).ravel()
        excess = float(np.sum(np.maximum(lo - th, 0.0) + np.maximum(th - hi, 0.0)))
        th_c = np.minimum(np.maximum(th, lo), hi)
        p = _unpack_theta(th_c, _p0, _vol)
        g = _observation_g(data, p, _h)
        if excess > 0.0:
            return g + (10.0 + 100.0 * excess)
        return g

    theta0 = np.minimum(np.maximum(_pack_theta(p0, stochastic_vol), lo), hi)
    nm_iter = max(int(maxiter), 1)
    id_iter = min(nm_iter, 400)
    nm_opts = {"adaptive": True, "xatol": 1e-8, "fatol": 1e-12}
    if str(W).lower() != "identity":
        fit_id = estimate(
            moments,
            theta0,
            W="identity",
            steps=1,
            hac_lags=hac_lags,
            names=names,
            j_test=False,
            options={
                **nm_opts,
                "maxiter": id_iter,
                "initial_simplex": _pos_simplex(theta0, hi, 0.2),
            },
        )
        theta0 = np.minimum(np.maximum(np.asarray(fit_id.theta, dtype=float), lo), hi)
    fit_nm = estimate(
        moments,
        theta0,
        W=W,
        steps=1,
        hac_lags=hac_lags,
        names=names,
        j_test=False,
        options={
            **nm_opts,
            "maxiter": nm_iter,
            "initial_simplex": _pos_simplex(theta0, hi, 0.15),
        },
    )
    theta_hat = np.minimum(np.maximum(np.asarray(fit_nm.theta, dtype=float), lo), hi)
    # φ_{dσ} is the unconstrained CUE value. The remaining miss vs Table 2
    # is `_annual_map` (monthly A1/A2 on annual z), not a post-hoc bound.
    fit = estimate(
        moments,
        theta_hat,
        W=W,
        steps=1,
        hac_lags=hac_lags,
        names=names,
        j_test=j_test,
        options={"maxiter": 0, "xatol": 1.0, "fatol": 1.0},
    )
    params = _unpack_theta(np.minimum(np.maximum(fit.theta, lo), hi), p0, stochastic_vol)
    if fit.se is not None:
        try:
            fit.se = _unscale_se(fit.se, stochastic_vol)
        except ValueError:
            pass
    if j_test:
        try:
            j_stat, j_df, j_p = _hansen_j_at_params(
                data, params, h, fit.W, hac_lags
            )
            fit.J = j_stat
            fit.J_df = j_df
            fit.J_pvalue = j_p
        except Exception:
            pass
    return BKYResults(
        params=params,
        h=h,
        gmm=fit,
        data=data,
        stochastic_vol=stochastic_vol,
    )


def estimate_bky(
    data: pd.DataFrame,
    *,
    h: int | None = None,
    h_grid: tuple[int, ...] | None = None,
    start: BKYParams | None = None,
    stochastic_vol: bool = True,
    method: str = "gmm",
    W: str = "cue_invvar",
    j_test: bool = True,
    hac_lags: int = 1,
    n_boot: int = 0,
    block_length: int = 8,
    maxiter: int = 800,
    bootstrap_h: bool = False,
) -> BKYResults:
    """GMM on the annual or quarterly panel. Table 2 is a comparison, not an input.

    ``data`` is ``load_annual()`` or ``load_quarterly()``. The start is
    the Bansal–Yaron (2004) monthly calibration, not the published Table
    2 vector. Integer ``h`` is chosen on a grid. ``n_boot>0`` is an
    eight-year moving-block bootstrap at ``ĥ``; ``bootstrap_h=True``
    re-selects ``h`` on each draw and stores SE(``h``) as the last entry
    of ``gmm.se``.
    """
    if data is None or len(data) == 0:
        raise TypeError("estimate_bky needs the annual panel from load_annual().")
    start = start or COLD_START
    spy = _samples_per_year(data)
    if h is not None:
        grid = (int(h),)
    elif h_grid is not None:
        grid = tuple(int(x) for x in h_grid)
    else:
        grid = (8, 9, 10, 11, 12, 13, 14) if spy == 1 else (1, 2, 3, 4)

    if method == "staged":
        tgt = _target_from_data(data)
        best_p: BKYParams | None = None
        best_h = grid[0]
        best_obj = np.inf
        for cand in grid:
            p, obj = _staged_at_h(
                cand, tgt, start, stochastic_vol, samples_per_year=spy,
            )
            if obj < best_obj:
                best_p, best_h, best_obj = p, cand, obj
        assert best_p is not None
        gmm = _md_results(best_p, best_h, tgt)
        return BKYResults(
            params=best_p,
            h=best_h,
            gmm=gmm,
            data=data,
            stochastic_vol=stochastic_vol,
        )
    if method not in ("gmm", "panel"):
        raise ValueError(f"Unknown method {method!r}; use 'gmm' or 'staged'.")

    best: BKYResults | None = None
    errors: list[str] = []
    for cand in grid:
        try:
            cand_res = _gmm_at_h(
                data, cand, start,
                stochastic_vol=stochastic_vol, W=W, j_test=j_test,
                hac_lags=hac_lags, maxiter=maxiter,
                samples_per_year=spy,
            )
        except Exception as exc:
            errors.append(f"h={cand}: {exc}")
            continue
        if best is None or cand_res.gmm.objective < best.gmm.objective:
            best = cand_res
    if best is None:
        raise RuntimeError("GMM failed at every h. " + "; ".join(errors))
    if n_boot > 0:
        h_hat = best.h

        def _boot(idx, _h=h_hat, _grid=grid, _spy=spy):
            sub = data.iloc[np.asarray(idx)].reset_index(drop=True)
            if bootstrap_h:
                res = estimate_bky(
                    sub,
                    h_grid=_grid,
                    start=start,
                    stochastic_vol=stochastic_vol,
                    method="gmm",
                    W=W,
                    j_test=False,
                    hac_lags=hac_lags,
                    n_boot=0,
                    maxiter=maxiter,
                )
                return np.append(_pack(res.params), float(res.h))
            res = _gmm_at_h(
                sub, _h, start,
                stochastic_vol=stochastic_vol, W=W, j_test=False,
                hac_lags=hac_lags, maxiter=maxiter,
                samples_per_year=_spy,
            )
            return _pack(res.params)

        se, _draws = block_bootstrap(
            _boot,
            len(data),
            block_length=block_length,
            n_boot=n_boot,
        )
        best.gmm.se = se
    return best
