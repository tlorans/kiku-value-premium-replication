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

import lrrcs as lrr
from lrrcs.implications.figures import figure5, figure_lr_premium, figure_mean_pd

# Table VII, Model column: cross-sample means (and SDs) of annual stats.
PAPER_ER = {"growth": 6.07, "value": 11.36, "market": 7.53}
PAPER_ER_SD = {"growth": 2.91, "value": 4.30, "market": 2.69}
PAPER_VOL = {"growth": 21.5, "value": 29.0, "market": 20.1}
PAPER_VOL_SD = {"growth": 4.90, "value": 6.13, "market": 4.35}


@pytest.fixture(scope="module")
def paper_model():
    """The Table II calibration; its grid solve is cached on the model."""
    return lrr.LongRunRisksModel()


@pytest.fixture(scope="module")
def paper_results(paper_model):
    """Solved on the paper grid (30 x 4)."""
    return paper_model.solve(n_x=30, n_s=4)


def test_solver_no_collapse(paper_results):
    z_c = paper_results.z_c
    assert np.all(np.isfinite(z_c))
    assert 5.0 < z_c.min() and z_c.max() < 9.0
    for name, z in paper_results.z.items():
        assert np.all(np.isfinite(z)), name
        # nowhere near the old -27.63 price floor, nowhere explosive
        assert 1.0 < z.min() and z.max() < 16.0, name


def test_rankings_on_paper_grid(paper_results):
    er = paper_results.expected_returns
    assert er["value"] > er["market"] > er["growth"]
    # CAPM fails inside the model: value has the higher premium and the
    # lower market beta (Table VIII).
    beta = paper_results.capm_betas
    assert beta["value"] < beta["growth"]
    lpd = paper_results.mean_log_pd
    assert lpd["value"] < lpd["market"] < lpd["growth"]


def test_table_vii_by_simulation(paper_model):
    sim = paper_model.simulate(n_samples=300, years=74, seed=0)
    er = sim.expected_returns
    assert er["value"] > er["market"] > er["growth"]
    assert 4.5 < sim.value_premium < 6.5           # paper: 5.29
    assert 0.3 < sim.risk_free < 2.2               # paper: 1.58
    assert 0.65 < sim.beta_ratio < 1.0             # paper: 0.92
    lpd = sim.mean_log_pd
    assert lpd["value"] < lpd["market"] < lpd["growth"]   # paper: 3.10 < 3.24 < 3.65
    for name in ("growth", "value", "market"):
        assert abs(er[name] - PAPER_ER[name]) < 1.5 * PAPER_ER_SD[name], name
        assert abs(sim.volatility[name] - PAPER_VOL[name]) < 1.5 * PAPER_VOL_SD[name], name


def test_grid_convergence():
    """rf rises monotonically with grid size; the premium never flips sign."""
    model = lrr.LongRunRisksModel()
    rf = []
    for n_x in (20, 40, 60):
        res = model.solve(n_x=n_x, n_s=4, tol=1e-8)
        assert 3.0 < res.value_premium < 7.0, n_x
        rf.append(res.risk_free)
    assert rf[0] < rf[1] < rf[2]


def test_analytical_consistency_fine_grid():
    """Numerical dz/dx matches the self-consistent log-linear A1 (eq. 11)."""
    model = lrr.LongRunRisksModel()
    res = model.solve(n_x=60, n_s=4, tol=1e-8)
    params = res.params
    c = params.cons
    is_mid = int(np.argmin(np.abs(res.s2_nodes - c.sigma**2)))
    n_x, n_s = res.n_x, res.n_s
    mid = n_x // 2
    for name, d in params.dividends.items():
        z2d = res.z[name].reshape(n_x, n_s)
        slope = ((z2d[mid + 1, is_mid] - z2d[mid - 1, is_mid])
                 / (res.x_nodes[mid + 1] - res.x_nodes[mid - 1]))
        zbar = float(np.dot(res.stationary, res.z[name]))
        kappa1 = np.exp(zbar) / (1 + np.exp(zbar))
        a1 = (d.phi - 1 / params.prefs.psi) / (1 - kappa1 * c.rho)
        assert abs(slope / a1 - 1.0) < 0.15, name


def test_degenerate_grid_raises_instead_of_flooring():
    """On a tiny grid the value claim's price is genuinely infinite; the
    solver must say so rather than clamp it to a floor."""
    with pytest.raises(lrr.SolverDivergenceError):
        lrr.LongRunRisksModel().solve(n_x=5, n_s=2)


def test_analytical_model_column_pd_ranking():
    """Section 3.4 linearization points recover value log(P/D) < growth."""
    res = lrr.LongRunRisksModel().solve(method="analytical")
    assert res.long_run_premium["value"] > res.long_run_premium["growth"]
    assert res.mean_log_pd["value"] < res.mean_log_pd["market"] < res.mean_log_pd["growth"]


def test_simulated_consumption_moment_ranking():
    cf = lrr.LongRunRisksModel().simulate_cashflows(n_sims=20, years=74, seed=1)
    cf = cf.set_index("series")
    assert 1.0 <= cf.loc["consumption", "mean"] <= 3.0


def test_figures_lr_and_5(tmp_path, paper_results):
    figure_lr_premium(tmp_path / "lr.pdf")
    figure_mean_pd(paper_results, tmp_path / "pd.pdf")
    figure5(tmp_path / "f5.pdf")
    assert (tmp_path / "lr.pdf").stat().st_size > 0
    assert (tmp_path / "f5.pdf").stat().st_size > 0
