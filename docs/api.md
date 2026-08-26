---
title: API
nav_order: 7
---

# API

Public names follow her sections 2–5. Version 0.3.0. The 0.2.0 modules `params`, `solver`, `moments`, `simulation`, and `analytical` are gone; there is no shim.

| Section | Import | Objects |
|:---|:---|:---|
| 2 | `kiku_value_premium.empirical` | `connect_wrds`, `build_annual_panel`, `table_i`, `table_vi_data`, `figure1`–`figure4`, `START`, `END` |
| 3 | `kiku_value_premium.model` | `ModelParams`, `PreferencesParams`, `ConsumptionParams`, `DividendParams`, `get_table_ii_params`, `EpsteinZinPreferences`, `Dynamics`, `StateGrid`, `ModelSolver`, `solve_analytical` |
| 4 | `kiku_value_premium.calibration` | `estimate_long_run_leverage`, `calibrate_from_data`, `get_table_ii_dividends`, `simulate_cashflow_moments` |
| 5 | `kiku_value_premium.implications` | `compute_asset_pricing_moments`, `print_asset_pricing_moments`, `figure_lr_premium`, `figure_mean_pd`, `figure5` |

`START, END = 1930, 2003`.

`calibrate_from_data(dc, dd_by_name, frequency="annual", window=2)` takes consumption growth and a dict of dividend-growth series. It has no argument for returns or premia.

Extras: `[fast]` (numba), `[data]` (wrds, python-dotenv, matplotlib), `[dev]` (pytest, matplotlib, numba).

`connect_wrds()` raises `EmpiricalDataError` if `[data]` is missing or `.env` keys are empty. `model`, `calibration`, and `implications` do not import `wrds`.

Recipes: [Empirical]({% link empirical.md %}), [Model]({% link model.md %}), [Calibration]({% link calibration.md %}), [Implications]({% link implications.md %}).
