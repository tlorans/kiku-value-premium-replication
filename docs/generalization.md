---
title: Other portfolios
nav_order: 8
---

# Other portfolios

The same cash-flow-only recipe prices any cross-section once you supply consumption growth and dividend-growth series — industries, quality, profitability, investment, countries.

Keep Table II aggregate consumption and Epstein–Zin preferences. Only `DividendParams` change. `calibrate_from_data` estimates $$\mu$$, $$\tilde\phi$$ from equation (19), $$\alpha$$ from residual/consumption-innovation correlation, and $$\varphi_\sigma$$ as residual vol over consumption-innovation vol (fallback 7.5). It never sees return premia.

`solve_analytical`, `print_value_premium`, and `compute_asset_pricing_moments` look up the paper keys `growth`, `value`, and `market`. Map any other sort onto those names before pricing.

```python
from kiku_value_premium.calibration import calibrate_from_data
from kiku_value_premium.model import get_table_ii_params, ModelSolver
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

Higher estimated $$\phi$$ means higher long-run risk premia and lower price–dividend ratios — the same ranking value has in her paper.

- [`examples/calibrate_any_portfolio.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_any_portfolio.py)
- [`examples/calibrate_from_real_data.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_from_real_data.py)
