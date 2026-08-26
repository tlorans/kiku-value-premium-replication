"""
Step 4 of Kiku’s recipe – Epstein–Zin recursive preferences
===========================================================

Agents with these preferences care about long-run growth prospects and
uncertainty.  Combined with heterogeneous long-run leverages (Step 2),
this generates large cross-sectional differences in risk premia.
"""

import numpy as np
from .params import PreferencesParams


class EpsteinZinPreferences:
    """Epstein–Zin preferences and the intertemporal marginal rate of substitution."""

    def __init__(self, params: PreferencesParams = None):
        self.p = params or PreferencesParams()

    @property
    def theta(self) -> float:
        return self.p.theta

    def imrs(self, delta_c: float, r_c: float) -> float:
        """
        Log intertemporal marginal rate of substitution:

            m = θ·log(δ) − (θ/ψ)·Δc + (θ−1)·r_c
        """
        return (self.p.theta * np.log(self.p.delta)
                - (self.p.theta / self.p.psi) * delta_c
                + (self.p.theta - 1) * r_c)

    def imrs_vectorized(self, delta_c: np.ndarray, r_c: np.ndarray) -> np.ndarray:
        return (self.p.theta * np.log(self.p.delta)
                - (self.p.theta / self.p.psi) * delta_c
                + (self.p.theta - 1) * r_c)
