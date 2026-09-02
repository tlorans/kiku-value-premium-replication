"""
Section 5 figures: long-run premia, mean log(P/D), and the model analogue of Figure 2.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from ..analytical import solve_analytical
from ..dynamics import Dynamics
from ..params import get_table_ii_params


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
        import matplotlib
    except ImportError as exc:
        raise ImportError(
            "matplotlib is required for implications figures. "
            "Install the [dev] or [data] extra."
        ) from exc
    try:
        matplotlib.use("Agg")
    except Exception:
        pass
    import matplotlib.pyplot as plt
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


def figure_mean_pd(results, path) -> None:
    """Bar chart of mean log price–dividend ratios from a grid solution.

    Takes the :class:`~geap.GridResults` returned by
    ``LongRunRisksModel.solve()``.
    """
    plt = _pyplot()
    if hasattr(results, "mean_pd") and callable(getattr(results, "mean_pd")):
        pd_vals = results.mean_pd()
    else:
        pd_vals = {
            name: float(np.dot(results.stationary, results.z[name]))
            for name in results.z
        }
    names = list(pd_vals.keys())
    fig, ax = plt.subplots()
    ax.bar(names, [pd_vals[name] for name in names])
    ax.set_ylabel("Mean log(P/D)")
    ax.set_title("Mean log price–dividend ratios")
    _save_pdf_svg(fig, path)
    plt.close(fig)


def _log_linear_pd_and_returns(sim: dict, sol, params) -> dict[str, np.ndarray]:
    """Monthly log(P/D) and simple returns from Section 3.4 elasticities."""
    x = sim["x"]
    s2 = sim["sigma2"]
    s2_bar = params.cons.sigma ** 2
    out: dict[str, np.ndarray] = {}
    for name in ("growth", "value", "market"):
        mean_z = sol.mean_log_pd[name]
        a1 = sol.A1[name]
        a2 = sol.A2[name]
        z = mean_z + a1 * x + a2 * (s2 - s2_bar)
        kappa1 = np.exp(mean_z) / (1.0 + np.exp(mean_z))
        kappa0 = np.log(1.0 + np.exp(mean_z)) - kappa1 * mean_z
        dd = sim[f"dd_{name}"]
        # r_{t+1} uses z_t and z_{t+1}; pad first observation with NaN
        r = np.full_like(z, np.nan)
        r[1:] = np.exp(kappa0 + kappa1 * z[1:] - z[:-1] + dd[1:]) - 1.0
        out[f"z_{name}"] = z
        out[f"r_{name}"] = r
        out[f"dd_{name}"] = dd
    return out


def _annualize_paths(monthly: dict[str, np.ndarray], years: int) -> dict[str, np.ndarray]:
    """Calendar-year returns, dividend growth, and December log(P/D)."""
    n = years * 12

    def block(x: np.ndarray) -> np.ndarray:
        return x[:n].reshape(years, 12)

    ann: dict[str, np.ndarray] = {}
    for name in ("growth", "value", "market"):
        r_m = block(monthly[f"r_{name}"])
        # Compound within year; January may be NaN on year 0 — treat as 0 contribution
        r_filled = np.where(np.isfinite(r_m), r_m, 0.0)
        ann[f"ret_{name}"] = np.prod(1.0 + r_filled, axis=1) - 1.0
        ann[f"dg_{name}"] = block(monthly[f"dd_{name}"]).sum(axis=1)
        ann[f"pd_{name}"] = np.exp(block(monthly[f"z_{name}"])[:, -1])
    return ann


def _expected_value_premium(
    spread: np.ndarray,
    pd_g: np.ndarray,
    pd_v: np.ndarray,
    dg_g: np.ndarray,
    dg_v: np.ndarray,
) -> np.ndarray:
    """OLS of value−growth returns on lagged Growth/Value P/D and Δd."""
    y = spread[1:]
    X = np.column_stack(
        [
            np.ones(y.size),
            pd_g[:-1],
            pd_v[:-1],
            dg_g[:-1],
            dg_v[:-1],
        ]
    )
    mask = np.isfinite(y) & np.all(np.isfinite(X), axis=1)
    prem = np.full(spread.shape, np.nan)
    if mask.sum() < 5:
        return prem
    beta, *_ = np.linalg.lstsq(X[mask], y[mask], rcond=None)
    fitted = X @ beta
    prem[1:] = fitted
    return prem


def _ar1_residual(x: np.ndarray) -> np.ndarray:
    y = x[1:]
    lag = x[:-1]
    X = np.column_stack([np.ones(y.size), lag])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return y - X @ beta


def figure5(path, years: int = 1000, seed: int = 1) -> None:
    """
    Model-implied analogue of Figure 2: value premium vs consumption volatility.

    Simulates `years` of monthly cash-flows, builds log-linear P/D and returns
    from Section 3.4 elasticities, projects the value−growth spread on lagged
    P/D and Δd, and plots that against the 3-year MA of squared AR(1)
    consumption residuals (rescaled).
    """
    plt = _pyplot()
    params = get_table_ii_params()
    sol = solve_analytical(params)
    n_months = years * 12
    sim = Dynamics(params, seed=seed).simulate_cashflows(n_months)
    monthly = _log_linear_pd_and_returns(sim, sol, params)
    ann = _annualize_paths(monthly, years)

    spread = ann["ret_value"] - ann["ret_growth"]
    prem = _expected_value_premium(
        spread,
        ann["pd_growth"],
        ann["pd_value"],
        ann["dg_growth"],
        ann["dg_value"],
    )

    dc_ann = sim["dc"][:n_months].reshape(years, 12).sum(axis=1)
    resid = _ar1_residual(dc_ann)
    sq = np.full(years, np.nan)
    sq[1:] = resid ** 2
    # 3-year MA; align to full sample with NaN edges
    vol_ma = np.full(years, np.nan)
    for t in range(2, years):
        window = sq[t - 2 : t + 1]
        if np.all(np.isfinite(window)):
            vol_ma[t] = float(np.mean(window))

    mask = np.isfinite(prem) & np.isfinite(vol_ma)
    prem_m = prem[mask]
    vol_m = vol_ma[mask]
    if prem_m.size == 0 or float(np.std(vol_m)) < 1e-18:
        vol_rescaled = vol_ma.copy()
    else:
        scale = float(np.std(prem_m))
        vol_rescaled = np.full(years, np.nan)
        vol_rescaled[mask] = (
            (vol_m - vol_m.mean()) / (vol_m.std() + 1e-12) * scale + prem_m.mean()
        )

    t = np.arange(years)
    fig, ax = plt.subplots(figsize=(7.5, 3.2))
    ax.plot(t[mask], prem_m * 100.0, color="k", lw=1.0, label="Model-implied value premium")
    ax.plot(
        t[mask],
        vol_rescaled[mask] * 100.0,
        color="0.5",
        lw=1.0,
        ls="--",
        label="Consumption vol (rescaled)",
    )
    ax.set_xlabel("Year")
    ax.set_ylabel("Percent")
    ax.set_title("Figure 5. Model-implied premium vs consumption volatility")
    ax.legend(frameon=False)
    fig.tight_layout()
    _save_pdf_svg(fig, path)
    plt.close(fig)
