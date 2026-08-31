"""General-equilibrium long-run risks: asset prices and risk premia.

Companion to tidyfinance. Documented import::

    import tidyfinance as tf
    import lrrcs as lrr

Solve the Kiku (2006) model and read its numbers::

    model = lrr.LongRunRisksModel()
    res = model.solve()
    print(res.summary())
    res.value_premium

    sim = model.simulate(n_samples=1000, years=74, seed=0)
    print(sim.summary())

The subpackages ``lrrcs.model``, ``lrrcs.implications``,
``lrrcs.calibration``, and ``lrrcs.empirical`` hold the machinery; the
names below are the documented surface.
"""

from __future__ import annotations

__version__ = "0.6.0"

from . import calibration, empirical
from .api import LongRunRisksModel
from .calibration import (
    estimate_long_run_leverage,
    expected_growth_proxy,
    filter_expected_growth,
)
from .empirical import (
    EmpiricalDataError,
    build_annual_panel,
    campbell_shiller_annual,
    load_consumption,
    load_deflator,
    real_rf_from_monthly,
    table_i,
    table_vi_data,
)
from .model.legs import Legs
from .model.params import (
    ConsumptionParams,
    DividendParams,
    ModelParams,
    PreferencesParams,
)
from .model.solver import SolverDivergenceError
from .results import AnalyticalResults, GridResults, SimulationResults, Summary

from ._backend import use_backend as _use_backend

# Frames cross the public boundary in whichever backend tidyfinance is set to.
for _name in ("build_annual_panel", "table_i", "table_vi_data"):
    globals()[_name] = _use_backend(globals()[_name])
del _name, _use_backend

__all__ = [
    # the model
    "LongRunRisksModel",
    # parameters
    "ModelParams",
    "PreferencesParams",
    "ConsumptionParams",
    "DividendParams",
    "Legs",
    # results
    "GridResults",
    "AnalyticalResults",
    "SimulationResults",
    "Summary",
    # errors
    "SolverDivergenceError",
    "EmpiricalDataError",
    # measuring loadings from cash flows
    "estimate_long_run_leverage",
    "expected_growth_proxy",
    "filter_expected_growth",
    # data construction
    "build_annual_panel",
    "table_i",
    "table_vi_data",
    "load_consumption",
    "load_deflator",
    "real_rf_from_monthly",
    "campbell_shiller_annual",
    # subpackages
    "calibration",
    "empirical",
]
