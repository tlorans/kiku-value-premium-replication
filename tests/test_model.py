from lrrcs.model import (
    Dynamics,
    EpsteinZinPreferences,
    ModelParams,
    ModelSolver,
    get_table_ii_params,
    solve_analytical,
)


def test_table_ii_phi():
    p = get_table_ii_params()
    assert p.prefs.delta == 0.999
    assert p.prefs.gamma == 10.0
    assert p.prefs.psi == 1.5
    assert p.cons.rho == 0.98
    assert p.dividends["value"].phi == 6.2
    assert p.dividends["growth"].phi == 2.6
    assert p.dividends["market"].phi == 2.8


def test_analytical_value_has_higher_lr_premium():
    sol = solve_analytical(get_table_ii_params())
    assert sol.premium_lr["value"] > sol.premium_lr["growth"]


def test_tiny_solver_runs():
    solver = ModelSolver(get_table_ii_params(), n_x=5, n_s=2, n_quad=3)
    solver.solve()
    assert solver.converged
    assert "value" in solver.z
