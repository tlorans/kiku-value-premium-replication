"""
Model parameters from Table II of Kiku (2006).
All rates monthly unless noted.
"""

from dataclasses import dataclass, field
from typing import Dict
import numpy as np


@dataclass
class PreferencesParams:
    delta: float = 0.999  # time discount factor
    gamma: float = 10.0  # risk aversion
    psi: float = 1.5     # IES

    @property
    def theta(self) -> float:
        """theta = (1 - gamma) / (1 - 1/psi)"""
        return (1 - self.gamma) / (1 - 1 / self.psi)


@dataclass
class ConsumptionParams:
    mu: float = 0.0015   # mean growth
    rho: float = 0.98    # persistence of x
    phi_x: float = 0.032 # vol of expected growth shock
    sigma: float = 0.0064  # mean vol of consumption
    nu: float = 0.99     # persistence of variance
    sigma_w: float = 0.0000017  # vol of variance shock


@dataclass
class DividendParams:
    mu: float
    phi: float  # loading on expected growth x (long-run risk exposure)
    phi_sigma: float  # loading on vol (phi in paper for short-run + vol)
    alpha: float  # corr with consumption innovation eta


@dataclass
class ModelParams:
    prefs: PreferencesParams = field(default_factory=PreferencesParams)
    cons: ConsumptionParams = field(default_factory=ConsumptionParams)
    dividends: Dict[str, DividendParams] = field(default_factory=dict)
    # residual correlations of orthogonalized dividend shocks (growth, value, market)
    residual_corr_gv: float = 0.20
    residual_corr_gm: float = 0.80
    residual_corr_vm: float = 0.45

    def __post_init__(self):
        if not self.dividends:
            self.dividends = {
                "growth": DividendParams(mu=0.0009, phi=2.6, phi_sigma=8.4, alpha=0.27),
                "value": DividendParams(mu=0.0019, phi=6.2, phi_sigma=7.4, alpha=0.15),
                "market": DividendParams(mu=0.0012, phi=2.8, phi_sigma=7.5, alpha=0.55),
            }


def get_default_params() -> ModelParams:
    return ModelParams()
