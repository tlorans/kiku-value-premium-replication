---
title: Other portfolios
nav_order: 9
---

# Other portfolios

The same investor and the same consumption process can price another sort — industries, quality, profitability, countries — without seeing that sort’s average returns. Only the dividend loadings change.

[Section 6]({% link further.md %}) states the case for the Fama and French (2015) profitability and investment sorts, including why RMW is not a relabeling of value.

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

A higher estimated $$\phi$$ implies a higher long-run risk premium and a lower price–dividend ratio, the ranking value has in this paper.

- [`examples/calibrate_any_portfolio.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_any_portfolio.py)
- [`examples/calibrate_from_real_data.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_from_real_data.py)
