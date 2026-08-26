"""
Kiku (2006) Value Premium Puzzle – Replication Package
=====================================================

This package is a transparent replica of Dana Kiku’s Job Market Paper
“Is the Value Premium a Puzzle?”. The public API follows her paper order.

2. Empirical Evidence
   → `empirical.START`, `empirical.END`

3. Model
   → `model.ModelParams`, `model.PreferencesParams`, `model.ConsumptionParams`,
     `model.DividendParams`, `model.get_table_ii_params`,
     `model.EpsteinZinPreferences`, `model.Dynamics`, `model.StateGrid`,
     `model.ModelSolver`, `model.solve_analytical`, `model.resolve_legs`

4. Calibration
   → `calibration.estimate_long_run_leverage`, `calibration.calibrate_from_data`,
     `calibration.get_table_ii_dividends`, `calibration.simulate_cashflow_moments`

5. Asset Pricing Implications
   → `implications.compute_asset_pricing_moments`,
     `implications.print_asset_pricing_moments`,
     `implications.figure_lr_premium`, `implications.figure_mean_pd`,
     `implications.figure5`

Full documentation: https://tlorans.github.io/kiku-value-premium-replication/
"""

__version__ = "0.3.0"

from .empirical import START, END
from .model import (
    ModelParams,
    PreferencesParams,
    ConsumptionParams,
    DividendParams,
    get_table_ii_params,
    EpsteinZinPreferences,
    Dynamics,
    StateGrid,
    ModelSolver,
    solve_analytical,
    resolve_legs,
)
from .calibration import (
    estimate_long_run_leverage,
    calibrate_from_data,
    get_table_ii_dividends,
    simulate_cashflow_moments,
)
from .implications import (
    compute_asset_pricing_moments,
    print_asset_pricing_moments,
    figure_lr_premium,
    figure_mean_pd,
    figure5,
)

__all__ = [
    "START",
    "END",
    "ModelParams",
    "PreferencesParams",
    "ConsumptionParams",
    "DividendParams",
    "get_table_ii_params",
    "EpsteinZinPreferences",
    "Dynamics",
    "StateGrid",
    "ModelSolver",
    "solve_analytical",
    "resolve_legs",
    "estimate_long_run_leverage",
    "calibrate_from_data",
    "get_table_ii_dividends",
    "simulate_cashflow_moments",
    "compute_asset_pricing_moments",
    "print_asset_pricing_moments",
    "figure_lr_premium",
    "figure_mean_pd",
    "figure5",
]
