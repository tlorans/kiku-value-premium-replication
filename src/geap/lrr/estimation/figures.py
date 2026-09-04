"""Figures 1 and 2 of Bansal, Kiku, and Yaron (2016)."""
from __future__ import annotations

import numpy as np
import pandas as pd
from numpy.polynomial.polynomial import polyroots
from scipy.optimize import least_squares
from scipy.signal import lfilter

from .goldens import TABLE_2_LRR, TABLE_4_ANNUAL
from .simulate import simulate_annual
from .solution import BKYParams, solve_loglinear
from .states import extract_states

_ARMA_P = 8
_ARMA_Q = 8


def _pyplot():
    try:
        import matplotlib
    except ImportError as exc:
        raise ImportError(
            "matplotlib is required for estimation figures. "
            "Install the [dev] or [data] extra."
        ) from exc
    try:
        matplotlib.use("Agg")
    except Exception:
        pass
    import matplotlib.pyplot as plt
    return plt


def figure1_frame(data: pd.DataFrame, params: BKYParams | None = None) -> pd.DataFrame:
    """Extracted expected growth against realized consumption growth."""
    p = params or TABLE_2_LRR
    sol = solve_loglinear(p)
    st = extract_states(
        data["log_pd"].to_numpy(),
        data["rf"].to_numpy(),
        sol,
        params=p,
        h=11,
    )
    return pd.DataFrame(
        {
            "year": data["year"].to_numpy(),
            "dc": data["dc"].to_numpy(dtype=float),
            "x": st.x,
            "sigma2": st.sigma2,
        }
    )


def figure1_plot(data: pd.DataFrame, params: BKYParams | None = None):
    """Dual-axis plot of realized Δc and extracted x_t, 1930–2015."""
    plt = _pyplot()
    frame = figure1_frame(data, params)
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    ax.plot(frame["year"], frame["dc"], color="k", lw=1.2, label="Realized growth")
    ax.set_ylabel("Consumption growth")
    ax.set_xlabel("Year")
    ax.set_xlim(1930, 2015)
    ax2 = ax.twinx()
    ax2.plot(
        frame["year"],
        frame["x"],
        color="0.5",
        lw=1.0,
        ls="--",
        label="Expected growth",
    )
    ax2.set_ylabel("Long-run risk (x)")
    lines = ax.get_lines() + ax2.get_lines()
    ax.legend(lines, [ln.get_label() for ln in lines], frameon=False)
    fig.tight_layout()
    return fig


def _finite_demean(y: np.ndarray) -> np.ndarray:
    y = np.asarray(y, dtype=float)
    y = y[np.isfinite(y)]
    if y.size == 0:
        return y
    return y - y.mean()


def _ar_phi(y: np.ndarray, p: int) -> np.ndarray:
    n = y.size
    if n <= p + 1:
        return np.zeros(p)
    Y = y[p:]
    X = np.column_stack([y[p - i : n - i] for i in range(1, p + 1)])
    phi, *_ = np.linalg.lstsq(X, Y, rcond=None)
    return np.asarray(phi, dtype=float)


def _poly_roots_outside_unit(coef: np.ndarray) -> bool:
    """True if Φ(z) = 1 − c1 z − … has all roots |z| > 1.

    ``numpy.polynomial.polynomial.polyroots`` takes low-degree-first
    coefficients, so this is the AR polynomial itself. ``np.roots`` on
    ``[1, −c…]`` would return the reciprocal roots.
    """
    if coef.size == 0 or not np.all(np.isfinite(coef)):
        return False
    roots = polyroots(np.concatenate(([1.0], -np.asarray(coef, dtype=float))))
    if roots.size == 0:
        return True
    return bool(np.all(np.abs(roots) > 1.0 + 1e-8))


def _arma_errors(y: np.ndarray, phi: np.ndarray, theta: np.ndarray) -> np.ndarray:
    b = np.concatenate(([1.0], -phi))
    a = np.concatenate(([1.0], theta))
    return lfilter(b, a, y)


def _arma_hr(y: np.ndarray, p: int, q: int) -> tuple[np.ndarray, np.ndarray]:
    """Hannan–Rissanen start for ARMA(p, q)."""
    n = y.size
    m = min(max(p + q + 8, 20), max(p + q, n // 5))
    if n <= m + p + q + 2:
        return _ar_phi(y, p), np.zeros(q)
    Y = y[m:]
    X = np.column_stack([y[m - i : n - i] for i in range(1, m + 1)])
    ar_m, *_ = np.linalg.lstsq(X, Y, rcond=None)
    e = np.zeros(n)
    e[m:] = Y - X @ ar_m
    start = max(p, m + q)
    if n - start < p + q + 2:
        return _ar_phi(y, p), np.zeros(q)
    cols = [y[start - i : n - i] for i in range(1, p + 1)]
    cols += [e[start - j : n - j] for j in range(1, q + 1)]
    coef, *_ = np.linalg.lstsq(np.column_stack(cols), y[start:], rcond=None)
    return np.asarray(coef[:p], dtype=float), np.asarray(coef[p:], dtype=float)


def _arma_css(
    y: np.ndarray, phi0: np.ndarray, theta0: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    p = int(phi0.size)
    q = int(theta0.size)
    start = max(p, q)
    x0 = np.concatenate([phi0, theta0])

    def resid(x: np.ndarray) -> np.ndarray:
        e = _arma_errors(y, x[:p], x[p:])
        if not np.all(np.isfinite(e)):
            return np.full(y.size - start, 1e6)
        return e[start:]

    try:
        out = least_squares(resid, x0, method="lm", max_nfev=400)
    except Exception:
        return phi0, theta0
    phi = np.asarray(out.x[:p], dtype=float)
    theta = np.asarray(out.x[p:], dtype=float)
    if not (np.all(np.isfinite(phi)) and np.all(np.isfinite(theta))):
        return phi0, theta0
    return phi, theta


def _arma_coefs(y: np.ndarray, p: int = _ARMA_P, q: int = _ARMA_Q) -> tuple[np.ndarray, np.ndarray]:
    """Conditional least-squares ARMA(p, q) on a demeaned series."""
    y = _finite_demean(y)
    if y.size < p + q + 8:
        return _ar_phi(y, p), np.zeros(q)
    phi, theta = _arma_hr(y, p, q)
    phi, theta = _arma_css(y, phi, theta)
    if not _poly_roots_outside_unit(phi):
        phi_hr, theta_hr = _arma_hr(y, p, q)
        if _poly_roots_outside_unit(phi_hr):
            return phi_hr, theta_hr
        return _ar_phi(y, p), np.zeros(q)
    return phi, theta


def _arma_irf(
    phi: np.ndarray,
    theta: np.ndarray,
    horizon: int,
    cumulative: bool,
) -> np.ndarray:
    if horizon <= 0:
        return np.zeros(0)
    impulse = np.zeros(horizon)
    impulse[0] = 1.0
    b = np.concatenate(([1.0], np.asarray(theta, dtype=float)))
    a = np.concatenate(([1.0], -np.asarray(phi, dtype=float)))
    psi = np.asarray(lfilter(b, a, impulse), dtype=float)
    if not np.all(np.isfinite(psi)):
        psi = np.zeros(horizon)
        psi[0] = 1.0
    return np.cumsum(psi) if cumulative else psi


def figure2_irf(
    *,
    horizon_dc: int = 50,
    horizon_var: int = 150,
    years: int = 800,
    seed: int = 0,
    horizon: int | None = None,
) -> pd.DataFrame:
    """ARMA(8, 8) impulse responses of annual consumption and its variance.

    Footnote 10: fit ARMA(8, 8) to a long simulated annual sample of Δc
    and of (Δc − mean)². Cumulative IRF of consumption; non-cumulative
    IRF of the variance proxy. LRR is Table 2 with h=11; annual is
    Table 4 with h=1. ``horizon`` is an alias for ``horizon_dc``.
    """
    if horizon is not None:
        horizon_dc = horizon
    lrr = simulate_annual(TABLE_2_LRR, 11, years=years, seed=seed)
    ann = simulate_annual(TABLE_4_ANNUAL, 1, years=years, seed=seed + 1)
    n = max(horizon_dc, horizon_var)
    dc_lrr = np.full(n, np.nan)
    dc_ann = np.full(n, np.nan)
    var_lrr = np.full(n, np.nan)
    var_ann = np.full(n, np.nan)
    phi, theta = _arma_coefs(lrr["dc"].to_numpy())
    dc_lrr[:horizon_dc] = _arma_irf(phi, theta, horizon_dc, True)
    phi, theta = _arma_coefs(ann["dc"].to_numpy())
    dc_ann[:horizon_dc] = _arma_irf(phi, theta, horizon_dc, True)
    v_lrr = (lrr["dc"] - lrr["dc"].mean()) ** 2
    v_ann = (ann["dc"] - ann["dc"].mean()) ** 2
    phi, theta = _arma_coefs(v_lrr.to_numpy())
    var_lrr[:horizon_var] = _arma_irf(phi, theta, horizon_var, False)
    phi, theta = _arma_coefs(v_ann.to_numpy())
    var_ann[:horizon_var] = _arma_irf(phi, theta, horizon_var, False)
    return pd.DataFrame(
        {
            "horizon": np.arange(n),
            "dc_lrr": dc_lrr,
            "dc_annual": dc_ann,
            "var_lrr": var_lrr,
            "var_annual": var_ann,
        }
    )


def figure2_plot(
    *,
    horizon_dc: int = 50,
    horizon_var: int = 150,
    years: int = 800,
    seed: int = 0,
):
    """Stacked IRFs of annual Δc (panel a) and its variance (panel b)."""
    plt = _pyplot()
    irf = figure2_irf(
        horizon_dc=horizon_dc,
        horizon_var=horizon_var,
        years=years,
        seed=seed,
    )
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 6.0))
    h = irf["horizon"].to_numpy()
    m_dc = h < horizon_dc
    m_var = h < horizon_var
    axes[0].plot(h[m_dc], irf.loc[m_dc, "dc_lrr"], color="k", lw=1.2, label="LRR")
    axes[0].plot(
        h[m_dc],
        irf.loc[m_dc, "dc_annual"],
        color="0.5",
        lw=1.0,
        ls="--",
        label="Annual",
    )
    axes[0].set_ylabel("Cumulative response")
    axes[0].set_title("(a) Annual consumption growth")
    axes[0].legend(frameon=False)
    axes[0].set_xlim(0, max(horizon_dc - 1, 0))
    axes[1].plot(h[m_var], irf.loc[m_var, "var_lrr"], color="k", lw=1.2, label="LRR")
    axes[1].plot(
        h[m_var],
        irf.loc[m_var, "var_annual"],
        color="0.5",
        lw=1.0,
        ls="--",
        label="Annual",
    )
    axes[1].set_ylabel("Response")
    axes[1].set_xlabel("Years")
    axes[1].set_title("(b) Conditional variance of consumption growth")
    axes[1].legend(frameon=False)
    axes[1].set_xlim(0, max(horizon_var - 1, 0))
    fig.tight_layout()
    return fig
