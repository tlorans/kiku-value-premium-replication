"""Mehra and Prescott (1985) two-state power-utility economy."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PowerUtilityParams:
    """Annual two-state chain plus power utility.

    Defaults are the paper's consumption moments (μ = 0.018, σ = 0.036,
    ρ = −0.14) and the edge of their plausible preference set
    (δ = 0.99, γ = 10).
    """

    delta: float = 0.99
    gamma: float = 10.0
    mu: float = 0.018
    sigma: float = 0.036
    rho: float = -0.14
