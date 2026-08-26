---
title: Other portfolios
nav_order: 9
---

# Other portfolios

The time-series object is the market. The cross-sectional object is any pair of claims that differ only in cash-flow loadings. Value is the first pair. The same investor and the same consumption process can be asked to account for the cross-sectional properties of another sort — profitability, investment, size, industries, climate — without seeing that sort’s average returns.

[Section 6]({% link further.md %}) writes the map for the Fama and French (2015) sorts. [Section 7]({% link climate.md %}) writes the map for Melin and Zhang (2026): two extra loadings, $$\Omega^i$$ on the damage signal and $$\Gamma^i$$ on policy tightening. $$\phi$$ raises the long-run premium and lowers $$\log(P/D)$$. $$\mu$$ raises $$\log(P/D)$$ and barely moves the premium. A climate sort that differs only in $$\phi$$ is value under another name.

Keep Table II aggregate consumption and Epstein–Zin preferences for Sections 2–6. For Section 7 keep the Melin–Zhang climate module as well. `calibrate_from_data` estimates $$\mu$$ from mean $$\Delta d$$, $$\tilde\phi$$ from equation (19), $$\alpha$$ from residual/consumption-innovation correlation, and $$\varphi_\sigma$$ as residual vol over consumption-innovation vol (fallback 7.5). It never sees return premia and it does not yet see $$Y_t$$ or $$P_t$$.

`calibrate_from_data(dc, long=..., short=..., market=...)` names the legs. `value` / `growth` remain aliases. `solve_analytical` and `compute_asset_pricing_moments` resolve either pair. The market key is the time-series check. The long and short keys are the cross-section.

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
