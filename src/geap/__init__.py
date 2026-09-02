"""General-equilibrium asset pricing models.

Documented import::

    import geap

    model = geap.LongRunRisksModel()
    res = model.solve()
    print(res.summary())
    res.compare("value", "growth").premium

Long-run risks (``geap.lrr``), power utility (``geap.ccapm``), and
habit (``geap.habit``) share :class:`~geap.base.AssetPricingModel`.
"""

from __future__ import annotations

__version__ = "1.2.0"

from .base import (
    AssetPricingModel,
    AssetPricingResults,
    Comparison,
    Summary,
)
from .ccapm import PowerUtilityModel
from .habit import CampbellCochraneModel
from .lrr import (
    AnalyticalResults,
    ClaimParams,
    ConsumptionParams,
    GridResults,
    LongRunRisksModel,
    ModelParams,
    PreferencesParams,
    SimulationResults,
    SolverDivergenceError,
)
from .lrr.calibration import (
    calibrate_claim,
    calibrate_claims,
    estimate_long_run_leverage,
    expected_growth_proxy,
    filter_expected_growth,
)
from .lrr.empirical import (
    EmpiricalDataError,
    build_annual_panel,
    campbell_shiller_annual,
    load_consumption,
    load_deflator,
    real_rf_from_monthly,
    table_i,
    table_vi_data,
)
from . import ccapm, habit, lrr
from ._backend import use_backend as _use_backend

# Frames cross the public boundary in whichever backend tidyfinance is set to.
for _name in ("build_annual_panel", "table_i", "table_vi_data"):
    globals()[_name] = _use_backend(globals()[_name])
del _name, _use_backend

__all__ = [
    "AssetPricingModel",
    "AssetPricingResults",
    "LongRunRisksModel",
    "PowerUtilityModel",
    "CampbellCochraneModel",
    "ModelParams",
    "PreferencesParams",
    "ConsumptionParams",
    "ClaimParams",
    "GridResults",
    "AnalyticalResults",
    "SimulationResults",
    "Comparison",
    "Summary",
    "SolverDivergenceError",
    "EmpiricalDataError",
    "calibrate_claim",
    "calibrate_claims",
    "estimate_long_run_leverage",
    "expected_growth_proxy",
    "filter_expected_growth",
    "build_annual_panel",
    "table_i",
    "table_vi_data",
    "load_consumption",
    "load_deflator",
    "real_rf_from_monthly",
    "campbell_shiller_annual",
    "lrr",
    "ccapm",
    "habit",
]
