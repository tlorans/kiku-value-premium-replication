"""
Time-series and cross-sectional properties of prices and returns
===============================================================

Replica of Dana Kiku (2006), “Is the Value Premium a Puzzle?”

Once cash-flow dynamics are calibrated to consumption and dividends, the
model is asked to account for both time-series and cross-sectional
properties of assets’ prices and returns. The time-series object is the
market claim. The first cross-sectional object is value versus growth.
Sections 6–7 ask the same question of other premia.

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
