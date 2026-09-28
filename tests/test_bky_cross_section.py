import pytest

from geap.lrr.estimation.cross_section import (
    claim_moments,
    fit_table7_claims,
    table7_capm,
    table7_claims,
    table7_contributions,
    table7_premia,
    table7_sample_capm,
    table7_sample_premia,
)
from geap.lrr.estimation.data import load_annual, load_cross_section
from geap.lrr.estimation.goldens import TABLE_2_LRR, TABLE_7_PHI, TABLE_7_PREMIA_MODEL


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
def bky_fits():
    return fit_table7_claims(load_cross_section(), market_params=TABLE_2_LRR, h=11)


@pytest.fixture(scope="module")
def estimated_claims(bky_fits):
    return {name: fit.params for name, fit in bky_fits.items()}


# Why the gate fails on small and value. Their 1930s dividend growth
# swings by up to 3.9 in logs (small, 1933: -3.94), and value misses
# 1933 and 1934. Sample vol(Δd) is 0.66 for small and 0.45 for value,
# against 0.18 and 0.15 without the |Δd| > 0.5 years, and no cash-flow
# vector at the Table 2 states comes near it (0.23 and 0.16 at the
# printed ones). The CUE puts little weight on vol(Δd), and the other
# moments then pull small's mu_j up and phi_j down, and value's rho_j
# to its bound of 1.
_GATE_XFAIL = {
    "small": "mu_j and phi_j beyond 2 SE: 1930s small-cap dividend growth, vol(dd) 0.66",
    "value": "rho_j at its bound of 1, beyond 2 SE: 1930s value dividend growth, vol(dd) 0.45",
}


def test_estimate_table7_claims_holds_market_preferences(estimated_claims):
    for name, p in estimated_claims.items():
        assert p.gamma == TABLE_2_LRR.gamma, name
        assert p.psi == TABLE_2_LRR.psi, name
        assert p.mu_c == TABLE_2_LRR.mu_c, name
        assert p.rho == TABLE_2_LRR.rho, name
        assert p.phi_e == TABLE_2_LRR.phi_e, name


def test_estimated_phi_small_exceeds_large(estimated_claims):
    assert estimated_claims["small"].phi_d > estimated_claims["large"].phi_d


@pytest.mark.xfail(strict=True, reason="value phi_j 4.8 against growth 6.8: " + _GATE_XFAIL["value"])
def test_estimated_phi_value_exceeds_growth(estimated_claims):
    assert estimated_claims["value"].phi_d > estimated_claims["growth"].phi_d


def test_estimated_claims_still_have_value_and_size_premia(estimated_claims):
    prem = table7_premia(claims=estimated_claims)
    assert prem["value"] > prem["growth"]
    assert prem["small"] > prem["large"]


@pytest.mark.parametrize(
    "name",
    [
        pytest.param(n, marks=pytest.mark.xfail(strict=True, reason=_GATE_XFAIL[n]))
        if n in _GATE_XFAIL
        else n
        for n in ("small", "large", "growth", "value")
    ],
)
def test_eq31_recovers_table7_panel_a_within_two_se(bky_fits, name):
    # The gate: BKY's eq. 31 at their Table 2 point and h = 11, on
    # 1930 to 2015, lands within two of their bootstrap SEs on every
    # cash-flow parameter of Table 7 Panel A.
    from geap.lrr.estimation.goldens import (
        TABLE_7_MU,
        TABLE_7_MU_SE,
        TABLE_7_PHI_SE,
        TABLE_7_PHI_SIGMA,
        TABLE_7_PHI_SIGMA_SE,
        TABLE_7_RHO,
        TABLE_7_RHO_SE,
    )

    p = bky_fits[name].params
    rows = (
        ("mu_d", p.mu_d, TABLE_7_MU[name], TABLE_7_MU_SE[name]),
        ("phi_d", p.phi_d, TABLE_7_PHI[name], TABLE_7_PHI_SE[name]),
        ("phi_d_sigma", p.phi_d_sigma, TABLE_7_PHI_SIGMA[name], TABLE_7_PHI_SIGMA_SE[name]),
        ("rho_d", p.rho_d, TABLE_7_RHO[name], TABLE_7_RHO_SE[name]),
    )
    far = [f"{k} {hat:.4g} vs {paper} (se {se})" for k, hat, paper, se in rows if abs(hat - paper) > 2.0 * se]
    assert not far, f"{name}: " + "; ".join(far)



def test_second_stage_targets_the_market_beta():
    from geap.lrr.estimation.cross_section import _CLAIM_MOMENTS, _model_beta
    from geap.lrr.estimation.solution import solve_loglinear

    assert "beta_mkt" in _CLAIM_MOMENTS
    sol = solve_loglinear(TABLE_2_LRR)
    assert _model_beta(sol, TABLE_2_LRR, sol, TABLE_2_LRR, same_shock=True) == pytest.approx(1.0)
    assert _model_beta(sol, TABLE_2_LRR, sol, TABLE_2_LRR) < 1.0
    claims = table7_claims(TABLE_2_LRR)
    small = _model_beta(solve_loglinear(claims["small"]), claims["small"], sol, TABLE_2_LRR)
    large = _model_beta(solve_loglinear(claims["large"]), claims["large"], sol, TABLE_2_LRR)
    assert small > large > 0.0


def test_sample_claim_targets_include_the_market_beta():
    import numpy as np

    from geap.lrr.estimation.cross_section import _align_claim, _claim_targets

    panel = load_cross_section()
    annual = load_annual().set_index("year")
    years = annual.index.to_numpy()
    dd, ret, z = _align_claim(panel, "small", years)
    tgt = _claim_targets(
        dd, ret, z,
        annual["dc"].to_numpy(dtype=float),
        annual["rf"].to_numpy(dtype=float),
        annual["rm"].to_numpy(dtype=float),
    )
    assert np.isfinite(tgt["beta_mkt"])
    assert 0.5 < tgt["beta_mkt"] < 2.0
    # Table 3: vol(r_d) is of the log return.
    assert tgt["vol_rd"] == pytest.approx(float(np.std(np.log1p(ret), ddof=1)))


def test_model_premium_is_the_one_bky_print():
    # h times the log-linear per-period premium is BKY's printed model
    # E[R_d - R_f]: Table 3 for the market, Table 7 for the claims.
    from geap.lrr.estimation.aggregation import model_moments
    from geap.lrr.estimation.goldens import TABLE_3_LRR_MODEL

    assert model_moments(TABLE_2_LRR, 11)["mean_excess"] == pytest.approx(
        TABLE_3_LRR_MODEL["mean_excess"], abs=5e-4
    )
    for name, p in table7_claims(TABLE_2_LRR).items():
        assert 100 * model_moments(p, 11)["mean_excess"] == pytest.approx(
            TABLE_7_PREMIA_MODEL[name], abs=0.1
        ), name


def test_claim_moment_conditions_follow_table3_definitions():
    import numpy as np

    panel = load_cross_section()
    cm = claim_moments(panel, "growth")
    assert cm.keys == (
        "mean_dd", "vol_dd", "corr_dc_dd", "mean_excess", "vol_rd", "mean_zd", "vol_zd", "beta_mkt",
    )
    p = table7_claims(TABLE_2_LRR)["growth"]
    g = cm.conditions(p)
    assert g.shape == (86, 8)
    from geap.lrr.estimation.aggregation import model_moments

    m = model_moments(p, 11)
    r = np.log1p(cm.ret)
    assert g[:, 4].mean() + m["vol_rd"] ** 2 == pytest.approx(np.var(r))
    assert g[:, 3].mean() + m["mean_excess"] == pytest.approx(np.mean(cm.ret - cm.rf))
    ortho = claim_moments(panel, "growth", orthogonality=True)
    assert ortho.keys[-2:] == ("e_u", "e_u_x")
    assert ortho.conditions(p).shape == (84, 10)


def test_own_years_keep_every_year_of_each_moment():
    import numpy as np

    panel = load_cross_section()
    p = table7_claims(TABLE_2_LRR)["value"]
    common = claim_moments(panel, "value").conditions(p)
    own = claim_moments(panel, "value", common_years=False).conditions(p)
    # Value misses dividend growth in 1933 and 1934 and P/D in 1933.
    assert common.shape == (84, 8)
    assert own.shape == (86, 8)
    cm = claim_moments(panel, "value", common_years=False)
    ok = np.isfinite(cm.ret) & np.isfinite(cm.rf)
    from geap.lrr.estimation.aggregation import model_moments

    m = model_moments(p, 11)
    assert own[:, 3].mean() + m["mean_excess"] == pytest.approx(np.mean((cm.ret - cm.rf)[ok]))


def test_eq31_fit_reports_j_and_beats_the_printed_point(bky_fits):
    import numpy as np

    contrib = table7_contributions(load_cross_section(), table7_claims(TABLE_2_LRR))
    for name, fit in bky_fits.items():
        assert fit.J_df == 4, name
        assert np.isfinite(fit.J) and 0.0 <= fit.J_pvalue <= 1.0, name
        assert abs(fit.params.rho_d) <= 1.0 and fit.params.phi_d_sigma > 0.0, name
        at_paper = contrib.loc[contrib["claim"] == name]
        assert at_paper["share"].sum() == pytest.approx(1.0)
        assert fit.objective <= at_paper["term"].sum() + 1e-9, name
        assert sum(fit.contributions().values()) == pytest.approx(fit.objective)
