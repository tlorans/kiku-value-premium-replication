"""Table 4 right panel: annual spec estimated on LRR simulations."""
from __future__ import annotations

import pytest

from geap.lrr.estimation.monte_carlo import table4_annual_on_lrr_sims

_COLUMNS = ("draw", "gamma", "psi", "rho", "phi_e", "sigma")


def test_table4_annual_on_lrr_sims_returns_required_columns():
    frame = table4_annual_on_lrr_sims(n_draws=2, years=86, seed=0)
    assert len(frame) == 2
    for col in _COLUMNS:
        assert col in frame.columns, col
    assert "objective" in frame.columns or "J" in frame.columns
    assert frame["draw"].tolist() == [0, 1]
    assert frame["gamma"].notna().all()
    assert frame["rho"].notna().all()


@pytest.mark.slow
def test_table4_annual_on_lrr_sims_median_gamma_and_rho():
    frame = table4_annual_on_lrr_sims(n_draws=20, years=86, seed=0)
    assert len(frame) == 20
    assert float(frame["gamma"].median()) > 11.0
    assert float(frame["rho"].median()) < 0.95
