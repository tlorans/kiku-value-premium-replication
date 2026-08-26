---
layout: default
title: Examples
---

# Examples

The repository contains ready-to-run scripts in the `examples/` folder.

## 1. Original value-premium mechanism

```bash
python examples/demo.py
```
Reproduces the analytical long-run risk decomposition and the numerical solution for value, growth and the market.

## 2. Calibrate any synthetic portfolios

```bash
python examples/calibrate_any_portfolio.py
```
Shows the full workflow:
1. Generate or supply cash-flow series
2. Call `calibrate_from_data`
3. Build a `ModelParams` object
4. Solve with `ModelSolver`
5. Read off the risk premia and valuations

## 3. Template for real data

```bash
python examples/calibrate_from_real_data.py
```
Skeleton that you can fill with your own consumption and dividend (or earnings) growth series. Ideal starting point for industry or climate portfolios.

## Typical workflow in code

```python
from kiku_value_premium.calibration import calibrate_from_data
from kiku_value_premium.params import get_default_params
from kiku_value_premium.solver import ModelSolver
from kiku_value_premium.moments import compute_asset_pricing_moments

# Your data (same frequency)
dividends = calibrate_from_data(dc, {"portA": dd_a, "portB": dd_b}, frequency="annual")

params = get_default_params()
params.dividends = dividends

solver = ModelSolver(params)
solver.solve()
moments = compute_asset_pricing_moments(solver)
```

For the economic rationale behind each call, see the **[Recipe](KIKU_RECIPE.html)** and **[Generalization](generalization.html)** pages.
