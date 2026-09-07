"""Tidy frames with the paper's printed values beside ours.

Every function returns a :class:`pandas.DataFrame` that a site cell wraps in
a ``great_tables.GT``. ``paper`` columns come from :mod:`goldens`; a cell the
paper does not print is ``NaN``.
"""
from __future__ import annotations

from collections.abc import Mapping

import numpy as np
import pandas as pd

from .cross_section import (
    table7_capm,
    table7_premia,
    table7_sample_capm,
    table7_sample_premia,
)
from .data import sample_moments
from .estimate import PARAM_NAMES, BKYResults
from .goldens import (
    TABLE_1,
    TABLE_2_LRR,
    TABLE_2_LRR_H,
    TABLE_2_LRR_J,
    TABLE_2_NOVOL,
    TABLE_2_NOVOL_H,
    TABLE_2_NOVOL_J,
    TABLE_2_NOVOL_SE,
    TABLE_2_SE,
    TABLE_4_ANNUAL,
    TABLE_4_J,
    TABLE_4_SE,
    TABLE_4_SIMULATED,
    TABLE_4_SIMULATED_J,
    TABLE_6,
    TABLE_6_J,
    TABLE_7_CAPM,
    TABLE_7_MU,
    TABLE_7_MU_SE,
    TABLE_7_PHI,
    TABLE_7_PHI_SE,
    TABLE_7_PHI_SIGMA,
    TABLE_7_PHI_SIGMA_SE,
    TABLE_7_PREMIA_DATA,
    TABLE_7_PREMIA_MODEL,
    TABLE_7_RHO,
    TABLE_7_RHO_SE,
    TABLE_8_H,
    TABLE_8_NO_TA,
    TABLE_8_NO_TA_J,
    TABLE_8_NO_TA_SE,
    TABLE_8_TA,
    TABLE_8_TA_J,
    TABLE_8_TA_SE,
)
from .solution import BKYParams
from .tables import table3_frame

_TABLE1_ROWS = (
    ("dc", "Consumption growth"),
    ("dd", "Dividend growth"),
    ("rm", "Market return"),
    ("log_pd", "Log (P/D)"),
    ("rf", "Risk-free rate"),
)
_CLAIMS = ("small", "large", "growth", "value")
_SPREADS = ("small_large", "value_growth")
_FIXED_NOVOL = ("nu", "sigma_w")


def table1_frame(data: pd.DataFrame) -> pd.DataFrame:
    """Table 1: sample mean and standard deviation, ours beside the paper's."""
    samp = sample_moments(data)
    rows = []
    for key, label in _TABLE1_ROWS:
        rows.append(
            {
                "series": label,
                "ours_mean": samp[f"{key}_mean"],
                "paper_mean": TABLE_1[f"{key}_mean"],
                "ours_sd": samp[f"{key}_std"],
                "paper_sd": TABLE_1[f"{key}_std"],
            }
        )
    return pd.DataFrame(rows)


def params_frame(
    res: BKYResults,
    *,
    paper: BKYParams,
    paper_se: Mapping[str, float] | None = None,
    paper_h: float | None = None,
    paper_j: tuple[float, float] | None = None,
) -> pd.DataFrame:
    """One estimated column: hats, own SEs, the printed vector, printed SEs.

    Rows are ``PARAM_NAMES`` then ``h``, ``J``, ``p``. Parameters the
    specification fixes (nu and sigma_w under No-Vol) are ``NaN`` in
    every column, as the paper prints nothing for them.
    """
    se = dict(paper_se) if paper_se is not None else {}
    base = res.table2_frame(paper=paper, paper_se=se, paper_h=paper_h)
    tab = base[["parameter", "hat", "se_hat", "paper", "se"]].rename(
        columns={"se": "se_paper"}
    )
    if not res.stochastic_vol:
        mask = tab["parameter"].isin(_FIXED_NOVOL)
        tab.loc[mask, ["hat", "se_hat", "paper", "se_paper"]] = np.nan
    j_hat = np.nan if res.gmm.J is None else float(res.gmm.J)
    p_hat = np.nan if res.gmm.J_pvalue is None else float(res.gmm.J_pvalue)
    j_paper, p_paper = paper_j if paper_j is not None else (np.nan, np.nan)
    extra = pd.DataFrame(
        [
            {"parameter": "J", "hat": j_hat, "se_hat": np.nan, "paper": j_paper, "se_paper": np.nan},
            {"parameter": "p", "hat": p_hat, "se_hat": np.nan, "paper": p_paper, "se_paper": np.nan},
        ]
    )
    return pd.concat([tab, extra], ignore_index=True)


def _rename(tab: pd.DataFrame, prefix: str) -> pd.DataFrame:
    return tab.rename(
        columns={
            "hat": f"{prefix}_hat",
            "se_hat": f"{prefix}_se",
            "paper": f"{prefix}_paper",
            "se_paper": f"{prefix}_paper_se",
        }
    )


def _join(left: pd.DataFrame, lprefix: str, right: pd.DataFrame, rprefix: str) -> pd.DataFrame:
    return _rename(left, lprefix).merge(_rename(right, rprefix), on="parameter", how="left")


def table2_frame(lrr: BKYResults, novol: BKYResults) -> pd.DataFrame:
    """Table 2: LRR and No-Vol columns side by side."""
    left = params_frame(
        lrr, paper=TABLE_2_LRR, paper_se=TABLE_2_SE, paper_h=TABLE_2_LRR_H, paper_j=TABLE_2_LRR_J
    )
    right = params_frame(
        novol,
        paper=TABLE_2_NOVOL,
        paper_se=TABLE_2_NOVOL_SE,
        paper_h=TABLE_2_NOVOL_H,
        paper_j=TABLE_2_NOVOL_J,
    )
    return _join(left, "lrr", right, "novol")


def table3_compare(
    data: pd.DataFrame,
    res: BKYResults,
    paper_model: Mapping[str, float],
    *,
    hac_lags: int = 1,
) -> pd.DataFrame:
    """Table 3 or 5: sample, model at the hats, t(diff), and the printed model column."""
    tab = table3_frame(data, res.params, res.h, hac_lags=hac_lags)
    tab["paper_model"] = [float(paper_model.get(k, np.nan)) for k in tab["moment"]]
    return tab


def table4_frame(ann: BKYResults, mc: pd.DataFrame | None = None) -> pd.DataFrame:
    """Table 4: annual specification, empirical and simulated columns.

    ``mc`` is :func:`monte_carlo.table4_annual_on_lrr_sims` output; its
    5, 50, and 95 percent quantiles fill ``ours_p5/p50/p95``. The paper's
    population column has no counterpart here.
    """
    tab = params_frame(
        ann, paper=TABLE_4_ANNUAL, paper_se=TABLE_4_SE, paper_h=1.0, paper_j=TABLE_4_J
    )
    for col, idx in (("paper_pop", 0), ("paper_p5", 1), ("paper_p50", 2), ("paper_p95", 3)):
        values = []
        key = col.replace("paper_", "")
        for name in tab["parameter"]:
            if name in TABLE_4_SIMULATED:
                values.append(TABLE_4_SIMULATED[name][idx])
            elif name == "J" and key in TABLE_4_SIMULATED_J:
                values.append(TABLE_4_SIMULATED_J[key][0])
            elif name == "p" and key in TABLE_4_SIMULATED_J:
                values.append(TABLE_4_SIMULATED_J[key][1])
            else:
                values.append(np.nan)
        tab[col] = values
    for col, q in (("ours_p5", 0.05), ("ours_p50", 0.50), ("ours_p95", 0.95)):
        values = []
        for name in tab["parameter"]:
            if mc is not None and name in mc.columns and mc[name].notna().any():
                values.append(float(np.nanquantile(mc[name].to_numpy(dtype=float), q)))
            else:
                values.append(np.nan)
        tab[col] = values
    return tab


def table6_frame(fits: Mapping[int, BKYResults]) -> pd.DataFrame:
    """Table 6: fixed decision frequencies, ``hat_h`` beside ``paper_h``."""
    out: pd.DataFrame | None = None
    for h in (26, 12, 4, 1):
        tab = params_frame(fits[h], paper=TABLE_6[h], paper_j=TABLE_6_J[h])
        tab = tab[tab["parameter"] != "h"][["parameter", "hat", "paper"]].rename(
            columns={"hat": f"hat_{h}", "paper": f"paper_{h}"}
        )
        out = tab if out is None else out.merge(tab, on="parameter", how="left")
    assert out is not None
    return out


def table7_panel_a(
    claims: Mapping[str, BKYParams],
    panel: pd.DataFrame,
    market: BKYParams,
    h: int,
) -> pd.DataFrame:
    """Table 7 Panel A: cash-flow parameters and risk premia by claim."""
    prem_model = table7_premia(market, h, claims=dict(claims))
    prem_data = table7_sample_premia(panel)
    rows = []
    for name in _CLAIMS:
        p = claims[name]
        rows.append(
            {
                "claim": name,
                "mu": p.mu_d,
                "mu_paper": TABLE_7_MU[name],
                "mu_paper_se": TABLE_7_MU_SE[name],
                "phi": p.phi_d,
                "phi_paper": TABLE_7_PHI[name],
                "phi_paper_se": TABLE_7_PHI_SE[name],
                "phi_sigma": p.phi_d_sigma,
                "phi_sigma_paper": TABLE_7_PHI_SIGMA[name],
                "phi_sigma_paper_se": TABLE_7_PHI_SIGMA_SE[name],
                "rho": p.rho_d,
                "rho_paper": TABLE_7_RHO[name],
                "rho_paper_se": TABLE_7_RHO_SE[name],
                "premium_data": prem_data[name],
                "premium_data_paper": TABLE_7_PREMIA_DATA[name],
                "premium_model": prem_model[name],
                "premium_model_paper": TABLE_7_PREMIA_MODEL[name],
            }
        )
    return pd.DataFrame(rows)


def table7_panel_b(
    claims: Mapping[str, BKYParams],
    market: BKYParams,
    h: int,
    panel: pd.DataFrame,
    annual: pd.DataFrame,
    *,
    years: int = 2000,
    seed: int = 1,
) -> pd.DataFrame:
    """Table 7 Panel B: CAPM beta and alpha of the two spreads, data and model."""
    model = table7_capm(market, h, years=years, seed=seed, claims=dict(claims))
    data = table7_sample_capm(panel, annual)
    rows = []
    for spread in _SPREADS:
        paper = TABLE_7_CAPM[spread]
        rows.append(
            {
                "spread": spread,
                "beta_data": data[spread]["beta_data"],
                "beta_data_paper": paper["beta_data"],
                "beta_model": model[spread]["beta_model"],
                "beta_model_paper": paper["beta_model"],
                "alpha_data": data[spread]["alpha_data"],
                "alpha_data_paper": paper["alpha_data"],
                "alpha_model": model[spread]["alpha_model"],
                "alpha_model_paper": paper["alpha_model"],
            }
        )
    return pd.DataFrame(rows)


def table8_frame(ta: BKYResults, no_ta: BKYResults) -> pd.DataFrame:
    """Table 8: post-war quarterly, with and without time aggregation."""
    left = params_frame(
        ta, paper=TABLE_8_TA, paper_se=TABLE_8_TA_SE, paper_h=TABLE_8_H, paper_j=TABLE_8_TA_J
    )
    right = params_frame(
        no_ta, paper=TABLE_8_NO_TA, paper_se=TABLE_8_NO_TA_SE, paper_h=1.0, paper_j=TABLE_8_NO_TA_J
    )
    return _join(left, "ta", right, "nota")
