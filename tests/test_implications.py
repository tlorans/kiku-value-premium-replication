from kiku_value_premium.model import ModelSolver, get_table_ii_params, solve_analytical
from kiku_value_premium.implications import compute_asset_pricing_moments


def test_value_premium_positive_on_tiny_grid():
    solver = ModelSolver(get_table_ii_params(), n_x=5, n_s=2, n_quad=3)
    solver.solve()
    mom = compute_asset_pricing_moments(solver)
    assert mom["mean_return"]["value"] > mom["mean_return"]["growth"]
    # mean_log_pd ranking is not asserted on 5×2: the Euler map can collapse
    # every claim to the same floor z, so stationary-weighted log(P/D) ties.
    assert mom["capm_beta"]["value"] / mom["capm_beta"]["growth"] < 1.05
