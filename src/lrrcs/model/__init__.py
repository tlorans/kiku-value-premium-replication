"""Model internals: parameters, dynamics, and the two solution engines.

The documented way in is :class:`lrrcs.LongRunRisksModel`; the names here
are the machinery behind it.
"""
from .legs import ROLE_ALIASES, Legs, resolve_legs
from .params import (
    ConsumptionParams,
    DividendParams,
    ModelParams,
    PreferencesParams,
    get_default_params,
    get_table_ii_params,
)
from .preferences import EpsteinZinPreferences
from .dynamics import Dynamics
from .discretization import StateGrid
from .solver import ModelSolver, SolverDivergenceError
from .analytical import (
    DEFAULT_PD_ANCHOR,
    PAPER_PD_ANCHORS,
    AnalyticalSolution,
    solve_analytical,
)

__all__ = [
    "ROLE_ALIASES",
    "Legs",
    "resolve_legs",
    "ModelParams",
    "PreferencesParams",
    "ConsumptionParams",
    "DividendParams",
    "get_table_ii_params",
    "get_default_params",
    "EpsteinZinPreferences",
    "Dynamics",
    "StateGrid",
    "ModelSolver",
    "SolverDivergenceError",
    "AnalyticalSolution",
    "solve_analytical",
    "PAPER_PD_ANCHORS",
    "DEFAULT_PD_ANCHOR",
]
