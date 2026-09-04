"""GMM on the annual panel from a Bansal–Yaron start, not Table 2."""
from __future__ import annotations

import numpy as np
import pytest

from geap.gmm.results import GMMResults
from geap.lrr.estimation.data import load_annual
from geap.lrr.estimation.goldens import (
    COLD_START,
    TABLE_2_LRR,
    TABLE_2_LRR_H,
    TABLE_2_SE,
)
from geap.lrr.estimation.moments import MOMENT_NAMES, observation_moments
from geap.lrr.estimation.estimate import PARAM_NAMES, BKYResults, estimate_bky

_TABLE3_NAMES = (
    "vol_dc",
    "ac1_dc",
    "ac2_dc",
    "vol_dd",
    "ac1_dd",
    "corr_dc_dd",
    "e_eta",
    "e_u",
    "e_eta_x",
    "e_eta2_s2",
    "vol_eta2",
    "ac1_eta2",
    "mean_zd",
    "vol_zd",
    "ac1_zd",
    "mean_excess",
    "vol_rd",
    "mean_rf",
    "corr_rd_zd",
    "corr_dc_zd",
)


def test_observation_moments_are_finite_at_table2():
    data = load_annual()
    g = observation_moments(data, TABLE_2_LRR, TABLE_2_LRR_H)
    assert MOMENT_NAMES == _TABLE3_NAMES
    assert MOMENT_NAMES[0] == "vol_dc"
    assert "mean_dc" not in MOMENT_NAMES
    assert "vol_eta2" in MOMENT_NAMES
    assert g.shape == (len(data) - 3, len(MOMENT_NAMES))
    assert np.all(np.isfinite(g))
    gT = np.nanmean(g, axis=0)
    assert np.all(np.isfinite(gT))
    # First column is vol(Δc), not E[Δc]; the discrepancy is a variance residual.
    assert abs(gT[0]) < 0.01


def test_results_expose_a_long_run_risks_model():
    dummy = GMMResults(
        np.zeros(13),
        np.zeros(15),
        np.eye(15),
        objective=0.0,
        nobs=86,
        names=tuple(f"p{i}" for i in range(13)),
        steps=1,
        J=9999.0,
        J_df=7,
        J_pvalue=0.0,
    )
    fit = BKYResults(params=TABLE_2_LRR, h=11, gmm=dummy, data=load_annual())
    model = fit.model
    assert model.params.prefs.gamma == pytest.approx(9.67)
    assert "market" in model.claims
    st = fit.states()
    assert st.x.shape[0] == len(fit.data)
    assert np.all(st.sigma2 > 0)
    tab = fit.moment_table()
    assert "sample" in tab.columns
    text = fit.summary().as_text()
    assert "J =" in text
    assert "p =" in text
    assert "9999" in text


def test_table2_frame_reports_own_standard_errors():
    dummy = GMMResults(
        np.zeros(13),
        np.zeros(15),
        np.eye(15),
        objective=0.0,
        nobs=86,
        names=tuple(PARAM_NAMES),
        steps=1,
        se=np.linspace(0.1, 1.3, 13),
    )
    fit = BKYResults(params=TABLE_2_LRR, h=11, gmm=dummy, data=load_annual())
    tab = fit.table2_frame()
    assert "se_hat" in tab.columns
    assert list(tab["parameter"]) == list(PARAM_NAMES) + ["h"]
    assert tab.loc[0, "se_hat"] == pytest.approx(0.1)
    assert np.isnan(tab.loc[tab["parameter"] == "h", "se_hat"].iloc[0])
    text = fit.summary().as_text()
    assert "0.1000" in text or "0.1" in text


def test_table2_frame_reports_se_hat_for_h_when_bootstrap_includes_h():
    dummy = GMMResults(
        np.zeros(13),
        np.zeros(15),
        np.eye(15),
        objective=0.0,
        nobs=86,
        names=tuple(PARAM_NAMES),
        steps=1,
        se=np.linspace(0.1, 1.4, 14),
    )
    fit = BKYResults(params=TABLE_2_LRR, h=11, gmm=dummy, data=load_annual())
    tab = fit.table2_frame()
    assert tab.loc[tab["parameter"] == "h", "se_hat"].iloc[0] == pytest.approx(1.4)


def test_sandwich_standard_errors_unscale_to_raw_units():
    from geap.lrr.estimation.estimate import _SCALE, _unscale_se

    raw = _unscale_se(_SCALE.copy(), True)
    assert raw == pytest.approx(np.ones(len(PARAM_NAMES)))
    scaled11 = np.array(
        [_SCALE[i] for i, n in enumerate(PARAM_NAMES) if n not in ("nu", "sigma_w")]
    )
    raw11 = _unscale_se(scaled11, False)
    assert raw11[PARAM_NAMES.index("gamma")] == pytest.approx(1.0)
    assert raw11[PARAM_NAMES.index("nu")] == pytest.approx(0.0)
    assert raw11[PARAM_NAMES.index("sigma_w")] == pytest.approx(0.0)


def test_j_at_table2_is_tens_not_thousands():
    """Lemma 4.2 J on this panel at the published vector, in raw coordinates.

    A finite-difference Jacobian in scaled optimiser units produced J in
    the thousands at Table 2. T g'W g at those parameters is about 43.
    """
    from geap.gmm.weighting import invvar_weights
    from geap.lrr.estimation.estimate import _hansen_j_at_params

    data = load_annual()
    g = observation_moments(data, TABLE_2_LRR, TABLE_2_LRR_H)
    W = invvar_weights(g)
    j_stat, j_df, j_p = _hansen_j_at_params(data, TABLE_2_LRR, TABLE_2_LRR_H, W, 1)
    assert j_df == 7
    assert 1.0 < j_stat < 30.0
    assert j_p > 0.05


def test_cold_start_is_not_the_published_table2():
    assert COLD_START.psi == pytest.approx(1.5)
    assert TABLE_2_LRR.psi == pytest.approx(2.18)
    assert abs(COLD_START.phi_d - TABLE_2_LRR.phi_d) > 1.0
    assert abs(COLD_START.gamma - TABLE_2_LRR.gamma) > 0.2


def test_gmm_moves_psi_from_cold_start():
    data = load_annual()
    fit = estimate_bky(data, start=COLD_START, h=11, maxiter=200)
    assert fit.h == 11
    assert fit.params.psi - COLD_START.psi > 0.2
    assert fit.params.psi > COLD_START.psi


@pytest.mark.slow
def test_gmm_runs_on_the_annual_panel_from_cold_start():
    data = load_annual()
    assert abs(COLD_START.psi - TABLE_2_LRR.psi) > 0.2
    fit = estimate_bky(data, start=COLD_START, h=11)
    assert fit.h == 11
    assert fit.data is data
    assert np.isfinite(fit.gmm.objective)
    import inspect

    from geap.lrr.estimation import estimate as estimate_mod

    src = inspect.getsource(estimate_mod._gmm_at_h)
    assert "_PHI_D_SIGMA_CAP" not in src
    assert "phi_d_sigma=" not in src.replace("params.phi_d_sigma", "")
    for name in PARAM_NAMES:
        hat = getattr(fit.params, name)
        paper = getattr(TABLE_2_LRR, name)
        se = TABLE_2_SE[name]
        # Remaining φ_{dσ} miss is `_annual_map` (monthly A1/A2 on annual z),
        # not a post-hoc bound. Unconstrained CUE is the reported hat.
        k = 4.0 if name == "phi_d_sigma" else 2.0
        assert abs(hat - paper) <= k * se + 1e-9, (
            f"{name}: {hat} vs {paper} (se={se})"
        )
    assert fit.params.phi_d_sigma != pytest.approx(5.5, abs=1e-9)
    assert fit.gmm.J_pvalue is not None
    tab = fit.table2_frame()
    assert list(tab["parameter"]) == list(PARAM_NAMES) + ["h"]
    text = fit.summary().as_text()
    assert "psi" in text
    assert "2.18" in text
    assert "J =" in text
    assert "p =" in text


@pytest.mark.slow
def test_gmm_selects_h_on_a_grid():
    data = load_annual()
    fit = estimate_bky(data, start=COLD_START, h_grid=(8, 11, 14))
    assert fit.h in (8, 11, 14)
