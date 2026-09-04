"""Table 4 Monte Carlo: annual specification on simulated LRR samples."""
from __future__ import annotations

import numpy as np
import pandas as pd

from .estimate import estimate_bky
from .goldens import COLD_START, TABLE_2_LRR, TABLE_2_LRR_H
from .simulate import simulate_annual

_ANNUAL_H = 1


def table4_annual_on_lrr_sims(
    n_draws: int = 20,
    years: int = 86,
    seed: int = 0,
) -> pd.DataFrame:
    """Estimate the annual (h=1) spec on draws from the Table 2 LRR economy.

    Each draw is a time-aggregated annual path at h=11. Estimation is
    staged SSE; full CUE is too slow for a Monte Carlo of this size.
    """
    rows = []
    for i in range(int(n_draws)):
        sim = simulate_annual(
            TABLE_2_LRR, TABLE_2_LRR_H, int(years), seed=int(seed) + i,
        )
        fit = estimate_bky(sim, start=COLD_START, h=_ANNUAL_H, method="staged")
        p = fit.params
        j_stat = fit.gmm.J
        rows.append(
            {
                "draw": i,
                "gamma": float(p.gamma),
                "psi": float(p.psi),
                "rho": float(p.rho),
                "phi_e": float(p.phi_e),
                "sigma": float(p.sigma),
                "objective": float(fit.gmm.objective),
                "J": float(j_stat) if j_stat is not None else np.nan,
            }
        )
    return pd.DataFrame(rows)
