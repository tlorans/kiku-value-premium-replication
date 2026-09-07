"""Table 4 Monte Carlo: annual specification on simulated LRR samples."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .estimate import PARAM_NAMES, estimate_bky
from .goldens import COLD_START, TABLE_2_LRR, TABLE_2_LRR_H
from .simulate import simulate_annual
from .solution import BKYParams

_ANNUAL_H = 1


def table4_annual_on_lrr_sims(
    n_draws: int = 20,
    years: int = 86,
    seed: int = 0,
    *,
    lrr_params: BKYParams | None = None,
    lrr_h: int | None = None,
    n_starts: int = 1,
    method: str = "gmm",
) -> pd.DataFrame:
    """Estimate the annual (h=1) spec on draws from an LRR economy.

    The economy is the paper's Table 2 vector at h=11 unless
    ``lrr_params`` and ``lrr_h`` say otherwise. Each draw is a
    time-aggregated annual path. ``method="gmm"`` is the same CUE as
    the empirical column, about fifteen seconds a draw at h=1;
    ``method="staged"`` is the fast SSE fit, which piles up at the
    parameter bounds on short samples and reports no ``J``. One row per
    draw with every parameter in ``PARAM_NAMES``.
    """
    economy = lrr_params if lrr_params is not None else TABLE_2_LRR
    h_econ = int(lrr_h) if lrr_h is not None else TABLE_2_LRR_H
    rows = []
    for i in range(int(n_draws)):
        sim = simulate_annual(economy, h_econ, int(years), seed=int(seed) + i)
        fit = estimate_bky(
            sim, start=COLD_START, h=_ANNUAL_H, method=method, n_starts=n_starts,
        )
        p = fit.params
        row = {"draw": i}
        row.update({name: float(getattr(p, name)) for name in PARAM_NAMES})
        row["objective"] = float(fit.gmm.objective)
        row["J"] = np.nan if fit.gmm.J is None else float(fit.gmm.J)
        row["p"] = np.nan if fit.gmm.J_pvalue is None else float(fit.gmm.J_pvalue)
        rows.append(row)
    return pd.DataFrame(rows)
