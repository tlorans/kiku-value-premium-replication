"""Campbell and Cochrane (1999) external-habit economy."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CampbellCochraneParams:
    """Annual parameters of the postwar calibration.

    The solver runs at monthly frequency. ``g``, ``sigma``, ``phi``, and
    ``rf`` are the annual numbers from the paper; they are converted
    internally. ``b = 0`` is their choice that makes the bill locally
    constant.
    """

    gamma: float = 2.0
    g: float = 0.0189
    sigma: float = 0.015
    phi: float = 0.87
    rf: float = 0.0094
    b: float = 0.0
