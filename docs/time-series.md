---
title: The market
nav_order: 5
---

# The market
{: .no_toc }

1. TOC
{:toc}

**Question.** Can this household price the *market* — the value-weighted claim on all listed stocks — year after year?

That is the test Bansal and Yaron (2004) wrote the model for. One claim. Not a ranking of firms. [Financial data]({{ '/financial-data.html' | relative_url }}) built consumption from NIPA and market dividends from CRSP via Campbell–Shiller. Here we use the 1930–2003 sample that pipeline writes. The recipe is [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}).

```python
import polars as pl
import plotnine as p9
import tidyfinance as tf
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
panel = pl.read_csv("data/annual_panel.csv")
rf = pl.read_csv("data/rf_annual.csv")
mkt = panel.filter(pl.col("claim") == "Market").join(dc, on="year")
```

## What long-run risk is

Consumption growth is not white noise. It has a small persistent expected-growth piece $$x_t$$:

$$
\Delta c_{t+1}=\mu+x_t+\sigma_t\eta_{t+1},\qquad x_{t+1}=\rho x_t+\varphi_x\sigma_t e_{t+1}.
$$

News about $$x_t$$ is long-run risk. Epstein–Zin with $$\psi\neq 1/\gamma$$ prices that news. A claim’s loading $$\phi$$ on $$x_t$$ is how much of it the claim inherits.

The annual picture is a two-year moving average of lagged $$\Delta c$$. Raw growth is jagged. The MA is the slow component.

```python
import polars as pl
import plotnine as p9

dc = pl.read_csv("data/consumption_annual.csv").sort("year")
plot_df = dc.with_columns(
    pl.col("dc").shift(1).rolling_mean(window_size=2).alias("ma")
)
(
    p9.ggplot(plot_df.to_pandas(), p9.aes("year"))
    + p9.geom_line(p9.aes(y="dc"))
    + p9.geom_line(p9.aes(y="ma"), color="steelblue")
    + p9.labs(x="Year", y="Δc", title="Consumption growth and a two-year MA of lags")
)
```

![Consumption growth and two-year MA](figures/consumption_ma.svg)

<p class="caption">Raw annual $$\Delta c$$ (black) and the two-year MA of lagged growth (blue). The blue line is the annual picture of $$x_t$$.</p>

The blue line is the annual stand-in for $$x_t$$. Table II’s monthly $$\rho=0.98$$ is the same object on a finer clock.

## Estimate x_t

**Proxy (the estimator we keep).** Same MA, then the package:

```python
import polars as pl
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
x_ma = lrr.expected_growth_proxy(dc["dc"], window=2)
```

`x_ma[t]` is the mean of `dc[t-2:t]`, `nan` on the first two years.

**Filter (the link to the solver).** A univariate Kalman / AR(1) on annual $$\Delta c$$:

$$
y_t=\mu+x_t+v_t,\qquad x_{t+1}=\rho x_t+w_t.
$$

```python
import numpy as np
import polars as pl
import plotnine as p9
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
y = dc["dc"].to_numpy()
mu = float(y.mean())
rho0 = float(np.corrcoef(y[:-1], y[1:])[0, 1])
# ... Kalman MLE for rho, q, r, then the filtered path ...

out = lrr.filter_expected_growth(dc["dc"])
out["rho"]   # annual persistence, not monthly 0.98
plot_df = dc.with_columns(
    pl.Series("ma", lrr.expected_growth_proxy(dc["dc"], window=2)),
    pl.Series("x_filt", out["x"]),
)
(
    p9.ggplot(plot_df.to_pandas(), p9.aes("year"))
    + p9.geom_line(p9.aes(y="dc"))
    + p9.geom_line(p9.aes(y="ma"), color="steelblue")
    + p9.geom_line(p9.aes(y="x_filt"), color="darkorange")
    + p9.labs(x="Year", y="Δc", title="MA proxy and filtered x̂_t")
)
```

```text
out["rho"]
0.43
```

![MA proxy and filtered expected growth](figures/xt_proxy_filter.svg)

<p class="caption">Consumption growth, the MA proxy (blue), and the Kalman filter $$\hat x_t$$ (orange). Filtered annual $$\rho\approx 0.43$$. The solver iterates the monthly counterpart $$0.98$$.</p>

Do not take $$\phi$$ or Table II numbers from this filter. Calibration below uses the MA.

## Calibrate dividends

Kiku (2006) equation (19): $$\Delta d_t=d_0+\tilde\phi\,\mathrm{MA}(\Delta c,2)+\varepsilon_t$$.

```python
import numpy as np
import polars as pl
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
mkt = pl.read_csv("data/annual_panel.csv").filter(pl.col("claim") == "Market")
joined = mkt.join(dc, on="year").drop_nulls()
x = lrr.expected_growth_proxy(joined["dc"], window=2)
y = joined["dgrowth"].to_numpy()
mask = np.isfinite(x)
phi_tilde = float(np.cov(y[mask], x[mask], ddof=0)[0, 1] / np.var(x[mask], ddof=0))
```

Then the same slope from the package, and the rest of the dividend process:

```python
import polars as pl
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
mkt = pl.read_csv("data/annual_panel.csv").filter(pl.col("claim") == "Market")
joined = mkt.join(dc, on="year").drop_nulls()
phi_tilde = lrr.estimate_long_run_leverage(joined["dc"], joined["dgrowth"], window=2)
div = lrr.calibrate_from_data(
    joined["dc"].to_numpy(),
    market=joined["dgrowth"].to_numpy(),
    frequency="annual",
    window=2,
)
div["market"].mu, div["market"].phi, div["market"].phi_sigma, div["market"].alpha
lrr.print_calibration_summary(div)
```

```text
Portfolio          μ (m)     φ (long-run)   φ_σ      α
-------------------------------------------------------
market              0.00076     0.722       5.33    0.57
```

Printed $$\tilde\phi$$ on the market is about $$0.72$$ in this replica file (about $$0.66$$ in Kiku’s Table VI). That number is a *ranking check*. The solver wants monthly $$\phi$$. Table II locks market $$\mu=0.0012$$, $$\phi=2.8$$, $$\varphi_\sigma=7.5$$, $$\alpha=0.55$$. Simulation and pricing below use `lrr.get_table_ii_params()`, not the annual slope as a monthly loading. Average returns never enter.

## Simulate cash flows

The recursion is the same one as above, now monthly, with Table II numbers:

$$
\Delta c_{t+1}=\mu_c+x_t+\sigma_t\eta_{t+1},\qquad
\Delta d_{t+1}=\mu_d+\phi x_t+\varphi_\sigma\sigma_t u_{t+1}.
$$

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
params.dividends["market"].phi  # 2.8
params.cons.rho                 # 0.98
print(lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=params))
lrr.print_moments(
    lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=params)
)
```

```text
Model-implied annual moments (compare to Tables III–IV):
  Consumption: E=1.82%, vol=2.44%, AC1=0.16
  market  : E=0.68%, vol=16.36%, AC1=0.03, corr(c,d)=0.57
```

Twenty simulated samples are noisy. Prose target (1000 samples of 74 years): consumption mean growth 1.86 percent against 1.96 in the data; volatility 2.16 against 2.20; first autocorrelation 0.43 against 0.44. Market dividend moments print on the same object. If those fail, stop. The premium that comes next would then be a free parameter in disguise.

## Solve and check returns and prices

The IMRS and Euler equation are on [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}). Table II is the default household.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
lrr.print_long_short_premium(lrr.solve_analytical(params))
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
lrr.print_asset_pricing_moments(lrr.compute_asset_pricing_moments(solver))
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

The Euler-equation check is both columns, returns **and** prices:

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

E[R] is the average simple return, percent per year. E[pd] is average $$\log(P/D)$$. Market return volatility is 20.1 percent in both. Success is **both** columns close. A match on returns with a wrong price–dividend ratio is a fail. The safe rate is about seventy basis points too high. The equity premium is a little short of the sample. Close enough to ask a second question.

One simulated path, so you see the series, not only the table. Log $$P/D$$ uses the analytical map $$z=\bar z+A_1 x+A_2(\sigma^2-\bar\sigma^2)$$. That is chapter code, not a new helper.

```python
import numpy as np
import polars as pl
import plotnine as p9
import lrrcs as lrr

params = lrr.get_table_ii_params()
path = lrr.Dynamics(params, seed=1).simulate_cashflows(T=74 * 12)
sol = lrr.solve_analytical(params)
x = path["x"]
s2 = path["sigma2"]
z = (
    sol.mean_log_pd["market"]
    + sol.A1["market"] * x
    + sol.A2["market"] * (s2 - params.cons.sigma**2)
)
sim = pl.DataFrame({"t": np.arange(len(x)), "x": x, "dd": path["dd_market"], "log_pd": z})
pdf = sim.to_pandas()
(
    p9.ggplot(pdf, p9.aes("t", "x"))
    + p9.geom_line()
    + p9.labs(x="Month", y="x_t", title="Simulated long-run risk")
)
(
    p9.ggplot(pdf, p9.aes("t", "dd"))
    + p9.geom_line()
    + p9.labs(x="Month", y="Δd", title="Simulated market dividend growth")
)
(
    p9.ggplot(pdf, p9.aes("t", "log_pd"))
    + p9.geom_line()
    + p9.labs(x="Month", y="log(P/D)", title="Model price–dividend along the path")
)
```

![Simulated long-run risk](figures/sim_xt.svg)

<p class="caption">One simulated monthly path of $$x_t$$.</p>

![Simulated market dividend growth](figures/sim_dd.svg)

<p class="caption">Market dividend growth along the same path.</p>

![Model price–dividend along the path](figures/sim_log_pd.svg)

<p class="caption">Model $$\log(P/D)$$ from $$z=\bar z+A_1 x+A_2(\sigma^2-\bar\sigma^2)$$. Returns and prices have to match together.</p>

Value and growth are [Value versus growth]({{ '/cross-section.html' | relative_url }}). Matching the market does not rank firms.
