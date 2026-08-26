---
layout: default
title: API / Modules Reference
---

# API / Modules Reference

Each module implements one (or more) steps of Kiku’s recipe.

| Module | Recipe step(s) | Key public objects |
|--------|----------------|--------------------|
| `params` | 1, 2, 4 | `ModelParams`, `ConsumptionParams`, `DividendParams`, `PreferencesParams`, `get_default_params()` |
| `dynamics` | 1, 2 | `Dynamics` – `simulate_states()`, `simulate_cashflows()` |
| `calibration` | 3 | `calibrate_from_data()`, `estimate_long_run_leverage()`, `get_table_ii_dividends()` |
| `preferences` | 4 | `EpsteinZinPreferences` – `imrs()`, `theta` |
| `discretization` | 5 | `StateGrid` – product grid + transition matrix |
| `solver` | 5 | `ModelSolver` – `solve()`, `mean_pd()`, `summary()` |
| `analytical` | 6a | `solve_analytical()`, `print_value_premium()`, `AnalyticalSolution` |
| `simulation` | 3 | `simulate_moments()`, `print_moments()` |
| `moments` | 6b | `compute_asset_pricing_moments()`, `print_asset_pricing_moments()` |

## Core objects

### ModelParams (params.py)
Holds the entire calibration:
- `prefs` – Epstein–Zin parameters (δ = 0.999, γ = 10, ψ = 1.5)
- `cons` – consumption process (ρ = 0.98, …)
- `dividends` – dict of `DividendParams` (the key heterogeneity lives in `phi`)

### DividendParams
- `mu` – mean dividend growth
- `phi` – **long-run leverage** (the decisive parameter: value = 6.2, growth = 2.6)
- `phi_sigma` – loading on volatility risk
- `alpha` – correlation with consumption innovation

### ModelSolver (solver.py)
```python
solver = ModelSolver(params=params, n_x=30, n_s=4, n_quad=7)
solver.solve()
# Access: solver.z_c, solver.z["value"], solver.z["growth"], solver.stationary
```

### calibrate_from_data (calibration.py)
The entry point for applying the recipe to new portfolios:
```python
from kiku_value_premium.calibration import calibrate_from_data
dividends = calibrate_from_data(dc, {"industry_A": dd_a, "industry_B": dd_b}, frequency="annual")
```

See the **[Recipe](KIKU_RECIPE.html)** for the economic meaning of every parameter and the **[Examples](examples.html)** page for usage patterns.
