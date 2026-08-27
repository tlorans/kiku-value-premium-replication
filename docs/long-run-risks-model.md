---
title: The long-run risks model
nav_order: 4
---

# The long-run risks model
{: .no_toc }

1. TOC
{:toc}

This chapter is the general-equilibrium counterpart of Tidy Finance’s [capital asset pricing model](https://www.tidy-finance.org/chapters/capital-asset-pricing-model.html). There the priced risk is covariance with the market return, and the objects are expected excess returns. Here the economy is Bansal and Yaron (2004) / Kiku (2006): the objects of the equilibrium are **asset prices and risk premia** — valuations and ex-ante compensations together.

Long-run risks are a small but highly persistent component that governs consumption growth. In addition, the model allows for time-variation in the conditional volatility of consumption — news about future economic uncertainty. Firms are distinguished by the exposure of their dividends to low- and high-frequency shocks in consumption, as well as news about future economic uncertainty. Time-non-separable Epstein and Zin (1989) preferences break the link between smoothing consumption over time and across states. The marginal rate of substitution then depends not only on present and future consumption, as under power utility, but also on the forward-looking return on the aggregate wealth portfolio.

What drives a premium in this economy? Shocks to the persistent growth-rate component significantly alter investors’ expectations about consumption far into the future, leading to large reactions in stock prices and sizable risk compensations. Assets’ valuations and risk premia therefore depend on the amount of low-frequency risks embodied in cash flows. Value firms are highly exposed to long-run consumption shocks; growth firms are driven more by short-lived fluctuations. Value firms exhibit higher elasticity of their price–dividend ratios to long-run consumption news, and have to provide investors with high ex-ante compensation.

We write those objects, simulate them, and look at the analogue of the security market line. Run the chunks **in order**.

```python
import numpy as np
import pandas as pd
import polars as pl
import plotnine as p9
import lrrcs as lrr
```

## Consumption is not white noise

The Mehra–Prescott equity-premium puzzle is usually stated under i.i.d. consumption growth and power utility. Annual U.S. consumption is not i.i.d. Load the NIPA series from [Financial data]({{ '/financial-data.html' | relative_url }}) and look at persistence.

```python
dc = pl.read_csv("data/consumption_annual.csv").sort("year")
y = dc["dc"].to_numpy()
len(y), round(float(y.mean() * 100), 2), round(float(y.std(ddof=1) * 100), 2)
round(float(np.corrcoef(y[:-1], y[1:])[0, 1]), 2)
```

```text
(74, 1.75, 2.37)
0.41
```

Seventy-four years, 1930–2003. Mean growth 1.75 percent, volatility 2.4 percent, first autocorrelation **0.41**. White noise would have autocorrelation near zero. That 0.41 is the fact the model is built around.

```python
(
    p9.ggplot(dc.to_pandas(), p9.aes("year", "dc"))
    + p9.geom_line()
    + p9.labs(x="Year", y="Δc", title="Annual consumption growth, 1930–2003")
)
```

![Real per-capita ND+S growth](figures/consumption_growth.svg)

<p class="caption">Log growth of real per-capita nondurables plus services. The series is positively autocorrelated. That is not a market return.</p>

## A persistent expected-growth state

Bansal and Yaron split consumption growth into a small persistent piece $$x_t$$ and a transitory shock:

$$
\Delta c_{t+1}=\mu+x_t+\sigma_t\eta_{t+1},\qquad
x_{t+1}=\rho x_t+\varphi_x\sigma_t e_{t+1}.
$$

$$x_t$$ is the small but highly persistent component that governs consumption growth. A shock to that growth-rate component significantly alters investors’ expectations about consumption far into the future. That revision is **long-run risk**. Table II of Kiku (2006) uses monthly $$\rho=0.98$$ — a half-life of about three years. Conditional volatility of consumption, $$\sigma_t$$, can move as well; that is news about future economic uncertainty.

Simulate two consumption paths with the same short-run shocks: one i.i.d., one with this $$x_t$$.

```python
mu, sigma, rho, phi_x = 0.0015, 0.0064, 0.98, 0.032
T = 240
rng = np.random.default_rng(1)
eta = rng.standard_normal(T)
eps = rng.standard_normal(T)

iid = mu + sigma * eta
x = np.zeros(T)
dc_m = np.empty(T)
for t in range(T):
    dc_m[t] = mu + x[t] + sigma * eta[t]
    if t + 1 < T:
        x[t + 1] = rho * x[t] + phi_x * sigma * eps[t]

paths = pd.DataFrame({
    "t": np.arange(T),
    "iid": np.cumsum(iid),
    "lrr": np.cumsum(dc_m),
    "x": x,
})
(
    p9.ggplot(paths, p9.aes("t"))
    + p9.geom_line(p9.aes(y="iid"), color="#888888")
    + p9.geom_line(p9.aes(y="lrr"), color="#1f4e79")
    + p9.labs(
        x="Month",
        y="log C (normalized)",
        title="Consumption paths: i.i.d. growth vs long-run risk",
    )
)
```

![Consumption paths with and without long-run risk](figures/lrr_consumption_paths.svg)

<p class="caption">Gray: i.i.d. growth. Blue: the same short-run shocks plus a small but highly persistent component in consumption growth. That extra low-frequency swing is long-run risk.</p>

```python
(
    p9.ggplot(paths, p9.aes("t", "x"))
    + p9.geom_line()
    + p9.labs(x="Month", y="x_t", title="The expected-growth state")
)
```

![The expected-growth state](figures/lrr_state.svg)

<p class="caption">$$x_t$$ is small (a few tenths of a percent per month) and highly persistent. That is the low-frequency risk embodied in cash flows.</p>

In the CAPM the factor is $$R_m-r_f$$. Here the factor is news in the persistent growth-rate component — and, separately, news about future economic uncertainty.

## Time-non-separable preferences

Power utility forces risk aversion and the EIS to be reciprocals: $$\gamma=1/\psi$$. That ties agents’ attitude towards smoothing consumption over time to their attitude across states of nature. Epstein and Zin (1989) / Weil (1989) break that link. The intertemporal marginal rate of substitution is

$$
M_{t+1}=\delta^\theta (C_{t+1}/C_t)^{-\theta/\psi} R_{c,t+1}^{\theta-1},
\qquad
\theta=\frac{1-\gamma}{1-1/\psi}.
$$

```python
delta, gamma, psi = 0.999, 10.0, 1.5
theta = (1.0 - gamma) / (1.0 - 1.0 / psi)
gamma, 1.0 / psi, theta
```

```text
(10.0, 0.667, -27.0)
```

$$\theta\neq 1$$. The term $$R_{c,t+1}^{\theta-1}$$ is the forward-looking return on the aggregate wealth portfolio. A shock to $$x_t$$ revises expected consumption far into the future, hence wealth, hence $$M_{t+1}$$. Under power utility $$\theta=1$$ and that term is 1. Then a gap in dividend loadings on low-frequency consumption shocks cannot produce large reactions in stock prices or sizable risk compensations, no matter how persistent $$x_t$$ is.

The Euler equation is still the whole pricing theory: $$\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1$$. The objects it delivers are **valuations and risk premia**.

## Low-frequency risks in cash flows

CAPM beta is the slope of asset excess returns on market excess returns. Long-run leverage $$\phi$$ is the exposure of *dividends* to the persistent growth-rate component:

$$
\Delta d_{t+1}=\mu_d+\phi x_t+\varphi_\sigma\sigma_t u_{t+1}.
$$

Firms are distinguished by this exposure, and by their loading on short-lived consumption shocks and on news about future economic uncertainty. Log price–dividend is affine in the state, $$z_t=\bar z+A_1 x_t+\cdots$$, with elasticity

$$
A_1=\frac{\phi-1/\psi}{1-\kappa_1\rho}.
$$

Because $$\rho$$ is close to one, $$A_1$$ is large: valuations react strongly to long-run consumption news. The long-run risk premium is $$A_1$$ times the price of that news. Assets’ valuations and risk premia, therefore, depend on the amount of low-frequency risk embodied in their cash flows.

```python
psi, rho, gamma = 1.5, 0.98, 10.0
phi_x, sigma = 0.032, 0.0064
mean_zc = 3.5
kappa_c1 = np.exp(mean_zc) / (1.0 + np.exp(mean_zc))
ratio = kappa_c1 * phi_x / (1.0 - kappa_c1 * rho)
Lambda_eps = (gamma - 1.0 / psi) * ratio
mean_z = 3.24
kappa1 = np.exp(mean_z) / (1.0 + np.exp(mean_z))
phis = np.linspace(1.0, 8.0, 29)
A1 = (phis - 1.0 / psi) / (1.0 - kappa1 * rho)
prem = 12.0 * kappa1 * A1 * phi_x * Lambda_eps * (sigma ** 2) * 100
line = pd.DataFrame({"phi": phis, "premium": prem})

sol = lrr.solve_analytical(lrr.get_table_ii_params())
pts = pd.DataFrame({
    "phi": [2.6, 2.8, 6.2],
    "premium": [100 * sol.premium_lr[k] for k in ("growth", "market", "value")],
    "name": ["Growth", "Market", "Value"],
})
(
    p9.ggplot()
    + p9.geom_line(line, p9.aes("phi", "premium"))
    + p9.geom_point(pts, p9.aes("phi", "premium"), size=3)
    + p9.geom_text(pts, p9.aes("phi", "premium", label="name"), nudge_y=0.08)
    + p9.labs(
        x="Long-run leverage φ",
        y="Long-run premium (% per year)",
        title="Valuations’ compensation for low-frequency cash-flow risk",
    )
)
```

![Long-run premium versus leverage](figures/lrr_sml.svg)

<p class="caption">The general-equilibrium analogue of the security market line. The horizontal axis is exposure of dividends to long-run consumption shocks, not CAPM $$\beta$$. Value firms are highly exposed to those shocks; growth firms less so. That dispersion shows up in valuations and in ex-ante premia.</p>

```text
A1 growth 43.1, market 37.5, value 88.9
Lambda_eps  5.95
```

Value’s $$A_1$$ is about twice growth’s: value firms exhibit higher elasticity of their price–dividend ratios to long-run consumption news, and have to provide investors with high ex-ante compensation. That is *not* a prediction that value has a larger CAPM beta — often it does not.

`lrr.solve_analytical` is this linearization for every claim in `ModelParams`. The points on the figure come from Table II: $$\phi_G=2.6$$, $$\phi_m=2.8$$, $$\phi_V=6.2$$.

## Cash flows in, prices and premia out

In the CAPM chapter you estimate $$\beta_i$$ from returns. Here you must **not** estimate $$\phi$$ from returns. $$\phi$$ is a cash-flow exposure (dividend growth on the persistent consumption component). Average returns, Sharpe ratios, and CAPM betas stay out of that step. The Euler equation is then a *test* of the general equilibrium: given those cash-flow numbers, do **valuations and risk premia** look like the data?

That test is the rest of the book. [The market]({{ '/time-series.html' | relative_url }}) extracts $$x_t$$, measures the market’s exposure to long-run consumption shocks, and checks the market’s price–dividend ratio and equity premium. [Value versus growth]({{ '/cross-section.html' | relative_url }}) does the same for two legs: value highly exposed to low-frequency shocks, growth driven more by short-lived fluctuations.

## Key takeaways

- Long-run risks are a small but highly persistent component that governs consumption growth.
- The model allows for time-variation in the conditional volatility of consumption — news about future economic uncertainty.
- Firms are distinguished by the exposure of their dividends to low- versus high-frequency consumption shocks.
- Time-non-separable Epstein–Zin preferences break the link between smoothing consumption over time and across states.
- The MRS depends on the forward-looking return on the aggregate wealth portfolio.
- Shocks to the growth-rate component alter expectations far into the future, producing large reactions in stock prices and sizable risk compensations.
- Valuations and risk premia depend on the amount of low-frequency risks embodied in cash flows.
- Value firms are highly exposed to long-run consumption shocks; growth firms are driven more by short-lived fluctuations.
- Value firms exhibit higher elasticity of their price–dividend ratios to long-run consumption news, and have to provide investors with high ex-ante compensation.
- $$\phi$$ is estimated from cash flows. Returns are the test.

## Exercises

1. Set $$\psi=1/\gamma=0.1$$ so that $$\theta=1$$. Recompute the premium-versus-$$\phi$$ line. What happens to the slope?
2. Lower $$\rho$$ from 0.98 to 0.90 and recompute $$A_1$$ for $$\phi=6.2$$. How much of the value claim’s elasticity came from persistence?
3. Using the 1930–2003 consumption series, replace the two-year MA of lags with a three-year MA. Does the market’s OLS slope on that proxy stay in the same ballpark?
