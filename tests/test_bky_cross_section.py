import pytest

from geap.lrr.estimation.cross_section import (
    estimate_table7_claims,
    table7_capm,
    table7_claims,
    table7_premia,
    table7_sample_capm,
    table7_sample_premia,
)
from geap.lrr.estimation.data import load_annual, load_cross_section
from geap.lrr.estimation.goldens import TABLE_2_LRR, TABLE_7_PHI, TABLE_7_PREMIA_MODEL

# Table 7 Panel A bootstrap SEs on φ_j (BKY 2016, p. 67).
_TABLE_7_PHI_SE = {"small": 1.45, "large": 1.85, "growth": 0.98, "value": 1.27}


def test_table7_value_loads_more_than_growth():
    claims = table7_claims(TABLE_2_LRR)
    assert claims["value"].phi_d > claims["growth"].phi_d
    assert claims["small"].phi_d > claims["large"].phi_d
    assert claims["value"].phi_d == TABLE_7_PHI["value"]


def test_table7_model_premia_match_the_paper():
    prem = table7_premia()
    for name, paper in TABLE_7_PREMIA_MODEL.items():
        assert prem[name] == pytest.approx(paper, abs=0.2), name


def test_table7_capm_replicates_the_failure():
    capm = table7_capm(years=400, seed=1)
    assert capm["value_growth"]["beta_model"] == pytest.approx(0.45, abs=0.2)
    assert capm["small_large"]["beta_model"] == pytest.approx(0.86, abs=0.2)
    assert capm["value_growth"]["alpha_model"] == pytest.approx(1.78, abs=0.6)
    assert capm["small_large"]["alpha_model"] == pytest.approx(1.63, abs=0.6)


def test_cross_section_sample_has_a_value_and_size_premium():
    panel = load_cross_section()
    means = panel.groupby("claim")["ret"].mean()
    assert float(means["value"]) > float(means["growth"])
    assert float(means["small"]) > float(means["large"])


def test_table7_sample_premia_are_positive_spreads():
    prem = table7_sample_premia(load_cross_section())
    assert prem["value"] > prem["growth"]
    assert prem["small"] > prem["large"]


def test_table7_sample_capm_betas_in_range():
    capm = table7_sample_capm(load_cross_section(), load_annual())
    for spread in ("small_large", "value_growth"):
        assert 0.0 < capm[spread]["beta_data"] < 1.2, spread
        assert "alpha_data" in capm[spread]


@pytest.fixture(scope="module")
def estimated_claims():
    return estimate_table7_claims(load_cross_section(), market_params=TABLE_2_LRR, h=11)


def test_estimate_table7_claims_holds_market_preferences(estimated_claims):
    for name, p in estimated_claims.items():
        assert p.gamma == TABLE_2_LRR.gamma, name
        assert p.psi == TABLE_2_LRR.psi, name
        assert p.mu_c == TABLE_2_LRR.mu_c, name
        assert p.rho == TABLE_2_LRR.rho, name
        assert p.phi_e == TABLE_2_LRR.phi_e, name


def test_estimated_phi_value_exceeds_growth_and_small_exceeds_large(estimated_claims):
    assert estimated_claims["value"].phi_d > estimated_claims["growth"].phi_d
    assert estimated_claims["small"].phi_d > estimated_claims["large"].phi_d


def test_estimated_claims_still_have_value_and_size_premia(estimated_claims):
    prem = table7_premia(claims=estimated_claims)
    assert prem["value"] > prem["growth"]
    assert prem["small"] > prem["large"]


def test_estimated_phi_within_two_paper_se(estimated_claims):
    for name, paper in TABLE_7_PHI.items():
        hat = estimated_claims[name].phi_d
        se = _TABLE_7_PHI_SE[name]
        assert abs(hat - paper) <= 2.0 * se, f"{name}: {hat} vs {paper} (se={se})"

