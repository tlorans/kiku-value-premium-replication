---
title: Other portfolios
parent: Package
nav_order: 3
---

# Other portfolios

The time-series object is the market. The cross-sectional object is any pair of claims that differ only in cash-flow loadings. Value is the first pair. The same investor can be asked to account for the cross-sectional properties of another sort without seeing that sort’s average returns.

[Cross section]({% link cross-section.md %}) is the map. [Section 6]({% link further.md %}) writes profitability, investment, and size. [Section 7]({% link climate.md %}) writes transition and physical sorts.

`calibrate_from_data(dc, long=..., short=..., market=...)` names the legs. `value` / `growth` remain aliases. `solve_analytical` and `compute_asset_pricing_moments` resolve either pair. The market key is the time-series check. The long and short keys are the cross-section.

```python
import lrrcs as lrr

dividends = lrr.calibrate_from_data(
    dc, long=dd_value, short=dd_growth, market=dd_market,
    frequency="annual", window=2,
)
params = lrr.get_table_ii_params()
params.dividends = dividends
solver = lrr.ModelSolver(params)
solver.solve()
print(lrr.compute_asset_pricing_moments(solver))
```

- [`examples/calibrate_any_portfolio.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_any_portfolio.py)
- [`examples/calibrate_from_real_data.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_from_real_data.py)
