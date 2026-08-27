---
title: The market
nav_order: 5
---

# The market
{: .no_toc }

1. TOC
{:toc}

**Question.** Can this household price the *market* — the value-weighted claim on all listed stocks — year after year?

That is the test Bansal and Yaron (2004) wrote the model for. One claim. Not a ranking of firms. The four steps are those of [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}).

## Data

Consumption is real per-capita nondurables plus services. Market dividends are Campbell–Shiller dividends on the CRSP value-weighted portfolio of ordinary shares, deflated, 1930–2003. The objects are how consumption and *market* dividends grow. Not the average stock return.

tidyfinance supplies CRSP, Compustat, CCM, and NYSE breakpoints. `lrrcs` still builds Campbell–Shiller dividends.

```python
import pandas as pd
import tidyfinance as tf
import lrrcs as lrr

tf.set_wrds_credentials()
bm = lrr.build_annual_panel(refresh=False)
print(lrr.table_i(bm))
dc = pd.read_csv("data/consumption_annual.csv").set_index("year")["dc"]
print(lrr.table_vi_data(bm, dc))
```

Defaults are 1930–2003. `refresh=True` rebuilds the extracts. Core install without WRDS still solves Table II in the next two steps.

## Calibrate cash flows

Consumption growth is not white noise. It has a small persistent expected-growth piece $$x_t$$ and a variance that itself moves. Market dividends are consumption with extra leverage on those shocks. Monthly loading on $$x_t$$ is $$\phi_m=2.8$$. Persistence is $$\rho=0.98$$.

**What is matched.** Mean and persistence of consumption growth, persistence of $$x_t$$, market dividend volatility, market loading on slow consumption.

**What is not matched.** The average market return, the Sharpe ratio, the CAPM beta of the market.

| Symbol | Value | Meaning |
|:---|---:|:---|
| $$\delta$$ | 0.999 | time discount |
| $$\gamma$$ | 10 | risk aversion |
| $$\psi$$ | 1.5 | EIS |
| $$\mu_c$$ | 0.0015 | mean monthly consumption growth |
| $$\rho$$ | 0.98 | persistence of $$x_t$$ |
| $$\varphi_x$$ | 0.032 | scale of shocks to $$x$$ |
| $$\sigma$$ | 0.0064 | average consumption volatility |

Market dividends: $$\mu=0.0012$$, $$\phi=2.8$$, $$\varphi_\sigma=7.5$$, $$\alpha=0.55$$.

Simulated consumption, 1000 samples of 74 years: mean growth 1.86 percent against 1.96 in the data; volatility 2.16 against 2.20; first autocorrelation 0.43 against 0.44. If those fail, stop. The premium that comes next would then be a free parameter in disguise.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
params.dividends["market"].phi  # 2.8
params.cons.rho                 # 0.98
print(lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=params))
```

## Solve

The IMRS and Euler equation are on [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}). Table II of Kiku (2006) is the default household. `solve_analytical` is the linearization shortcut. `ModelSolver` is the Euler map on a grid.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
lrr.print_long_short_premium(lrr.solve_analytical(params))
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
```

## Compare pricing moments

Given those locked cash-flow numbers, what prices does the Euler equation assign to the market and the safe bond?

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

E[R] is the average simple return, percent per year. E[pd] is average $$\log(P/D)$$. Numbers in parentheses are standard errors across simulated samples. Market return volatility is 20.1 percent in both. The safe rate is about seventy basis points too high. The equity premium is a little short of the sample. Close enough to ask a second question.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
lrr.print_asset_pricing_moments(lrr.compute_asset_pricing_moments(solver))
```

The market column on that printout is this page. Value and growth are [Value versus growth]({{ '/cross-section.html' | relative_url }}). Matching the market does not rank firms.
