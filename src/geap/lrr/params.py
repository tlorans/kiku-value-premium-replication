"""
Step 1 & 2 of Kiku’s recipe – Model parameters
==============================================

Step 1  Aggregate long-run risks consumption process
        → ConsumptionParams (Table II of the paper)

Step 2  Heterogeneous cash-flow processes
        → ClaimParams for each portfolio

The single most important cross-sectional parameter is

    ClaimParams.phi   = long-run leverage
                        = loading of the claim's cash-flow growth on the
                          persistent expected-growth component x_t of
                          consumption.

In the paper: value has phi = 6.2, growth has phi = 2.6.
This differential long-run exposure is what generates the value premium
under Epstein–Zin preferences.
"""

from dataclasses import dataclass, field
from typing import Dict
import numpy as np


@dataclass
class PreferencesParams:
    """Step 4 – Epstein–Zin preference parameters (Table II)."""
    delta: float = 0.999  # time discount factor
    gamma: float = 10.0   # risk aversion
    psi: float = 1.5      # elasticity of intertemporal substitution

    @property
    def theta(self) -> float:
        """theta = (1 - gamma) / (1 - 1/psi)"""
        return (1 - self.gamma) / (1 - 1 / self.psi)


@dataclass
class ConsumptionParams:
    """Step 1 – Aggregate long-run risks consumption process (Table II)."""
    mu: float = 0.0015       # mean growth
    rho: float = 0.98        # persistence of expected growth x_t
    phi_x: float = 0.032     # volatility of expected-growth shocks
    sigma: float = 0.0064    # mean volatility of consumption
    nu: float = 0.99         # persistence of variance
    sigma_w: float = 0.0000017  # volatility of variance shocks


@dataclass
class ClaimParams:
    """
    Step 2 – The cash-flow process of one claim.

    A claim is anything with a cash-flow stream to price: a portfolio, a
    single firm, or a synthetic claim you invent. Only ``phi`` varies the
    economics across a cross-section.

    Parameters
    ----------
    mu : float
        Mean cash-flow growth (monthly).
    phi : float
        **Long-run leverage** – loading on the persistent expected-growth
        component x_t of consumption.  This is the key cross-sectional
        parameter in Kiku’s paper (value = 6.2, growth = 2.6).
    phi_sigma : float
        Loading on short-run / volatility risk.
    alpha : float
        Correlation of the claim’s residual shock with the consumption
        innovation.

    Examples
    --------
    ```python
    import geap
    claim = geap.ClaimParams(mu=0.0019, phi=6.2, phi_sigma=7.4, alpha=0.15)
    geap.LongRunRisksModel(claims={"mine": claim}).solve(method="analytical")
    ```
    """
    mu: float
    phi: float          # long-run leverage (the decisive parameter)
    phi_sigma: float
    alpha: float

    @property
    def long_run_leverage(self) -> float:
        """Alias for `phi` – makes the economic meaning explicit."""
        return self.phi

    @classmethod
    def from_loading(cls, phi: float, *, mu: float = 0.0015,
                     phi_sigma: float = 7.5, alpha: float = 0.5) -> "ClaimParams":
        """A synthetic claim defined by its loading on x_t.

        The loading is measured from cash flows, never from returns; see
        :func:`geap.estimate_long_run_leverage`. The other three
        parameters default to neutral middle-of-the-road values so that
        two claims built this way differ only in ``phi``.

        Examples
        --------
        ```python
        import geap
        model = geap.LongRunRisksModel(claims={
            "high": geap.ClaimParams.from_loading(1.5),
            "low": geap.ClaimParams.from_loading(0.5),
        })
        ```
        """
        return cls(mu=mu, phi=phi, phi_sigma=phi_sigma, alpha=alpha)


@dataclass
class ModelParams:
    """
    Complete model parameterisation used throughout the package.

    Contains:
    - prefs  : Epstein–Zin preferences (Step 4)
    - cons   : aggregate consumption process (Step 1)
    - claims : dict of ClaimParams, one per claim to price (Step 2)
    """
    prefs: PreferencesParams = field(default_factory=PreferencesParams)
    cons: ConsumptionParams = field(default_factory=ConsumptionParams)
    claims: Dict[str, ClaimParams] = field(default_factory=dict)
    # residual correlations of orthogonalised dividend shocks
    residual_corr_gv: float = 0.20
    residual_corr_gm: float = 0.80
    residual_corr_vm: float = 0.45
    # Residual correlations for claims outside the paper's three portfolios,
    # keyed by the pair of claim names: {("high", "low"): 0.2}. Pairs listed
    # here win over the residual_corr_* attributes above.
    residual_corr: Dict[frozenset, float] | None = None

    def __post_init__(self):
        if not self.claims:
            # Exact Table II values (bottom panel)
            self.claims = {
                "growth": ClaimParams(mu=0.0009, phi=2.6, phi_sigma=8.4, alpha=0.27),
                "value":  ClaimParams(mu=0.0019, phi=6.2, phi_sigma=7.4, alpha=0.15),
                "market": ClaimParams(mu=0.0012, phi=2.8, phi_sigma=7.5, alpha=0.55),
            }
        if self.residual_corr:
            self.residual_corr = {
                frozenset(pair): float(rho)
                for pair, rho in self.residual_corr.items()
            }


def get_table_ii_params() -> ModelParams:
    """Exact Table II calibration."""
    return ModelParams()


def get_default_params() -> ModelParams:
    return get_table_ii_params()
