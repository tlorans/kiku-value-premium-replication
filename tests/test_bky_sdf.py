"""SDF permanent / transitory split (BKY 2016 JME eq. 32)."""
from __future__ import annotations

import pytest

from geap.lrr.estimation.goldens import TABLE_2_LRR, TABLE_2_LRR_H
from geap.lrr.estimation.sdf import sdf_component_vols, sdf_loadings
from geap.lrr.estimation.solution import solve_loglinear


def test_sdf_loadings_match_equation_32():
    p = TABLE_2_LRR
    sol = solve_loglinear(p)
    lam = sdf_loadings(p)
    assert set(lam) == {"lambda1", "lambda2", "lambda3", "lambda4"}
    assert lam["lambda1"] == pytest.approx(p.gamma)
    assert lam["lambda2"] == pytest.approx(sol.A_c1 * p.phi_e)
    # Permanent vol loading is the BN coefficient on σ_w w.
    perm_w = -sol.Lambda[2] + sol.Gamma[2] / (1.0 - p.nu)
    assert lam["lambda3"] == pytest.approx(perm_w)
    assert lam["lambda3"] + lam["lambda4"] == pytest.approx(-sol.Lambda[2])


def test_one_month_vols_match_paper():
    vols = sdf_component_vols(TABLE_2_LRR, 1)
    assert set(vols) == {"total", "growth_perm", "vol_perm"}
    assert vols["total"] == pytest.approx(0.15, abs=0.02)
    assert vols["growth_perm"] == pytest.approx(0.11, abs=0.02)
    assert vols["vol_perm"] == pytest.approx(0.04, abs=0.02)


def test_five_year_vols_match_paper_at_decision_frequency():
    # Five years at ĥ = 11 is 55 decision periods.
    vols = sdf_component_vols(TABLE_2_LRR, 5 * TABLE_2_LRR_H)
    assert vols["total"] == pytest.approx(1.11, abs=0.08)
    assert vols["growth_perm"] == pytest.approx(0.86, abs=0.08)
    assert vols["vol_perm"] == pytest.approx(0.31, abs=0.08)


def test_permanent_components_scale_with_sqrt_horizon():
    one = sdf_component_vols(TABLE_2_LRR, 1)
    five = sdf_component_vols(TABLE_2_LRR, 5 * TABLE_2_LRR_H)
    n = 5 * TABLE_2_LRR_H
    assert five["growth_perm"] == pytest.approx(one["growth_perm"] * n**0.5)
    assert five["vol_perm"] == pytest.approx(one["vol_perm"] * n**0.5)
