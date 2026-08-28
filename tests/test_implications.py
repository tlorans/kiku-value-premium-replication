"""Validation of the numerical solver against Kiku (2006) Tables VII–VIII.

Four layers, in gating order:
1. no collapse — valuation ratios are finite and away from any floor,
2. internal consistency — numerical elasticities match the log-linear
   solution on a fine grid,
3. grid behaviour — the risk-free rate converges monotonically and the
   premium stays positive at every grid size,
4. Table VII — simulated sample statistics sit inside the paper's own
   cross-sample dispersion bands.
"""
import numpy as np
import pytest

from lrrcs.calibration import simulate_cashflow_moments
from lrrcs.implications import compute_asset_pricing_moments, simulate_table_vii
from lrrcs.implications.figures import figure5, figure_lr_premium, figure_mean_pd
from lrrcs.model import ModelSolver, get_table_ii_params, solve_analytical
from lrrcs.model.solver import SolverDivergenceError

# Table VII, Model column: cross-sample means (and SDs) of annual stats.
PAPER_ER = {"growth": 6.07, "value": 11.36, "market": 7.53}
PAPER_ER_SD = {"growth": 2.91, "value": 4.30, "market": 2.69}
PAPER_VOL = {"growth": 21.5, "value": 29.0, "market": 20.1}
PAPER_VOL_SD = {"growth": 4.90, "value": 6.13, "market": 4.35}


@pytest.fixture(scope="module")
def paper_solver():
    """The Table II calibration solved on the paper grid (30 x 4)."""
    return ModelSolver(get_table_ii_params(), n_x=30, n_s=4).solve()


def test_solver_no_collapse(paper_solver):
    z_c = paper_solver.z_c
    assert np.all(np.isfinite(z_c))
    assert 5.0 < z_c.min() and z_c.max() < 9.0
    for name, z in paper_solver.z.items():
        assert np.all(np.isfinite(z)), name
        # nowhere near the old -27.63 price floor, nowhere explosive
        assert 1.0 < z.min() and z.max() < 16.0, name


def test_rankings_on_paper_grid(paper_solver):
    mom = compute_asset_pricing_moments(paper_solver)
    er = mom["mean_return"]
    assert er["value"] > er["market"] > er["growth"]
    # CAPM fails inside the model: value has the higher premium and the
    # lower market beta (Table VIII).
    assert mom["capm_beta"]["value"] < mom["capm_beta"]["growth"]
    lpd = mom["mean_log_pd"]
    assert lpd["value"] < lpd["market"] < lpd["growth"]


def test_table_vii_by_simulation(paper_solver):
    tab = simulate_table_vii(paper_solver, n_samples=300, years=74, seed=0)
    er = tab["mean_return"]
    assert er["value"] > er["market"] > er["growth"]
    assert 4.5 < tab["value_premium"] < 6.5          # paper: 5.29
    assert 0.3 < tab["mean_rf"] < 2.2                # paper: 1.58
    assert 0.65 < tab["beta_ratio"] < 1.0            # paper: 0.92
    lpd = tab["mean_log_pd"]
    assert lpd["value"] < lpd["market"] < lpd["growth"]   # paper: 3.10 < 3.24 < 3.65
    for name in ("growth", "value", "market"):
        assert abs(er[name] - PAPER_ER[name]) < 1.5 * PAPER_ER_SD[name], name
        assert abs(tab["volatility"][name] - PAPER_VOL[name]) < 1.5 * PAPER_VOL_SD[name], name


def test_grid_convergence():
    """rf rises monotonically with grid size; the premium never flips sign."""
    rf = []
    for n_x in (20, 40, 60):
        solver = ModelSolver(get_table_ii_params(), n_x=n_x, n_s=4).solve(tol=1e-8)
        mom = compute_asset_pricing_moments(solver)
        assert 3.0 < mom["value_premium"] < 7.0, n_x
        rf.append(mom["mean_rf"])
    assert rf[0] < rf[1] < rf[2]


def test_analytical_consistency_fine_grid():
    """Numerical dz/dx matches the self-consistent log-linear A1 (eq. 11)."""
    params = get_table_ii_params()
    solver = ModelSolver(params, n_x=60, n_s=4).solve(tol=1e-8)
    g = solver.grid
    c = params.cons
    is_mid = int(np.argmin(np.abs(g.s2_nodes - c.sigma**2)))
    mid = g.n_x // 2
    for name, d in params.dividends.items():
        z2d = solver.z[name].reshape(g.n_x, g.n_s)
        slope = ((z2d[mid + 1, is_mid] - z2d[mid - 1, is_mid])
                 / (g.x_nodes[mid + 1] - g.x_nodes[mid - 1]))
        zbar = float(np.dot(solver.stationary, solver.z[name]))
        kappa1 = np.exp(zbar) / (1 + np.exp(zbar))
        a1 = (d.phi - 1 / params.prefs.psi) / (1 - kappa1 * c.rho)
        assert abs(slope / a1 - 1.0) < 0.15, name


def test_degenerate_grid_raises_instead_of_flooring():
    """On a tiny grid the value claim's price is genuinely infinite; the
    solver must say so rather than clamp it to a floor."""
    solver = ModelSolver(get_table_ii_params(), n_x=5, n_s=2)
    with pytest.raises(SolverDivergenceError):
        solver.solve()


def test_analytical_model_column_pd_ranking():
    """Section 3.4 linearization points recover value log(P/D) < growth."""
    sol = solve_analytical(get_table_ii_params())
    assert sol.premium_lr["value"] > sol.premium_lr["growth"]
    assert sol.mean_log_pd["value"] < sol.mean_log_pd["market"] < sol.mean_log_pd["growth"]


def test_simulated_consumption_moment_ranking():
    mom = simulate_cashflow_moments(n_sims=20, years=74, seed=1)
    assert 1.0 <= mom["consumption"]["E[dc]"] <= 3.0


def test_figures_lr_and_5(tmp_path, paper_solver):
    figure_lr_premium(tmp_path / "lr.pdf")
    figure_mean_pd(paper_solver, tmp_path / "pd.pdf")
    figure5(tmp_path / "f5.pdf")
    assert (tmp_path / "lr.pdf").stat().st_size > 0
    assert (tmp_path / "f5.pdf").stat().st_size > 0
