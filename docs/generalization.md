---
title: Other portfolios
nav_order: 9
---

# Other portfolios

The same investor and the same consumption process can price another sort — industries, quality, profitability, countries — without seeing that sort’s average returns. Only the four dividend loadings $$(\mu,\phi,\varphi,\alpha)$$ change.

[Section 6]({% link further.md %}) writes the map for the Fama and French (2015) sorts. $$\phi$$ raises the long-run premium and lowers $$\log(P/D)$$. $$\mu$$ raises $$\log(P/D)$$ and barely moves the premium. Profitability needs both: a larger $$\phi$$ on the robust leg for the premium, a larger $$\mu$$ on that same leg if the claim is to remain expensive. Investment is the value ranking. Print `.mu` and `.phi` on each leg before reading Section 5 moments.

Keep Table II aggregate consumption and Epstein–Zin preferences. `calibrate_from_data` estimates $$\mu$$ from mean $$\Delta d$$, $$\tilde\phi$$ from equation (19), $$\alpha$$ from residual/consumption-innovation correlation, and $$\varphi_\sigma$$ as residual vol over consumption-innovation vol (fallback 7.5). It never sees return premia.

`calibrate_from_data(dc, long=..., short=..., market=...)` names the legs. `value` / `growth` remain aliases. `solve_analytical` and `compute_asset_pricing_moments` resolve either pair.

```python
from kiku_value_premium.calibration import calibrate_from_data
from kiku_value_premium.model import get_table_ii_params, ModelSolver
from kiku_value_premium.implications import compute_asset_pricing_moments

dividends = calibrate_from_data(
    dc,
    long=dd_value, short=dd_growth, market=dd_market,
    frequency="annual",
    window=2,
)
for name, d in dividends.items():
    print(name, d.mu, d.phi, d.phi_sigma, d.alpha)
params = get_table_ii_params()
params.dividends = dividends
solver = ModelSolver(params)
solver.solve()
moments = compute_asset_pricing_moments(solver)
```

- [`examples/calibrate_any_portfolio.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_any_portfolio.py)
- [`examples/calibrate_from_real_data.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_from_real_data.py)
