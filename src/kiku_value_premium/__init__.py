"""
Kiku (2006) Value Premium Puzzle – Replication Package
=====================================================

This package implements the **exact 6-step methodology** of Dana Kiku’s
Job Market Paper “Is the Value Premium a Puzzle?”.

The recipe (and the corresponding public API) is:

1. Aggregate long-run risks consumption process
   → `params.ConsumptionParams`, `dynamics.Dynamics`

2. Heterogeneous cash-flow processes (different long-run loadings)
   → `params.DividendParams`  (the key field is `phi` = long-run leverage)

3. Calibrate cash-flow dynamics *only* to time-series moments
   → `calibration.calibrate_from_data`, `calibration.get_table_ii_dividends`

4. Epstein–Zin preferences
   → `preferences.EpsteinZinPreferences`, `params.PreferencesParams`

5. Numerical solution (Tauchen–Hussey style)
   → `solver.ModelSolver`, `discretization.StateGrid`

6. Evaluate both time-series and cross-section
   → `moments.compute_asset_pricing_moments`, `analytical.solve_analytical`

Full documentation: https://tlorans.github.io/kiku-value-premium-replication/
"""

__version__ = "0.3.0"

# ------------------------------------------------------------------
# Public API organised around Kiku’s 6-step recipe
# ------------------------------------------------------------------

from .model import (
    ModelParams,
    PreferencesParams,
    ConsumptionParams,
    DividendParams,
    get_default_params,
    Dynamics,
    EpsteinZinPreferences,
    StateGrid,
    ModelSolver,
    solve_analytical,
    print_value_premium,
)
from .calibration import (
    calibrate_from_data,
    estimate_long_run_leverage,
    get_table_ii_dividends,
)
from .moments import compute_asset_pricing_moments, print_asset_pricing_moments
from .simulation import simulate_moments, print_moments

__all__ = [
    # Step 1–2
    "ModelParams",
    "PreferencesParams",
    "ConsumptionParams",
    "DividendParams",
    "get_default_params",
    "Dynamics",
    # Step 3
    "calibrate_from_data",
    "estimate_long_run_leverage",
    "get_table_ii_dividends",
    # Step 4
    "EpsteinZinPreferences",
    # Step 5
    "StateGrid",
    "ModelSolver",
    # Step 6
    "solve_analytical",
    "print_value_premium",
    "compute_asset_pricing_moments",
    "print_asset_pricing_moments",
    "simulate_moments",
    "print_moments",
]
