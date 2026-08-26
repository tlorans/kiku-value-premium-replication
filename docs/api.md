---
layout: default
title: API / Modules Reference
---

# API / Modules Reference

The public API follows Kiku’s paper order. Headline names:

| Section | Import from | Objects |
|---------|-------------|---------|
| 2 | `kiku_value_premium.empirical` | `connect_wrds`, `build_annual_panel`, `table_i`, `table_vi_data`, `figure1`, `figure2`, `figure3`, `figure4`, `START`, `END` |
| 3 | `kiku_value_premium.model` | `ModelParams`, `PreferencesParams`, `ConsumptionParams`, `DividendParams`, `get_table_ii_params`, `EpsteinZinPreferences`, `Dynamics`, `StateGrid`, `ModelSolver`, `solve_analytical` |
| 4 | `kiku_value_premium.calibration` | `estimate_long_run_leverage`, `calibrate_from_data`, `get_table_ii_dividends`, `simulate_cashflow_moments` |
| 5 | `kiku_value_premium.implications` | `compute_asset_pricing_moments`, `print_asset_pricing_moments`, `figure_lr_premium`, `figure_mean_pd`, `figure5` |

`START, END = 1930, 2003` live in `empirical` and are the only sample window.

`calibrate_from_data(dc, dd_by_name, frequency="annual", window=2)` takes consumption growth and a dict of dividend-growth series. It has no argument for returns or premia.

Core dependencies: numpy, scipy, pandas. Optional:

- `[fast]`: `numba>=0.56`
- `[data]`: `wrds`, `python-dotenv`, `matplotlib`
- `[dev]`: pytest, matplotlib, numba

Importing `empirical` without `[data]` raises `EmpiricalDataError` that names the extra and the two `.env` keys. `model`, `calibration`, and `implications` must not import `wrds`.

The 0.2.0 flat modules (`kiku_value_premium.params`, `.solver`, `.moments`, `.simulation`, `.analytical`) are gone. There is no compatibility shim.

See the section recipes for call patterns: [Empirical](empirical.html), [Model](model.html), [Calibration](calibration.html), [Implications](implications.html).
