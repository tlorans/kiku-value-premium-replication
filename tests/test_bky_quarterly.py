"""Table 8: quarterly GMM with and without time aggregation."""
from __future__ import annotations

import numpy as np
import pytest

from geap.lrr.estimation.data import load_quarterly
from geap.lrr.estimation.estimate import estimate_bky
from geap.lrr.estimation.goldens import (
    COLD_START,
    TABLE_8_H,
    TABLE_8_NO_TA,
    TABLE_8_TA,
)
from geap.lrr.estimation.moments import MOMENT_NAMES, observation_moments


def test_quarterly_panel_has_date_not_year():
    q = load_quarterly()
    assert list(q.columns) == ["date", "dc", "dd", "rm", "log_pd", "rf"]
    assert "year" not in q.columns
    assert q["date"].dt.year.min() == 1948
    assert q["date"].dt.year.max() == 2015
    assert len(q) == 272


def test_observation_moments_on_quarterly_at_table8():
    q = load_quarterly()
    g = observation_moments(q, TABLE_8_TA, TABLE_8_H)
    assert g.shape == (len(q) - 3, len(MOMENT_NAMES))
    assert np.all(np.isfinite(g))
    g0 = observation_moments(q, TABLE_8_NO_TA, 1)
    assert g0.shape == (len(q) - 3, len(MOMENT_NAMES))
    assert np.all(np.isfinite(g0))


def test_cold_start_is_not_table8():
    assert abs(COLD_START.gamma - TABLE_8_TA.gamma) > 0.2
    assert abs(COLD_START.psi - TABLE_8_TA.psi) > 0.2
    assert TABLE_8_NO_TA.gamma > TABLE_8_TA.gamma


def test_quarterly_panel_is_four_samples_per_year():
    from geap.lrr.estimation.estimate import _samples_per_year
    from geap.lrr.estimation.data import load_annual

    assert _samples_per_year(load_quarterly()) == 4
    assert _samples_per_year(load_annual()) == 1


def test_quarterly_start_rescales_from_monthly_not_as_if_annual():
    from geap.lrr.estimation.estimate import _start_at_h

    mean_dc = float(load_quarterly()["dc"].mean())
    p1 = _start_at_h(COLD_START, 1, mean_dc, samples_per_year=4)
    p2 = _start_at_h(COLD_START, 2, mean_dc, samples_per_year=4)
    # h=1 is a quarterly decision (4/year): k=12/4=3, not k=12.
    assert p1.rho == pytest.approx(COLD_START.rho ** 3, rel=1e-10)
    assert p1.sigma == pytest.approx(COLD_START.sigma * 3**0.5, rel=1e-10)
    # h=2 is 8 decisions/year: k=12/8=1.5, not the unscaled monthly start.
    assert p2.rho == pytest.approx(COLD_START.rho ** 1.5, rel=1e-10)
    assert p2.sigma == pytest.approx(COLD_START.sigma * 1.5**0.5, rel=1e-10)
    assert p1.mu_c == pytest.approx(mean_dc)
    assert p2.mu_c == pytest.approx(mean_dc / 2.0)


def test_annual_h11_start_keeps_monthly_persistence():
    from geap.lrr.estimation.data import load_annual
    from geap.lrr.estimation.estimate import _start_at_h

    mean_dc = float(load_annual()["dc"].mean())
    p = _start_at_h(COLD_START, 11, mean_dc, samples_per_year=1)
    assert p.rho == pytest.approx(COLD_START.rho)
    assert p.sigma == pytest.approx(COLD_START.sigma)
    assert p.mu_c == pytest.approx(mean_dc / 11.0)


def test_quarterly_default_h_grid_is_one_through_four():
    q = load_quarterly()
    fit = estimate_bky(q, start=COLD_START, method="staged")
    assert fit.h in (1, 2, 3, 4)


def test_staged_quarterly_gmm_from_cold_start():
    q = load_quarterly()
    fit = estimate_bky(q, start=COLD_START, h_grid=(1, 2, 3, 4), method="staged")
    fit0 = estimate_bky(q, start=COLD_START, h=1, method="staged")
    assert fit.h in (1, 2, 3, 4)
    assert fit0.h == 1
    assert np.isfinite(fit.params.gamma)
    assert np.isfinite(fit0.params.gamma)


@pytest.mark.slow
def test_quarterly_gmm_from_cold_start():
    q = load_quarterly()
    fit = estimate_bky(q, start=COLD_START, h_grid=(1, 2, 3, 4))
    fit0 = estimate_bky(q, start=COLD_START, h=1)
    assert fit.h in (1, 2, 3, 4)
    assert fit0.h == 1
    assert 5.0 <= fit.params.gamma <= 20.0
    assert 5.0 <= fit0.params.gamma <= 20.0
    assert np.isfinite(fit.gmm.objective)
    assert fit.gmm.J_pvalue is not None
    # Paper: ignoring TA raises gamma (8.66 vs 7.45). CUE on this panel
    # reverses that (task-10-report); do not gate on the ranking.
