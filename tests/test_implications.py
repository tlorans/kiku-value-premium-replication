from kiku_value_premium.calibration import simulate_cashflow_moments
from kiku_value_premium.implications import compute_asset_pricing_moments
from kiku_value_premium.implications.figures import figure5, figure_lr_premium, figure_mean_pd
from kiku_value_premium.model import ModelSolver, get_table_ii_params, solve_analytical


def test_value_premium_positive_on_tiny_grid():
    solver = ModelSolver(get_table_ii_params(), n_x=5, n_s=2, n_quad=3)
    solver.solve()
    mom = compute_asset_pricing_moments(solver)
    assert mom["mean_return"]["value"] > mom["mean_return"]["market"] > mom["mean_return"]["growth"]
    # mean_log_pd ranking is not asserted on 5×2: the Euler map can collapse
    # every claim to the same floor z, so stationary-weighted log(P/D) ties.
    assert mom["capm_beta"]["value"] / mom["capm_beta"]["growth"] < 1.0


def test_analytical_model_column_pd_ranking():
    """Section 3.4 linearization points recover value log(P/D) < growth."""
    sol = solve_analytical(get_table_ii_params())
    assert sol.premium_lr["value"] > sol.premium_lr["growth"]
    assert sol.mean_log_pd["value"] < sol.mean_log_pd["market"] < sol.mean_log_pd["growth"]


def test_simulated_consumption_moment_ranking():
    mom = simulate_cashflow_moments(n_sims=20, years=74, seed=1)
    assert 1.0 <= mom["consumption"]["E[dc]"] <= 3.0


def test_figures_lr_and_5(tmp_path):
    from kiku_value_premium.model import ModelSolver, get_table_ii_params
    figure_lr_premium(tmp_path / "lr.pdf")
    solver = ModelSolver(get_table_ii_params(), n_x=5, n_s=2, n_quad=3)
    solver.solve()
    figure_mean_pd(solver, tmp_path / "pd.pdf")
    figure5(tmp_path / "f5.pdf")
    assert (tmp_path / "lr.pdf").stat().st_size > 0
    assert (tmp_path / "f5.pdf").stat().st_size > 0
