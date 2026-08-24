"""
Epstein-Zin recursive preferences and IMRS.
"""

import numpy as np
from .params import PreferencesParams


class EpsteinZinPreferences:
    def __init__(self, params: PreferencesParams = None):
        self.p = params or PreferencesParams()

    @property
    def theta(self) -> float:
        return self.p.theta

    def imrs(self, delta_c: float, r_c: float) -> float:
        """
        Log IMRS: m = theta * log(delta) - (theta / psi) * delta_c + (theta - 1) * r_c
        """
        return (self.p.theta * np.log(self.p.delta)
                - (self.p.theta / self.p.psi) * delta_c
                + (self.p.theta - 1) * r_c)

    def imrs_vectorized(self, delta_c: np.ndarray, r_c: np.ndarray) -> np.ndarray:
        return (self.p.theta * np.log(self.p.delta)
                - (self.p.theta / self.p.psi) * delta_c
                + (self.p.theta - 1) * r_c)
