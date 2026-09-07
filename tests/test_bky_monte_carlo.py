"""Table 4 right panel: annual spec estimated on LRR simulations."""
from __future__ import annotations

import pytest

from geap.lrr.estimation.monte_carlo import table4_annual_on_lrr_sims

_COLUMNS = ("draw", "gamma", "psi", "rho", "phi_e", "sigma")


def test_table4_annual_on_lrr_sims_returns_required_columns():
    frame = table4_annual_on_lrr_sims(n_draws=2, years=86, seed=0, method="staged")
    assert len(frame) == 2
    for col in _COLUMNS:
        assert col in frame.columns, col
    assert "objective" in frame.columns or "J" in frame.columns
    assert frame["draw"].tolist() == [0, 1]
    assert frame["gamma"].notna().all()
    assert frame["rho"].notna().all()


@pytest.mark.slow
def test_table4_annual_on_lrr_sims_median_gamma_and_rho():
    frame = table4_annual_on_lrr_sims(n_draws=20, years=86, seed=0, method="staged")
    assert len(frame) == 20
    assert float(frame["gamma"].median()) > 11.0
    assert float(frame["rho"].median()) < 0.95


def test_table4_monte_carlo_records_every_parameter_and_the_fit():
    from geap.lrr.estimation.estimate import PARAM_NAMES
    from geap.lrr.estimation.goldens import TABLE_2_LRR

    frame = table4_annual_on_lrr_sims(
        n_draws=1, years=60, seed=3, lrr_params=TABLE_2_LRR, lrr_h=11, method="staged"
    )
    for name in PARAM_NAMES:
        assert name in frame.columns, name
    for col in ("draw", "objective", "J", "p"):
        assert col in frame.columns, col
    assert frame["delta"].notna().all()


@pytest.mark.slow
def test_table4_monte_carlo_cue_draws_report_j():
    frame = table4_annual_on_lrr_sims(n_draws=2, years=86, seed=0)
    assert frame["J"].notna().all()
    assert (frame["gamma"] < 20.0).all()
