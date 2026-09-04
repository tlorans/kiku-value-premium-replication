"""Bansal–Kiku–Yaron (2016) GMM estimation of the long-run risks model.

This is the inverse of :class:`~geap.lrr.model.LongRunRisksModel`: data
in, parameters out. The Kiku (2006) quadrature solver is unchanged.
"""
from .aggregation import long_run_variance_share, model_moments
from .cross_section import table7_capm, table7_claims, table7_premia
from .data import (
    build_annual,
    load_annual,
    load_cross_section,
    load_quarterly,
    sample_moments,
)
from .estimate import BKYResults, estimate_bky
from .figures import figure1_frame, figure2_irf
from .tables import table3_frame, table5_frame
from .goldens import (
    COLD_START,
    TABLE_2_LRR,
    TABLE_2_LRR_H,
    TABLE_2_NOVOL,
    TABLE_2_NOVOL_H,
    TABLE_2_SE,
    TABLE_3_NOVOL_MODEL,
    TABLE_4_ANNUAL,
    TABLE_8_H,
    TABLE_8_TA,
)
from .solution import BKYParams, LogLinearSolution, solve_loglinear
from .states import extract_states

__all__ = [
    "BKYParams",
    "LogLinearSolution",
    "solve_loglinear",
    "model_moments",
    "long_run_variance_share",
    "COLD_START",
    "TABLE_2_LRR",
    "TABLE_2_LRR_H",
    "TABLE_2_SE",
    "TABLE_2_NOVOL",
    "TABLE_2_NOVOL_H",
    "TABLE_3_NOVOL_MODEL",
    "TABLE_4_ANNUAL",
    "TABLE_8_H",
    "TABLE_8_TA",
    "build_annual",
    "load_annual",
    "load_quarterly",
    "load_cross_section",
    "sample_moments",
    "BKYResults",
    "estimate_bky",
    "extract_states",
    "table7_claims",
    "table7_premia",
    "table7_capm",
    "figure1_frame",
    "figure2_irf",
    "table3_frame",
    "table5_frame",
]
