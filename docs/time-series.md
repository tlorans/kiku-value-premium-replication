---
title: The Time Series
nav_order: 5
---

# The Time Series
{: .no_toc }

1. TOC
{:toc}

Now we test the model where Bansal and Yaron (2004) built it to be tested: the aggregate market, year after year. Two questions have organized macro-finance for forty years. Why is the equity premium so large — why does one claim on aggregate cash flows out-earn a Treasury bill by six to eight percentage points? And why do valuations move so much — why does the market's price–dividend ratio swing from 10 to 88 across this sample? A DCF has no answer to either; it takes the premium and the valuation as inputs. The equilibrium must produce both as outputs, from cash flows alone, and it gets no partial credit: *a match on the equity premium with the wrong price–dividend ratio is a fail.*

The plan follows the model's two halves. First the cash-flow side, built from data: extract the persistent component $$x_t$$ from consumption growth, measure how hard the market's dividends load on it, and confirm that simulated cash flows look like sample cash flows. Then the discount-rate side does its work: the Epstein–Zin household prices the calibrated claim through the Euler equation, and we read off the premium and the valuation together. Average returns appear nowhere until the final scoreboard. One claim; the ranking of firms is [The Cross Section]({{ '/cross-section.html' | relative_url }}).

We use the following packages. Run the chunks **in order**: later snippets reuse `dc`, `mkt`, and `y`.

```python
import numpy as np
import pandas as pd
import polars as pl
import plotnine as p9
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv").sort("year")
panel = pl.read_csv("data/annual_panel.csv")
rf = pl.read_csv("data/rf_annual.csv")
y = dc["dc"].to_numpy()
```

## Preparing the sample

[Financial data]({{ '/financial-data.html' | relative_url }}) already wrote annual consumption growth and Campbell–Shiller market dividends for 1930–2003. We do not rebuild those series. Join them on `year`. `ret` is the real simple return, `dgrowth` is log dividend growth, `pd` is the year-end price–dividend ratio.

```python
mkt = (
    panel.filter(pl.col("claim") == "Market")
    .join(dc, on="year")
    .sort("year")
)
mkt.head()
```

```text
 year  claim   ret      dgrowth    pd      dc
 1930  Market -0.258    -0.026     15.76  -0.053
 1931  Market -0.377    -0.131     10.52  -0.024
 1932  Market  0.044    -0.385     15.07  -0.088
 1933  Market  0.632    -0.172     28.00  -0.021
 1934  Market -0.013     0.098     24.06   0.062
 1935  Market  0.419     0.077     30.34   0.042
```

Seventy-four annual observations. Consumption growth averages 1.75 percent with volatility 2.37 percent — the endowment is astonishingly smooth, which is precisely why the premium is a puzzle. Its first autocorrelation is 0.41: not white noise, and that autocorrelation is the crack the whole model climbs through. Market returns average 8.5 percent; mean $$P/D$$ is about 31 (log $$P/D$$ about 3.33). The real T-bill on this reconstruction is near zero; Kiku's printed sample is 0.91 percent.

```python
print(len(y), y.mean() * 100, y.std(ddof=1) * 100)
print(np.corrcoef(y[:-1], y[1:])[0, 1])
print(round(float(rf["rf"].mean() * 100), 2))
mkt.select("ret", "dgrowth", "pd").describe()
```

```text
74 1.75 2.37
0.41
0.07
```

| statistic | ret | dgrowth | pd |
|:---|---:|---:|---:|
| mean | 0.085 | 0.009 | 30.85 |
| std | 0.201 | 0.110 | 16.07 |
| min | −0.377 | −0.433 | 10.52 |
| max | 0.632 | 0.422 | 88.07 |

Look at the last column. The valuation is not a constant the way a Gordon formula would have it; it is a series with a standard deviation half its mean. The Euler equation has to match this valuation, not only the average return.

```python
(
    p9.ggplot(
        mkt.with_columns(pl.col("pd").log().alias("log_pd")).to_pandas(),
        p9.aes("year", "log_pd"),
    )
    + p9.geom_line()
    + p9.labs(x="Year", y="log(P/D)", title="Market price–dividend, 1930–2003")
)
```

![Market log price–dividend](figures/market_log_pd.svg)

<p class="caption">Market $$\log(P/D)$$ from Campbell–Shiller on CRSP. Valuations and risk premia have to match together.</p>

## Extract expected growth

This section and the next are the cash-flow model, built from data. [The long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}) split consumption growth into a small persistent piece $$x_t$$ and a transitory shock. Fine on paper — but does the annual sample contain such an object, and can we see it? If growth were i.i.d., only the current shock would be priced and the chapter would end here. It is not: AC1 is 0.41.

You can already *see* $$x_t$$ with no machinery at all. Average the last two years of consumption growth. Raw $$\Delta c$$ is jagged; the moving average is the slow component — the annual picture of the small but highly persistent component that governs consumption growth.

Kiku's equation (19) uses that two-year MA as the regressor for dividend growth. Write it without the package: at date $$t$$, average $$\Delta c_{t-2}$$ and $$\Delta c_{t-1}$$ (not the current year). Then the shortcut.

```python
window = 2
ma = np.full(len(y), np.nan)
for t in range(window, len(y)):
    ma[t] = float(np.mean(y[t - window : t]))
dc.with_columns(pl.Series("ma", ma)).head(6)
lrr.expected_growth_proxy(y, window=2)[:6]
```

```text
 year     dc      ma
 1930  -0.053     NA
 1931  -0.024     NA
 1932  -0.088  -0.038
 1933  -0.021  -0.056
 1934   0.062  -0.055
 1935   0.042   0.020
```

The first two years are missing by construction. Plot the same `ma` we will regress on.

```python
plot_df = dc.with_columns(pl.Series("ma", ma))
(
    p9.ggplot(plot_df.to_pandas(), p9.aes("year"))
    + p9.geom_line(p9.aes(y="dc"))
    + p9.geom_line(p9.aes(y="ma"), color="steelblue")
    + p9.labs(
        x="Year",
        y="Δc",
        title="Consumption growth and a two-year MA of lags",
    )
)
```

![Consumption growth and two-year MA](figures/consumption_ma.svg)

<p class="caption">Raw annual $$\Delta c$$ (black) and the two-year MA of lagged growth (blue). The blue line is the annual picture of $$x_t$$.</p>

Table II of Kiku (2006) puts this object on a monthly clock with $$\rho=0.98$$ (about $$0.98^{12}\approx 0.78$$ per year in a simple compounding sense; the annual MA is the counterpart we can plot).

A moving average is honest but crude. The solver does not iterate a two-year MA; it iterates an AR(1) state. The annual analogue is the linear Gaussian system

$$
y_t=\mu+x_t+v_t,\qquad x_{t+1}=\rho x_t+w_t,
$$

with $$v_t\sim N(0,r)$$ and $$w_t\sim N(0,q)$$ — observed growth is the hidden state plus noise, and the state decays at $$\rho$$. The Kalman filter gives $$E[x_t\mid y_{1:t}]$$, and we estimate $$(\rho,q,r)$$ by maximum likelihood. Here is the whole procedure, fifteen lines, no black box:

```python
from scipy.optimize import minimize

def kalman_filter(y, mu, rho, q, r):
    n = y.size
    x_filt = np.empty(n)
    x_pred = 0.0
    p_pred = q / max(1.0 - rho * rho, 1e-8)
    loglik = 0.0
    for t in range(n):
        innov = y[t] - mu - x_pred
        s = p_pred + r
        k = p_pred / s
        x_upd = x_pred + k * innov
        p_upd = (1.0 - k) * p_pred
        loglik += -0.5 * (np.log(2.0 * np.pi * s) + innov * innov / s)
        x_filt[t] = x_upd
        x_pred = rho * x_upd
        p_pred = rho * rho * p_upd + q
    return loglik, x_filt

mu = float(y.mean())
var = float(np.var(y))
rho0 = float(np.clip(np.corrcoef(y[:-1], y[1:])[0, 1], 1e-6, 0.999))
q0 = r0 = max(var / 2.0, 1e-12)

def nll(theta):
    rho, q, r = theta
    ll, _ = kalman_filter(y, mu, rho, q, r)
    return -ll if np.isfinite(ll) else 1e20

res = minimize(
    nll,
    x0=np.array([rho0, q0, r0]),
    method="L-BFGS-B",
    bounds=[(1e-6, 0.999), (1e-12, None), (1e-12, None)],
)
rho, q, r = res.x
loglik, x_filt = kalman_filter(y, mu, rho, q, r)
rho, q, r, loglik
```

```text
(0.43, 0.00046, 1e-12, 178.9)
```

Annual persistence comes back at about 0.43, close to the raw AC1 of 0.41. Measurement-error variance sits on the lower bound: once $$x_t$$ is in the model, almost all of the annual series is state, not noise. `lrr.filter_expected_growth(y)` is this filter plus the MLE. Overlay the two extractors:

```python
plot_df = dc.with_columns(
    pl.Series("ma", ma),
    pl.Series("x_filt", x_filt),
)
(
    p9.ggplot(plot_df.to_pandas(), p9.aes("year"))
    + p9.geom_line(p9.aes(y="dc"))
    + p9.geom_line(p9.aes(y="ma"), color="steelblue")
    + p9.geom_line(p9.aes(y="x_filt"), color="darkorange")
    + p9.labs(x="Year", y="Δc", title="MA proxy and filtered x̂_t")
)
```

![MA proxy and filtered expected growth](figures/xt_proxy_filter.svg)

<p class="caption">Consumption growth, the MA proxy (blue), and the Kalman filter $$\hat x_t$$ (orange). Filtered annual $$\rho\approx 0.43$$. The solver iterates the monthly counterpart $$0.98$$.</p>

Do **not** take $$\phi$$ or Table II numbers from this filter. Calibration uses the MA, as in the paper.

## One cash-flow exposure

We have the state. Now, how hard do the market's dividends lever it? This is the model's $$g$$, estimated — and notice what sits on the right-hand side of Kiku's equation (19): the consumption MA, and nothing else.

$$
\Delta d_t=d_0+\tilde\phi\,\mathrm{MA}(\Delta c,2)+\varepsilon_t.
$$

No return, no price, no premium. Align the market `dgrowth` series with the same `ma` and run OLS with an intercept.

```python
dd = mkt["dgrowth"].to_numpy()
mask = np.isfinite(ma) & np.isfinite(dd)
x = ma[mask] - ma[mask].mean()
e = dd[mask] - dd[mask].mean()
phi_tilde = float(np.dot(x, e) / np.dot(x, x))
resid = dd[mask] - (dd[mask].mean() + phi_tilde * (ma[mask] - ma[mask].mean()))
innov = np.empty_like(y)
innov[0] = 0.0
rho_c = float(np.corrcoef(y[:-1], y[1:])[0, 1])
innov[1:] = y[1:] - rho_c * y[:-1]
alpha = float(np.corrcoef(resid, innov[mask])[0, 1])
phi_sigma = float(np.std(resid) / np.std(innov[mask]))
mu_d_annual = float(np.mean(dd))
phi_tilde, mu_d_annual, phi_sigma, alpha
```

```text
(0.722, 0.0092, 5.33, 0.57)
```

The slope $$\tilde\phi=0.72$$ is the *ranking check* (Kiku's Table VI prints about 0.66 for the market, with a large standard error — seventy-four annual observations buy you a ranking, not a third decimal). Plot the same regression.

```python
plot_df = mkt.with_columns(pl.Series("ma", ma)).filter(
    pl.col("ma").is_finite() & pl.col("dgrowth").is_finite()
)
(
    p9.ggplot(plot_df.to_pandas(), p9.aes("ma", "dgrowth"))
    + p9.geom_point()
    + p9.labs(
        x="Two-year MA of lagged Δc",
        y="Market Δd",
        title="Market cash-flow exposure, not returns",
    )
)
```

![Market dividend growth against the MA](figures/market_dd_vs_ma.svg)

<p class="caption">Market dividend growth against the two-year MA of lagged consumption. Average returns never entered.</p>

`lrr.estimate_long_run_leverage` and `lrr.calibrate_from_data` wrap the same arithmetic.

```python
lrr.estimate_long_run_leverage(y, dd, window=2)
lrr.print_calibration_summary(
    lrr.calibrate_from_data(y, market=dd, frequency="annual", window=2)
)
```

```text
Portfolio          μ (m)     φ (long-run)   φ_σ      α
-------------------------------------------------------
market              0.00076     0.722       5.33    0.57
```

The solver wants *monthly* $$\phi$$. Table II locks $$\mu=0.0012$$, $$\phi=2.8$$, $$\varphi_\sigma=7.5$$, $$\alpha=0.55$$. Simulation and pricing below use those numbers, not the annual slope as a monthly loading. Average returns never entered.

## Simulate cash flows

Before the household is allowed to price anything, the calibrated cash-flow model has to pass its own exam: simulate it, and check that the simulated consumption and dividends look like the sample. This is where the cash-flow side either earns its keep or gets sent back. Write one monthly path, annualize by summing twelve log-growths, then repeat. Then the shortcut.

```python
mu_c, rho, phi_x, sigma = 0.0015, 0.98, 0.032, 0.0064
nu, sigma_w = 0.99, 0.0000017
mu_d, phi, phi_sig, alpha = 0.0012, 2.8, 7.5, 0.55
years, n_sims, seed = 74, 20, 1

def annualize(monthly):
    n = len(monthly) // 12
    return monthly[: n * 12].reshape(n, 12).sum(axis=1)

def one_path(rng, T):
    x = np.zeros(T)
    s2 = np.full(T, sigma ** 2)
    dc_m = np.empty(T)
    dd_m = np.empty(T)
    for t in range(T):
        eta = rng.standard_normal()
        dc_m[t] = mu_c + x[t] + np.sqrt(s2[t]) * eta
        u = alpha * eta + np.sqrt(max(1.0 - alpha ** 2, 0.0)) * rng.standard_normal()
        dd_m[t] = mu_d + phi * x[t] + phi_sig * np.sqrt(s2[t]) * u
        if t + 1 < T:
            eps = rng.standard_normal()
            w = rng.standard_normal()
            x[t + 1] = rho * x[t] + phi_x * np.sqrt(s2[t]) * eps
            s2[t + 1] = max(sigma ** 2 * (1 - nu) + nu * s2[t] + sigma_w * w, 1e-12)
    return x, s2, dc_m, dd_m

rng = np.random.default_rng(seed)
T = years * 12
cons_mean, cons_vol, cons_ac1 = [], [], []
dd_mean, dd_vol = [], []
for _ in range(n_sims):
    _, _, dc_m, dd_m = one_path(rng, T)
    dc_a = annualize(dc_m)
    dd_a = annualize(dd_m)
    cons_mean.append(dc_a.mean() * 100)
    cons_vol.append(dc_a.std() * 100)
    cons_ac1.append(np.corrcoef(dc_a[:-1], dc_a[1:])[0, 1])
    dd_mean.append(dd_a.mean() * 100)
    dd_vol.append(dd_a.std() * 100)

{
    "E[dc]": np.mean(cons_mean),
    "sigma(dc)": np.mean(cons_vol),
    "AC1": np.mean(cons_ac1),
    "E[dd]": np.mean(dd_mean),
    "sigma(dd)": np.mean(dd_vol),
}
```

```text
{'E[dc]': 1.82, 'sigma(dc)': 2.44, 'AC1': 0.16, 'E[dd]': 0.68, 'sigma(dd)': 16.36}
```

Twenty samples of 74 years are noisy (annual AC1 in particular). With 1000 samples the model is close to the data on consumption: mean 1.86 vs 1.96, volatility 2.16 vs 2.20, AC1 0.43 vs 0.44. `lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1)` is the same Monte Carlo. If those cash-flow moments fail, stop. A premium matched afterward would be a free parameter in disguise.

## Solve and check returns and prices

Now, and only now, the discount-rate machinery. The Euler equation is $$E_t[M_{t+1}R_{i,t+1}]=1$$ with the Epstein–Zin IMRS from [the long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}); we do not re-derive it. Nothing on the discount-rate side is re-tuned to this chapter — the household is the one calibrated in Table II, and it now prices the cash flows we just built. The log-linear price–dividend ratio of a claim is affine in the state,

$$
z_t=\bar z+A_1 x_t+A_2(\sigma_t^2-\bar\sigma^2),
$$

with elasticity

$$
A_1=\frac{\phi-1/\psi}{1-\kappa_1\rho}.
$$

There it is again — cash-flow leverage $$\phi$$ over the household's $$1/\psi$$, amplified by persistence. Larger $$\phi$$ means prices rise more when expected growth is high, and the long-run premium is $$A_1$$ times the price of $$x$$-news. With Table II's market $$\phi=2.8$$, $$\psi=1.5$$, $$\rho=0.98$$, and $$\bar z=3.24$$:

```python
phi, psi, rho = 2.8, 1.5, 0.98
mean_z = 3.24
kappa1 = np.exp(mean_z) / (1.0 + np.exp(mean_z))
A1 = (phi - 1.0 / psi) / (1.0 - kappa1 * rho)
kappa1, A1
```

```text
(0.962, 56.3)
```

`lrr.solve_analytical` returns that elasticity for every claim, plus the long-run premium. Market $$A_1$$ is large: prices move a lot with $$x_t$$.

```python
params = lrr.get_table_ii_params()
sol = lrr.solve_analytical(params)
lrr.print_long_short_premium(sol)
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

The scoreboard. `lrr.compute_asset_pricing_moments` integrates the Euler equation on a grid; Kiku's Table VII (1000 samples) is the comparison. Remember the standard: the premium and the valuation come as a pair, and a match on one with a miss on the other is a fail.

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

Look at the pair, not just the first column. The model earns 7.53 percent against 8.56 in the data — a little short — *and* prices the claim at a mean log $$P/D$$ of 3.24 against 3.34. Market return volatility is 20.1 percent in both. The blemish is the safe rate, about seventy basis points too high. The verdict: not a bullseye, but both members of the pair land, from cash flows that never saw a return. Close enough to ask a second question — and the second question is the cross section.

One simulated monthly path, using the affine map we just wrote. $$A_2$$ is the elasticity of $$\log P/D$$ to news about future economic uncertainty — time-variation in the conditional volatility of consumption — from the same analytical solution.

```python
x, s2, dc_m, dd_m = one_path(np.random.default_rng(1), 74 * 12)
s2_bar = sigma ** 2
z = sol.mean_log_pd["market"] + sol.A1["market"] * x + sol.A2["market"] * (s2 - s2_bar)
sim = pd.DataFrame({"t": np.arange(len(x)), "x": x, "dd": dd_m, "log_pd": z})
(
    p9.ggplot(sim, p9.aes("t", "x"))
    + p9.geom_line()
    + p9.labs(x="Month", y="x_t", title="Simulated long-run risk")
)
(
    p9.ggplot(sim, p9.aes("t", "dd"))
    + p9.geom_line()
    + p9.labs(x="Month", y="Δd", title="Simulated market dividend growth")
)
(
    p9.ggplot(sim, p9.aes("t", "log_pd"))
    + p9.geom_line()
    + p9.labs(x="Month", y="log(P/D)", title="Model price–dividend along the path")
)
```

![Simulated long-run risk](figures/sim_xt.svg)

<p class="caption">One simulated monthly path of $$x_t$$.</p>

![Simulated market dividend growth](figures/sim_dd.svg)

<p class="caption">Market dividend growth along the same path. High $$x_t$$ raises $$\Delta d$$ by $$\phi=2.8$$.</p>

![Model price–dividend along the path](figures/sim_log_pd.svg)

<p class="caption">Model $$\log(P/D)$$ from $$z=\bar z+A_1 x+A_2(\sigma^2-\bar\sigma^2)$$. Valuations and risk premia have to match together.</p>

## Key takeaways

- The cash-flow model is built from data in two estimated steps: extract $$x_t$$ from consumption growth (a two-year MA, or a Kalman AR(1) — annual $$\rho\approx 0.43$$ either way), then regress dividend growth on it ($$\tilde\phi\approx 0.72$$). No return appears in either step.
- Simulated cash-flow moments have to look like the sample *before* you look at prices or premia. If they fail, stop; a later match on returns would be a free parameter in disguise.
- The discount-rate side is not re-tuned: the same Table II household prices the calibrated claim through the Euler equation.
- The equilibrium is graded on the pair — the equity premium *and* the mean valuation. Table II lands both for the market (7.53 vs 8.56 percent; log $$P/D$$ 3.24 vs 3.34), with the safe rate as the visible blemish.
- $$A_2$$ prices news about future economic uncertainty, alongside $$A_1$$ for the growth-rate component.

Value and growth are [The Cross Section]({{ '/cross-section.html' | relative_url }}). Matching the market does not rank firms.

## Exercises

1. Replace the two-year MA with `lrr.expected_growth_proxy(y, window=3)` and recompute $$\tilde\phi$$. Does the market's slope stay in the same ballpark?
2. Lower $$\rho$$ from 0.98 to 0.90 in the $$A_1$$ arithmetic for $$\phi=2.8$$. How much of the market's elasticity came from persistence?
3. Call `lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1)` and compare annual AC1 to the 1000-sample numbers in the text. How noisy is persistence in a 74-year sample?
