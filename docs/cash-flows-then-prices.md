---
title: Cash flows, then prices
nav_order: 4
---

# Cash flows, then prices
{: .no_toc }

1. TOC
{:toc}

Every claim in this book is judged the same way. Form the claim from data. Calibrate how its dividends move with consumption. Solve for prices. Then ask whether those prices look like the data. Average returns never enter the second step. If they did, the fourth step would not be a test.

[The market]({{ '/time-series.html' | relative_url }}) and [Value versus growth]({{ '/cross-section.html' | relative_url }}) both copy this loop. This page is the map: the household, the four steps, and a skeleton you can run. Run the chunks **in order**.

```python
import numpy as np
import pandas as pd
import polars as pl
import plotnine as p9
import tidyfinance as tf
import lrrcs as lrr
```

## The household

The household is Epstein and Zin (1989) / Weil (1989). Risk aversion $$\gamma$$ and the elasticity of intertemporal substitution $$\psi$$ are different numbers. Power utility forces $$\gamma=1/\psi$$. Write $$\theta$$ and look at it:

```python
delta, gamma, psi = 0.999, 10.0, 1.5
theta = (1.0 - gamma) / (1.0 - 1.0 / psi)
gamma, 1.0 / psi, theta
```

```text
(10.0, 0.667, -27.0)
```

$$\theta\neq 1$$. The intertemporal marginal rate of substitution is

$$
M_{t+1}=\delta^\theta (C_{t+1}/C_t)^{-\theta/\psi} R_{c,t+1}^{\theta-1}.
$$

Because $$\theta\neq 1$$, news about wealth $$R_{c,t+1}$$ is priced. Under power utility $$\theta=1$$ and that term drops out. A gap in dividend loadings on slow consumption $$x_t$$ then cannot produce a large premium. The Euler equation is the whole pricing theory: $$\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1$$.

Table II uses those $$(\delta,\gamma,\psi)$$ together with monthly $$\rho=0.98$$ for $$x_t$$.

## The four steps

**Data.** Form the claim or claims. Consumption growth and dividend growth are the cash-flow series. [Financial data]({{ '/financial-data.html' | relative_url }}) downloads NIPA from FRED, builds Campbell–Shiller dividends from CRSP `ret` / `retx`, and sorts on book-to-market.

```python
dc = pl.read_csv("data/consumption_annual.csv").sort("year")
panel = pl.read_csv("data/annual_panel.csv")
dc.height, panel["claim"].unique().to_list()
```

```text
(74, ['Growth', 'Value', 'Market'])
```

**Calibrate cash flows.** Match mean and persistence of consumption growth, persistence of $$x_t$$, dividend volatilities, and each claim’s loading on slow consumption. Do not match mean returns, Sharpe ratios, or CAPM betas. Equation (19) is OLS of $$\Delta d$$ on a two-year MA of lagged $$\Delta c$$:

```python
y = dc["dc"].to_numpy()
ma = np.full(len(y), np.nan)
for t in range(2, len(y)):
    ma[t] = float(np.mean(y[t - 2 : t]))

def phi_hat(claim):
    dd = (
        panel.filter(pl.col("claim") == claim)
        .join(dc, on="year")
        .sort("year")["dgrowth"]
        .to_numpy()
    )
    mask = np.isfinite(ma) & np.isfinite(dd)
    x = ma[mask] - ma[mask].mean()
    e = dd[mask] - dd[mask].mean()
    return float(np.dot(x, e) / np.dot(x, x))

{c: round(phi_hat(c), 3) for c in ("Growth", "Value", "Market")}
```

```text
{'Growth': -0.267, 'Value': 12.129, 'Market': 0.722}
```

Value’s annual slope is larger than growth’s. That *ranking* is the check. The solver wants monthly $$\phi$$; Table II locks 6.2 / 2.6 / 2.8. `lrr.calibrate_from_data` is the first-pass helper for a new sort. If simulated consumption does not look like the sample, stop.

**Solve.** Give those locked cash-flow numbers to the linearized map or the Euler grid. Elasticity of log $$P/D$$ to $$x_t$$ is

$$
A_1=\frac{\phi-1/\psi}{1-\kappa_1\rho}.
$$

```python
psi, rho = 1.5, 0.98
for name, phi, zbar in (("growth", 2.6, 3.65), ("value", 6.2, 3.10), ("market", 2.8, 3.24)):
    kappa1 = np.exp(zbar) / (1.0 + np.exp(zbar))
    A1 = (phi - 1.0 / psi) / (1.0 - kappa1 * rho)
    print(name, round(kappa1, 3), round(A1, 1))
```

```text
growth 0.975 43.1
value  0.957 88.9
market 0.962 37.5
```

Value’s price moves about twice as much with $$x_t$$ as growth’s. `lrr.solve_analytical` returns those $$A_1$$ and the long-run premia. `ModelSolver` is the Euler map on a grid.

**Compare pricing moments.** Equity premium, risk-free rate, return volatility, mean $$\log(P/D)$$, and — when there are two legs — the long–short premium and the price–dividend ranking. Success is the model column close to the data column without having seen those numbers in calibration. `lrr.compute_asset_pricing_moments` and `lrr.print_long_short_premium` print that comparison.

## Skeleton

Both later chapters copy this shape. Table II locks the household. For a new sort, replace `params.dividends` with `calibrate_from_data`.

```python
params = lrr.get_table_ii_params()
print(lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=params))
lrr.print_long_short_premium(lrr.solve_analytical(params))
```

```text
Approximate annualized long-run risk premia:
  growth  :   0.39%
  value   :   0.80%
  market  :   0.34%
Value-growth spread from long-run risks: 0.40%
A1 (PD elasticity to x): growth=43.1, value=88.9
Price of long-run risk Lambda_eps = 5.95
```

## Key takeaways

- Cash flows in, prices out. Returns are not a calibration target.
- $$\theta\neq 1$$ is why long-run risk is priced.
- The ranking of $$\tilde\phi$$ across claims is the ranking of long-run premia.

Next: run the four steps on [the market]({{ '/time-series.html' | relative_url }}), then on [value versus growth]({{ '/cross-section.html' | relative_url }}).
