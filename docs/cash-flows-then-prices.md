---
title: Cash flows, then prices
nav_order: 4
---

# Cash flows, then prices
{: .no_toc }

1. TOC
{:toc}

Every claim in this book is judged the same way. Form the claim from data. Calibrate how its dividends move with consumption. Solve for prices. Then ask whether those prices look like the data. Average returns never enter the second step. If they did, the fourth step would not be a test.

The household is Epstein and Zin (1989) / Weil (1989). Risk aversion $$\gamma$$ and the elasticity of intertemporal substitution $$\psi$$ are different numbers. The intertemporal marginal rate of substitution is

$$
M_{t+1}=\delta^\theta (C_{t+1}/C_t)^{-\theta/\psi} R_{c,t+1}^{\theta-1},
\qquad
\theta=\frac{1-\gamma}{1-1/\psi}.
$$

The Euler equation is the whole pricing theory: $$\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1$$. Table II uses $$\delta=0.999$$, $$\gamma=10$$, $$\psi=1.5$$, so $$\theta\neq 1$$ and news about wealth is priced. Under power utility ($$\gamma=1/\psi$$) that news is not priced, and a gap in dividend loadings on slow consumption cannot produce a large premium.

## The four steps

**Data.** Form the claim or claims. Consumption growth and dividend growth are the cash-flow series. How to retrieve those series is [Financial data]({{ '/financial-data.html' | relative_url }}). tidyfinance supplies CRSP, Compustat, CCM, and NYSE breakpoints. `lrrcs` still builds Campbell–Shiller dividends and historical book equity.

**Calibrate cash flows.** Match mean and persistence of consumption growth, persistence of $$x_t$$, dividend volatilities, and each claim’s loading on slow consumption. Do not match mean returns, Sharpe ratios, or CAPM betas. Table II is the default. `calibrate_from_data` is the first-pass helper for a new sort. If simulated consumption does not look like the sample, stop.

**Solve.** Give those locked cash-flow numbers to `solve_analytical` or `ModelSolver`. The Euler equation returns prices and expected returns.

**Compare pricing moments.** Equity premium, risk-free rate, return volatility, mean $$\log(P/D)$$, and — when there are two legs — the long–short premium and the price–dividend ranking. Success is the model column close to the data column without having seen those numbers in calibration.

## Skeleton

Both later chapters copy this shape.

```python
import pandas as pd
import tidyfinance as tf
import lrrcs as lrr

tf.set_wrds_credentials()
bm = lrr.build_annual_panel(refresh=False)
dc = pd.read_csv("data/consumption_annual.csv").set_index("year")["dc"]

# Table II locks the household. For a new sort, set params.dividends to
# lrr.calibrate_from_data(dc, long=..., short=..., market=...).
params = lrr.get_table_ii_params()
print(lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=params))

lrr.print_long_short_premium(lrr.solve_analytical(params))
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
print(lrr.compute_asset_pricing_moments(solver))
```

Next: run the four steps on [the market]({{ '/time-series.html' | relative_url }}), then on [value versus growth]({{ '/cross-section.html' | relative_url }}).
