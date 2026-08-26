"""
Section 5 figures: long-run premia, mean log(P/D), and the model analogue of Figure 2.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from ..model.analytical import solve_analytical
from ..model.dynamics import Dynamics
from ..model.params import get_table_ii_params


def _pdf_svg_paths(path) -> tuple[Path, Path]:
    p = Path(path)
    stem = p.with_suffix("")
    return stem.with_suffix(".pdf"), stem.with_suffix(".svg")


def _save_pdf_svg(fig, path) -> None:
    pdf_path, svg_path = _pdf_svg_paths(path)
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(pdf_path)
    fig.savefig(svg_path)


def _pyplot():
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise ImportError(
            "matplotlib is required for implications figures. "
            "Install the [dev] or [data] extra."
        ) from exc
    return plt


def figure_lr_premium(path) -> None:
    """Bar chart of analytical long-run risk premia by asset."""
    plt = _pyplot()
    sol = solve_analytical(get_table_ii_params())
    names = list(sol.premium_lr.keys())
    values = [sol.premium_lr[name] * 100.0 for name in names]
    fig, ax = plt.subplots()
    ax.bar(names, values)
    ax.set_ylabel("Long-run risk premium (%)")
    ax.set_title("Long-run risk component of expected returns")
    _save_pdf_svg(fig, path)
    plt.close(fig)


def figure_mean_pd(solver, path) -> None:
    """Bar chart of mean log price–dividend ratios from a solved model."""
    plt = _pyplot()
    if hasattr(solver, "mean_pd") and callable(getattr(solver, "mean_pd")):
        pd_vals = solver.mean_pd()
    else:
        pd_vals = {
            name: float(np.dot(solver.stationary, solver.z[name]))
            for name in solver.z
        }
    names = list(pd_vals.keys())
    fig, ax = plt.subplots()
    ax.bar(names, [pd_vals[name] for name in names])
    ax.set_ylabel("Mean log(P/D)")
    ax.set_title("Mean log price–dividend ratios")
    _save_pdf_svg(fig, path)
    plt.close(fig)


def figure5(path, years: int = 200, seed: int = 1) -> None:
    """
    Model-implied analogue of Figure 2: value premium vs consumption volatility.

    Simulates `years` of monthly cash-flows, annualizes, and plots the
    analytical value–growth spread scaled by consumption variance against
    the 3-year moving average of squared AR(1) consumption residuals.
    """
    plt = _pyplot()
    params = get_table_ii_params()
    n_months = years * 12
    sim = Dynamics(params, seed=seed).simulate_cashflows(n_months)

    dc_ann = sim["dc"].reshape(years, 12).sum(axis=1)
    s2_ann = sim["sigma2"].reshape(years, 12).mean(axis=1)

    sol = solve_analytical(params)
    spread = sol.premium_lr["value"] - sol.premium_lr["growth"]
    prem = spread * (s2_ann / np.mean(s2_ann))

    # AR(1) residuals of annual Δc; 3-year MA of squares, rescaled to the premium.
    rho = np.corrcoef(dc_ann[:-1], dc_ann[1:])[0, 1] if years > 2 else 0.0
    resid = np.empty(years)
    resid[0] = 0.0
    resid[1:] = dc_ann[1:] - rho * dc_ann[:-1]
    sq = resid ** 2
    kernel = np.ones(3) / 3.0
    vol_ma = np.convolve(sq, kernel, mode="same")
    vol_rescaled = (
        (vol_ma - vol_ma.mean()) / (vol_ma.std() + 1e-12) * prem.std() + prem.mean()
    )

    t = np.arange(years)
    fig, ax = plt.subplots()
    ax.plot(t, prem * 100.0, label="Model-implied value premium")
    ax.plot(t, vol_rescaled * 100.0, label="Consumption vol (rescaled)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Percent")
    ax.set_title("Model-implied premium vs consumption volatility")
    ax.legend()
    _save_pdf_svg(fig, path)
    plt.close(fig)
