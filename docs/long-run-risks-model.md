---
title: The long-run risks model
nav_order: 4
---

# The long-run risks model
{: .no_toc }

1. TOC
{:toc}

Tidy Finance’s [capital asset pricing model](https://www.tidy-finance.org/chapters/capital-asset-pricing-model.html) chapter starts from mean-variance investors and arrives at

$$
E[R_i]-r_f=\beta_i\,\bigl(E[R_m]-r_f\bigr).
$$

The priced risk is covariance with the *market return*. This chapter is the same kind of walk-through for a different factor. In Bansal and Yaron (2004), the priced risk is news about *expected consumption growth*. We do not survey the literature. We write the objects, simulate them, and look at the analogue of the security market line. Run the chunks **in order**.

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

$$x_t$$ is *expected* growth. A shock to $$x_t$$ revises the whole future path of consumption, not just next month. That revision is **long-run risk**. Table II of Kiku (2006) uses monthly $$\rho=0.98$$ — a half-life of about three years.

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

<p class="caption">Gray: i.i.d. growth. Blue: the same short-run shocks plus an AR(1) expected-growth state. Long-run risk is the extra low-frequency swing.</p>

```python
(
    p9.ggplot(paths, p9.aes("t", "x"))
    + p9.geom_line()
    + p9.labs(x="Month", y="x_t", title="The expected-growth state")
)
```

![The expected-growth state](figures/lrr_state.svg)

<p class="caption">$$x_t$$ is small (a few tenths of a percent per month) and highly persistent. That is the factor.</p>

In the CAPM the factor is $$R_m-r_f$$. Here the factor is news in $$x_t$$.

## Why power utility is not enough

Power utility forces risk aversion and the EIS to be reciprocals: $$\gamma=1/\psi$$. Epstein and Zin (1989) / Weil (1989) let them differ. The IMRS is

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

$$\theta\neq 1$$. The term $$R_{c,t+1}^{\theta-1}$$ prices news about wealth. A shock to $$x_t$$ is news about the whole path of future consumption, hence about wealth. Under power utility $$\theta=1$$ and that term is 1. Then a gap in dividend loadings on $$x_t$$ cannot produce a large premium, no matter how persistent $$x_t$$ is.

The Euler equation is still the whole pricing theory: $$\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1$$. What changed is *which* shocks $$M_{t+1}$$ loads on.

## The analogue of beta

CAPM beta is the slope of asset excess returns on market excess returns. Long-run leverage $$\phi$$ is the slope of *dividend growth* on $$x_t$$:

$$
\Delta d_{t+1}=\mu_d+\phi x_t+\varphi_\sigma\sigma_t u_{t+1}.
$$

A claim with larger $$\phi$$ inherits more of the expected-growth news. Log price–dividend is affine in the state, $$z_t=\bar z+A_1 x_t+\cdots$$, with elasticity

$$
A_1=\frac{\phi-1/\psi}{1-\kappa_1\rho}.
$$

Because $$\rho$$ is close to one, $$A_1$$ is large: prices move a lot with $$x_t$$. The long-run premium is $$A_1$$ times the price of $$x$$-news. That is the analogue of $$\beta_i\times(E[R_m]-r_f)$$.

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
        title="Compensation for exposure to expected-growth news",
    )
)
```

![Long-run premium versus leverage](figures/lrr_sml.svg)

<p class="caption">The long-run-risks analogue of the security market line. The horizontal axis is $$\phi$$, not CAPM $$\beta$$. Growth, market, and value are Table II. Value sits further along the same line because its dividends load more on $$x_t$$.</p>

```text
A1 growth 43.1, market 37.5, value 88.9
Lambda_eps  5.95
```

Value’s $$A_1$$ is about twice growth’s. That is the cross-sectional prediction. It is *not* a prediction that value has a larger CAPM beta — often it does not.

`lrr.solve_analytical` is this linearization for every claim in `ModelParams`. The points on the figure come from Table II: $$\phi_G=2.6$$, $$\phi_m=2.8$$, $$\phi_V=6.2$$.

## Cash flows in, prices out

In the CAPM chapter you estimate $$\beta_i$$ from returns. Here you must **not** estimate $$\phi$$ from returns. $$\phi$$ is a cash-flow slope (dividend growth on slow consumption). Average returns, Sharpe ratios, and CAPM betas stay out of that step. The Euler equation is then a *test*: given those cash-flow numbers, do expected returns and $$P/D$$ look like the data?

That test is the rest of the book. [The market]({{ '/time-series.html' | relative_url }}) extracts $$x_t$$, loads market dividends on it, and checks the market’s $$E[R]$$ and $$E[\log P/D]$$. [Value versus growth]({{ '/cross-section.html' | relative_url }}) does the same for two legs with different $$\phi$$.

## Key takeaways

- Long-run risk is news about expected consumption growth $$x_t$$, not news about the market return.
- Consumption growth is persistent in the data (annual AC1 about 0.4). That is the empirical hook.
- Epstein–Zin with $$\psi\neq 1/\gamma$$ prices that news. Power utility does not.
- $$\phi$$ is to this model what $$\beta$$ is to the CAPM. It is a cash-flow loading, estimated without returns.
- Claims with larger $$\phi$$ earn a larger long-run premium and have more elastic $$P/D$$.

## Exercises

1. Set $$\psi=1/\gamma=0.1$$ so that $$\theta=1$$. Recompute the premium-versus-$$\phi$$ line. What happens to the slope?
2. Lower $$\rho$$ from 0.98 to 0.90 and recompute $$A_1$$ for $$\phi=6.2$$. How much of the value claim’s elasticity came from persistence?
3. Using the 1930–2003 consumption series, replace the two-year MA of lags with a three-year MA. Does the market’s OLS slope on that proxy stay in the same ballpark?
