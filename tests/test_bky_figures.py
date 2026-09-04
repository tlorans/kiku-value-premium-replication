"""Figures 1 and 2."""
from __future__ import annotations

import numpy as np
from matplotlib.figure import Figure

from geap.lrr.estimation.data import load_annual
from geap.lrr.estimation.figures import (
    _arma_coefs,
    figure1_frame,
    figure1_plot,
    figure2_irf,
    figure2_plot,
)
from geap.lrr.estimation.goldens import TABLE_2_LRR, TABLE_4_ANNUAL
from geap.lrr.estimation.simulate import simulate_annual


def test_figure1_extracts_a_state_path():
    frame = figure1_frame(load_annual())
    assert len(frame) == 86
    assert (frame["sigma2"] > 0).all()


def test_figure1_plot_has_two_axes():
    fig = figure1_plot(load_annual())
    assert isinstance(fig, Figure)
    assert len(fig.axes) == 2


def test_figure2_lrr_consumption_irf_is_more_persistent():
    irf = figure2_irf(horizon_dc=50, horizon_var=150, years=800, seed=2)
    # Cumulative consumption response stays higher under time aggregation.
    assert float(irf.loc[20, "dc_lrr"]) > float(irf.loc[20, "dc_annual"])
    assert float(irf.loc[30, "var_lrr"]) > float(irf.loc[30, "var_annual"])


def test_figure2_plot_has_two_axes():
    fig = figure2_plot(years=80, seed=0)
    assert isinstance(fig, Figure)
    assert len(fig.axes) == 2


def test_figure2_lrr_cumulative_dc_irf_at_horizon_40():
    irf = figure2_irf(years=800, seed=0)
    lrr = float(irf.loc[40, "dc_lrr"])
    annual = float(irf.loc[40, "dc_annual"])
    assert lrr > annual
    assert lrr > 1.7
    assert annual < 1.7


def test_figure2_arma_ma_coefficients_are_nonzero():
    lrr = simulate_annual(TABLE_2_LRR, 11, years=800, seed=0)
    ann = simulate_annual(TABLE_4_ANNUAL, 1, years=800, seed=1)
    for y in (lrr["dc"].to_numpy(), ann["dc"].to_numpy()):
        _phi, theta = _arma_coefs(y)
        assert theta.size == 8
        assert np.max(np.abs(theta)) > 1e-4
        assert not np.allclose(theta, 0.0, atol=1e-8)


def test_figure2_irf_horizon_alias_sets_horizon_dc():
    irf = figure2_irf(horizon=21, years=80, seed=0)
    assert int(irf["dc_lrr"].notna().sum()) == 21
    assert np.isfinite(irf.loc[20, "dc_lrr"])
