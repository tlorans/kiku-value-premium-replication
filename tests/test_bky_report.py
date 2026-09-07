"""Tidy report frames with paper columns for the site pages."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from geap.gmm.results import GMMResults
from geap.lrr.estimation.cross_section import table7_claims
from geap.lrr.estimation.data import load_annual, load_cross_section
from geap.lrr.estimation.estimate import PARAM_NAMES, BKYResults
from geap.lrr.estimation.goldens import (
    TABLE_1,
    TABLE_2_LRR,
    TABLE_2_LRR_J,
    TABLE_2_NOVOL,
    TABLE_2_NOVOL_SE,
    TABLE_3_LRR_MODEL,
    TABLE_3_LRR_RESIDUALS,
    TABLE_4_ANNUAL,
    TABLE_4_SIMULATED,
    TABLE_6,
    TABLE_6_J,
    TABLE_7_CAPM,
    TABLE_7_PHI,
    TABLE_7_PREMIA_DATA,
    TABLE_7_PREMIA_MODEL,
    TABLE_8_NO_TA,
    TABLE_8_TA,
    TABLE_8_TA_SE,
)
from geap.lrr.estimation.report import (
    params_frame,
    table1_frame,
    table2_frame,
    table3_compare,
    table4_frame,
    table6_frame,
    table7_panel_a,
    table7_panel_b,
    table8_frame,
)
from geap.lrr.estimation.tables import table3_keys


def _fit(params, h, *, J=12.0, p=0.1, vol=True):
    n = 13 if vol else 11
    dummy = GMMResults(
        np.zeros(n), np.zeros(20), np.eye(20), objective=0.5, nobs=86,
        names=tuple(PARAM_NAMES[:n]), steps=1, se=np.linspace(0.1, 1.3, n),
        J=J, J_df=20 - n, J_pvalue=p,
    )
    return BKYResults(params=params, h=h, gmm=dummy, data=load_annual(), stochastic_vol=vol)


def test_table1_frame_has_paper_columns():
    tab = table1_frame(load_annual())
    assert list(tab.columns) == ["series", "ours_mean", "paper_mean", "ours_sd", "paper_sd"]
    assert len(tab) == 5
    assert tab.loc[0, "paper_mean"] == pytest.approx(TABLE_1["dc_mean"])
    assert tab.loc[4, "paper_sd"] == pytest.approx(TABLE_1["rf_std"])


def test_params_frame_rows_end_with_h_j_p():
    tab = params_frame(_fit(TABLE_2_LRR, 11), paper=TABLE_2_LRR, paper_j=TABLE_2_LRR_J)
    assert list(tab["parameter"]) == list(PARAM_NAMES) + ["h", "J", "p"]
    assert list(tab.columns) == ["parameter", "hat", "se_hat", "paper", "se_paper"]
    by = tab.set_index("parameter")
    assert by.loc["J", "hat"] == pytest.approx(12.0)
    assert by.loc["J", "paper"] == pytest.approx(10.4)
    assert by.loc["p", "paper"] == pytest.approx(0.11)
    assert by.loc["h", "paper"] == pytest.approx(11.0)
    assert np.isnan(by.loc["J", "se_hat"])


def test_table2_frame_joins_lrr_and_novol():
    tab = table2_frame(_fit(TABLE_2_LRR, 11), _fit(TABLE_2_NOVOL, 9, vol=False))
    assert list(tab["parameter"]) == list(PARAM_NAMES) + ["h", "J", "p"]
    assert list(tab.columns) == [
        "parameter", "lrr_hat", "lrr_se", "lrr_paper", "lrr_paper_se",
        "novol_hat", "novol_se", "novol_paper", "novol_paper_se",
    ]
    by = tab.set_index("parameter")
    assert np.isnan(by.loc["nu", "novol_paper"])
    assert np.isnan(by.loc["nu", "novol_hat"])
    assert by.loc["gamma", "novol_paper_se"] == pytest.approx(TABLE_2_NOVOL_SE["gamma"])
    assert by.loc["h", "novol_paper"] == pytest.approx(9.0)
    assert by.loc["J", "novol_paper"] == pytest.approx(78.5)


def test_table3_compare_adds_the_paper_model_column():
    paper = {**TABLE_3_LRR_MODEL, **TABLE_3_LRR_RESIDUALS}
    tab = table3_compare(load_annual(), _fit(TABLE_2_LRR, 11), paper)
    assert list(tab.columns) == ["moment", "sample", "model", "t_diff", "paper_model"]
    assert list(tab["moment"]) == list(table3_keys())
    assert tab["paper_model"].notna().all()


def test_table4_frame_quantiles_from_monte_carlo():
    ann = _fit(TABLE_4_ANNUAL, 1)
    empty = table4_frame(ann, None)
    assert list(empty["parameter"]) == list(PARAM_NAMES) + ["h", "J", "p"]
    assert empty["ours_p50"].isna().all()
    by = empty.set_index("parameter")
    assert by.loc["gamma", "paper_pop"] == pytest.approx(TABLE_4_SIMULATED["gamma"][0])
    assert by.loc["gamma", "paper_p95"] == pytest.approx(TABLE_4_SIMULATED["gamma"][3])
    assert np.isnan(by.loc["J", "paper_pop"])
    mc = pd.DataFrame({n: [1.0, 2.0, 3.0] for n in PARAM_NAMES})
    mc["draw"] = [0, 1, 2]
    mc["J"] = [5.0, 6.0, 7.0]
    full = table4_frame(ann, mc)
    by = full.set_index("parameter")
    assert by.loc["rho", "ours_p50"] == pytest.approx(2.0)
    assert by.loc["rho", "ours_p5"] == pytest.approx(1.1)
    assert by.loc["J", "ours_p95"] == pytest.approx(6.9)


def test_table6_frame_orders_columns_by_frequency():
    fits = {h: _fit(TABLE_6[h], h) for h in (26, 12, 4, 1)}
    tab = table6_frame(fits)
    assert list(tab.columns) == [
        "parameter", "hat_26", "paper_26", "hat_12", "paper_12",
        "hat_4", "paper_4", "hat_1", "paper_1",
    ]
    by = tab.set_index("parameter")
    assert by.loc["J", "paper_12"] == pytest.approx(TABLE_6_J[12][0])
    assert by.loc["gamma", "paper_26"] == pytest.approx(TABLE_6[26].gamma)
    assert "h" not in by.index


def test_table7_panels_carry_paper_values():
    panel = load_cross_section()
    annual = load_annual()
    claims = table7_claims(TABLE_2_LRR)
    a = table7_panel_a(claims, panel, TABLE_2_LRR, 11)
    assert list(a["claim"]) == ["small", "large", "growth", "value"]
    for col in ("mu", "phi", "phi_sigma", "rho", "premium_data", "premium_model"):
        assert col in a.columns
        assert f"{col}_paper" in a.columns
    by = a.set_index("claim")
    assert by.loc["value", "phi_paper"] == pytest.approx(TABLE_7_PHI["value"])
    assert by.loc["small", "premium_model_paper"] == pytest.approx(TABLE_7_PREMIA_MODEL["small"])
    assert by.loc["small", "premium_data_paper"] == pytest.approx(TABLE_7_PREMIA_DATA["small"])
    assert by.loc["small", "premium_model"] == pytest.approx(TABLE_7_PREMIA_MODEL["small"], abs=0.2)
    b = table7_panel_b(claims, TABLE_2_LRR, 11, panel, annual, years=200, seed=1)
    assert list(b["spread"]) == ["small_large", "value_growth"]
    for col in ("beta_data", "beta_model", "alpha_data", "alpha_model"):
        assert col in b.columns and f"{col}_paper" in b.columns
    assert b.set_index("spread").loc["value_growth", "beta_model_paper"] == pytest.approx(
        TABLE_7_CAPM["value_growth"]["beta_model"]
    )


def test_table8_frame_uses_quarterly_goldens():
    tab = table8_frame(_fit(TABLE_8_TA, 2), _fit(TABLE_8_NO_TA, 1))
    assert list(tab.columns) == [
        "parameter", "ta_hat", "ta_se", "ta_paper", "ta_paper_se",
        "nota_hat", "nota_se", "nota_paper", "nota_paper_se",
    ]
    by = tab.set_index("parameter")
    assert by.loc["h", "ta_paper"] == pytest.approx(2.0)
    assert by.loc["h", "ta_paper_se"] == pytest.approx(TABLE_8_TA_SE["h"])
    assert by.loc["h", "nota_paper"] == pytest.approx(1.0)
    assert np.isnan(by.loc["h", "nota_paper_se"])
    assert by.loc["J", "ta_paper"] == pytest.approx(13.3)
