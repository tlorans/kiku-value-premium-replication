---
title: API
nav_order: 7
---

# API

The four import paths are Sections 2–5 of the paper. A function that prices assets does not live next to the WRDS pull.

Version 0.3.0 dropped the flat 0.2.0 names (`params`, `solver`, `moments`, `simulation`, `analytical`) so the code layout cannot drift from the argument.

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

[Section 2]({% link empirical.md %}) · [Section 3]({% link model.md %}) · [Section 4]({% link calibration.md %}) · [Section 5]({% link implications.md %})
