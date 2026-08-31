import lrrcs as lrr
from lrrcs.model import Dynamics, EpsteinZinPreferences, ModelParams


def test_table_ii_phi():
    p = lrr.ModelParams()
    assert p.prefs.delta == 0.999
    assert p.prefs.gamma == 10.0
    assert p.prefs.psi == 1.5
    assert p.cons.rho == 0.98
    assert p.claims["value"].phi == 6.2
    assert p.claims["growth"].phi == 2.6
    assert p.claims["market"].phi == 2.8


def test_analytical_value_has_higher_lr_premium():
    res = lrr.LongRunRisksModel().solve(method="analytical")
    assert res.long_run_premium["value"] > res.long_run_premium["growth"]


def test_small_solver_runs():
    # 15 x 4 is the smallest grid on which every claim has a finite price
    res = lrr.LongRunRisksModel().solve(n_x=15, n_s=4)
    assert res.converged
    assert "value" in res.z
