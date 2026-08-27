"""Kiku (2006) Figures 1–4 from an annual book-to-market panel."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .goldens import FIGURE2_START
from .tables import _ar1_residual


def _pyplot():
    try:
        import matplotlib
    except ImportError as exc:
        raise ImportError(
            "matplotlib is required for empirical figures. "
            "Install the [dev] or [data] extra."
        ) from exc
    try:
        matplotlib.use("Agg")
    except Exception:
        pass
    import matplotlib.pyplot as plt
    return plt


def _save_pdf_svg(fig, path) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(p)
    fig.savefig(p.with_suffix(".svg"))


def _wide(bm: pd.DataFrame, col: str) -> pd.DataFrame:
    return bm.pivot(index="year", columns="claim", values=col)


def _ma3(s: pd.Series) -> pd.Series:
    return s.astype(float).rolling(3, min_periods=3).mean()


def _rescale(src: pd.Series, target: pd.Series) -> pd.Series:
    a, b = src.align(target, join="inner")
    a = a.astype(float)
    b = b.astype(float)
    sd_a = float(a.std(ddof=1)) if a.size else 0.0
    sd_b = float(b.std(ddof=1)) if b.size else 0.0
    if a.size == 0 or not np.isfinite(sd_a) or sd_a == 0.0:
        return pd.Series(np.nan, index=a.index)
    scale = sd_b if np.isfinite(sd_b) and sd_b else 1.0
    return (a - a.mean()) / sd_a * scale + b.mean()


def expected_value_premium(
    spread: pd.Series,
    pd_g: pd.Series,
    pd_v: pd.Series,
    dg_g: pd.Series,
    dg_v: pd.Series,
) -> pd.Series:
    """OLS of the value–growth spread on lagged Growth/Value P/D and Δd."""
    X = pd.concat(
        {
            "const": pd.Series(1.0, index=spread.index),
            "pdg": pd_g.shift(1),
            "pdv": pd_v.shift(1),
            "dgg": dg_g.shift(1),
            "dgv": dg_v.shift(1),
        },
        axis=1,
    )
    frame = pd.concat([spread.rename("y"), X], axis=1).dropna()
    if frame.empty:
        return pd.Series(dtype=float, name="premium")
    y = frame["y"].to_numpy(dtype=float)
    xx = frame.drop(columns=["y"]).to_numpy(dtype=float)
    beta, *_ = np.linalg.lstsq(xx, y, rcond=None)
    return pd.Series(xx @ beta, index=frame.index, name="premium")


def _arma11_params(x: np.ndarray) -> tuple[float, float, float]:
    y = np.asarray(x, dtype=float)
    y = y[np.isfinite(y)]
    y = y - y.mean() if y.size else y
    t = y.size
    if t < 3:
        return 0.0, 0.0, float(np.var(y, ddof=0)) if t else 1.0
    g0 = float(np.dot(y, y) / t)
    g1 = float(np.dot(y[1:], y[:-1]) / t)
    g2 = float(np.dot(y[2:], y[:-2]) / t)
    if g0 <= 0.0:
        return 0.0, 0.0, 0.0
    phi = 0.0 if abs(g1) < 1e-15 else float(np.clip(g2 / g1, -0.99, 0.99))
    rho1 = g1 / g0
    a = phi - rho1
    b = 1.0 + phi * phi - 2.0 * rho1 * phi
    c = phi - rho1
    theta = 0.0
    if abs(a) < 1e-15:
        if abs(b) > 1e-15:
            theta = float(np.clip(-c / b, -0.99, 0.99))
    else:
        disc = b * b - 4.0 * a * c
        if disc >= 0.0:
            root = float(np.sqrt(disc))
            cands = [(-b + root) / (2.0 * a), (-b - root) / (2.0 * a)]
            invert = [z for z in cands if abs(z) < 1.0]
            theta = float(invert[0]) if invert else float(np.clip(cands[0], -0.99, 0.99))
    num = 1.0 + theta * theta + 2.0 * phi * theta
    den = 1.0 - phi * phi
    sigma2 = g0 * den / num if abs(num) > 1e-15 else g0
    return phi, theta, max(float(sigma2), 0.0)


def _arma11_spectrum(omega: np.ndarray, phi: float, theta: float, sigma2: float) -> np.ndarray:
    num = 1.0 + theta * theta + 2.0 * theta * np.cos(omega)
    den = 1.0 + phi * phi - 2.0 * phi * np.cos(omega)
    den = np.where(np.abs(den) < 1e-15, 1e-15, den)
    return (sigma2 / (2.0 * np.pi)) * num / den


def _bartlett_periodogram(x: np.ndarray, omega: np.ndarray) -> np.ndarray:
    y = np.asarray(x, dtype=float)
    y = y[np.isfinite(y)]
    y = y - y.mean() if y.size else y
    t = y.size
    if t == 0:
        return np.zeros_like(omega)
    m = t - 1
    gamma0 = float(np.dot(y, y) / t)
    if m < 1:
        return np.full_like(omega, gamma0 / (2.0 * np.pi), dtype=float)
    spec = np.full_like(omega, gamma0, dtype=float)
    for k in range(1, m + 1):
        w = 1.0 - k / (m + 1)
        gammak = float(np.dot(y[k:], y[:-k]) / t)
        spec = spec + 2.0 * w * gammak * np.cos(omega * k)
    return spec / (2.0 * np.pi)


def figure1(bm: pd.DataFrame, path) -> None:
    """Bar chart of 100 × (Value − Growth) realized returns."""
    plt = _pyplot()
    w = _wide(bm, "ret")
    spread = w["Value"] - w["Growth"]
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    ax.bar(spread.index.astype(float), 100.0 * spread.to_numpy(), color="0.35", width=0.8)
    ax.axhline(0.0, color="k", lw=0.6)
    ax.set_ylabel("Value minus growth, percent")
    ax.set_xlabel("Year")
    ax.set_title("Figure 1. Realized value premium")
    fig.tight_layout()
    _save_pdf_svg(fig, path)
    plt.close(fig)


def figure2(bm: pd.DataFrame, dc: pd.Series, path) -> None:
    """Expected value premium vs rescaled 3-year MA of squared AR(1) Δc residuals."""
    plt = _pyplot()
    w_ret = _wide(bm, "ret")
    w_pd = _wide(bm, "pd")
    w_dg = _wide(bm, "dgrowth")
    spread = w_ret["Value"] - w_ret["Growth"]
    prem = expected_value_premium(
        spread, w_pd["Growth"], w_pd["Value"], w_dg["Growth"], w_dg["Value"]
    )
    eta = _ar1_residual(pd.Series(dc).astype(float))
    vol = _ma3(eta.pow(2))
    prem, vol = prem.align(vol, join="inner")
    vol = _rescale(vol, prem)
    if (prem.index >= FIGURE2_START).any():
        prem = prem[prem.index >= FIGURE2_START]
        vol = vol[vol.index >= FIGURE2_START]
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    ax.plot(prem.index, 100.0 * prem, color="k", lw=1.2, label="Value premium")
    ax.plot(vol.index, 100.0 * vol, color="0.5", lw=1.0, ls="--", label="Consumption uncertainty")
    ax.legend(frameon=False)
    ax.set_ylabel("Percent")
    ax.set_xlabel("Year")
    ax.set_title("Figure 2. Expected value premium and consumption volatility")
    fig.tight_layout()
    _save_pdf_svg(fig, path)
    plt.close(fig)


def figure3(dc: pd.Series, path) -> None:
    """ARMA(1,1) spectrum versus Bartlett lag-window periodogram of Δc."""
    plt = _pyplot()
    x = pd.Series(dc).astype(float).dropna().to_numpy()
    omega = np.linspace(0.0, np.pi, 256)
    phi, theta, sigma2 = _arma11_params(x)
    arma = _arma11_spectrum(omega, phi, theta, sigma2)
    bart = _bartlett_periodogram(x, omega)
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    ax.plot(omega, arma, color="k", lw=1.2, label="ARMA(1,1)")
    ax.plot(omega, bart, color="0.5", lw=1.0, ls="--", label="Bartlett")
    ax.set_xlabel("Frequency")
    ax.set_ylabel("Spectrum")
    ax.set_title("Figure 3. Spectral density of consumption growth")
    ax.legend(frameon=False)
    fig.tight_layout()
    _save_pdf_svg(fig, path)
    plt.close(fig)


def figure4(bm: pd.DataFrame, dc: pd.Series, path) -> None:
    """Two panels: 3-year MA of Δd versus rescaled 3-year MA of Δc (growth, value)."""
    plt = _pyplot()
    w = _wide(bm, "dgrowth")
    c = _ma3(pd.Series(dc).astype(float))
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 5.5), sharex=True)
    for ax, claim in zip(axes, ("Growth", "Value")):
        g = _ma3(w[claim])
        cres = _rescale(c, g)
        ax.plot(g.index, 100.0 * g, color="k", lw=1.2, label=f"{claim} Δd")
        ax.plot(cres.index, 100.0 * cres, color="0.5", lw=1.0, ls="--", label="Consumption")
        ax.set_ylabel("Three-year average, percent")
        ax.legend(frameon=False)
        ax.set_title(claim)
    axes[-1].set_xlabel("Year")
    fig.suptitle("Figure 4. Dividend growth and consumption")
    fig.tight_layout()
    _save_pdf_svg(fig, path)
    plt.close(fig)
