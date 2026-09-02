"""Hansen GMM for asset-pricing moment conditions.

GMM chooses parameters so the averages the model promises match the
averages in the data. This is a different estimator from the cash-flow
calibration in :mod:`geap.lrr.calibration`: returns never enter that
path, and they do not enter it through this module either.
"""
from .estimate import estimate
from .moments import linear_factor, power_utility_sdf, sdf_moments
from .results import GMMResults

__all__ = [
    "estimate",
    "linear_factor",
    "power_utility_sdf",
    "sdf_moments",
    "GMMResults",
]
