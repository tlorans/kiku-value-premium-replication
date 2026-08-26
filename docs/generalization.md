---
layout: default
title: Generalizing the Recipe
---

# Generalizing beyond value / growth

The same cash-flow-only recipe prices any cross-section once you supply consumption growth and the portfolios’ dividend-growth series. Typical use: industry portfolios, quality, profitability, investment, or country sorts.

`calibrate_from_data` estimates \(\mu\), \(\tilde\phi\) from equation (19), \(\alpha\) from residual/consumption-innovation correlation, and \(\varphi_\sigma\) as the ratio of equation-(19) residual volatility to consumption-innovation volatility (same frequency as the series; falls back to 7.5 if that scale is degenerate). It never sees return premia. Keep Table II aggregate consumption and Epstein–Zin preferences; only the `DividendParams` change.

`solve_analytical`, `print_value_premium`, and `compute_asset_pricing_moments` look up the paper keys `growth` / `value` / `market`. Map any other cross-section onto those names before pricing.

## What you call

```python
from kiku_value_premium.calibration import calibrate_from_data
from kiku_value_premium.model import ModelParams, get_table_ii_params, ModelSolver
from kiku_value_premium.implications import compute_asset_pricing_moments

dividends = calibrate_from_data(
    dc,
    {"growth": dd_growth, "value": dd_value, "market": dd_market},
    frequency="annual",
    window=2,
)

params = get_table_ii_params()
params.dividends = dividends

solver = ModelSolver(params)
solver.solve()
moments = compute_asset_pricing_moments(solver)
```

The ranking of estimated \(\phi\) becomes the ranking of long-run risk premia. Portfolios with higher long-run leverage command higher expected returns and lower price–dividend ratios — exactly as value stocks do in the original paper.

Ready-to-run starting points:

- [`examples/calibrate_any_portfolio.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_any_portfolio.py) — synthetic series, full workflow
- [`examples/calibrate_from_real_data.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_from_real_data.py) — template for your own \(\Delta d\) arrays
