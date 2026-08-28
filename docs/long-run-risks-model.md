---
title: The long-run risks model
nav_order: 4
---

# The long-run risks model
{: .no_toc }

1. TOC
{:toc}

Here is the model. It has exactly two parts, and they are the two halves of every DCF you have ever built. A consumption process with a slow-moving component tells us where cash-flow growth comes from. An investor who fears news about that component tells us where the discount rate comes from. The chapter ends at the one expression where the halves meet, and with the model's answer to the security market line, drawn before we touch a single return.

Why go to this trouble? Because "the market went down, the discount rate must have risen" is not economics, it is poetry. A model earns the name only if the thing driving it can be measured and its predictions can fail. The driver here is expected consumption growth; the predictions are prices *and* risk premia. [The Time Series]({{ '/time-series.html' | relative_url }}) and [The Cross Section]({{ '/cross-section.html' | relative_url }}) run those tests. This chapter only builds the machine.

We use the following packages. Run the chunks **in order** — later snippets reuse `paths` and `sol`.

```python
import numpy as np
import pandas as pd
import polars as pl
import plotnine as p9
import lrrcs as lrr
```

## The consumption process

[Financial data]({{ '/financial-data.html' | relative_url }}) delivered 74 years of consumption growth, and that series has a property worth staring at: its first autocorrelation is about 0.41 — this year's growth carries real information about next year's. That matters more than it looks. The equity-premium puzzle of Mehra and Prescott is usually stated for an economy where growth is i.i.d. — independent and identically distributed, coin-flip growth with no memory — and where, under standard preferences, the model's premium comes out near zero. Bansal and Yaron (2004) change the consumption process, not the arithmetic: split growth into a small persistent piece $$x_t$$ and a transitory shock,

$$
\Delta c_{t+1}=\mu+x_t+\sigma_t\eta_{t+1},\qquad
x_{t+1}=\rho x_t+\varphi_x\sigma_t e_{t+1}.
$$

In words: this period's growth is a constant, plus where expected growth currently stands, plus noise — and expected growth itself drifts slowly, decaying at rate $$\rho$$. A shock to $$x_t$$ is not news about this year; it is news about the next *decade* of consumption. That is the risk the model is named for: long-run risk. Kiku's Table II uses monthly $$\rho=0.98$$, which means a piece of news about $$x_t$$ still retains half its force three years later. The volatility $$\sigma_t$$ drifts too — uncertainty itself rises and falls — and that will matter, but $$x_t$$ carries this chapter.

Is such a component even visible? Barely — that is both the point and the standing objection to the whole enterprise. $$x_t$$ is a few tenths of a percent per month, easily buried under the transitory shocks. Look at what it does to the *level* of consumption anyway. Simulate two paths with the very same short-run shocks: one i.i.d., one with $$x_t$$.

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

<p class="caption">Gray: i.i.d. growth. Blue: the same short-run shocks plus the slow component. The extra low-frequency swing is long-run risk.</p>

```python
(
    p9.ggplot(paths, p9.aes("t", "x"))
    + p9.geom_line()
    + p9.labs(x="Month", y="x_t", title="The expected-growth state")
)
```

![The expected-growth state](figures/lrr_state.svg)

<p class="caption">$$x_t$$ is small — a few tenths of a percent per month — and very slow to die out. Small news, long shadow.</p>

For the DCF reader: $$x_t$$ *is* your $$g$$ — not a constant plugged into a terminal value, but a condition of the economy that wanders, and that dividends inherit. Extracting it from seventy-four years of annual data is the business of [The Time Series]({{ '/time-series.html' | relative_url }}).

## The household

Now the discount rate — which means, now the investor. Prices come from her willingness to trade consumption today against consumption in some future state, so we need her *marginal utility*: how much an extra dollar is worth to her, in each state. An asset that pays off in states where the extra dollar is precious is valuable and can charge a low expected return; an asset that pays off when she is already comfortable must offer a premium. All of asset pricing is bookkeeping around that sentence.

Under the standard textbook preferences — power utility — one parameter does two jobs: risk aversion $$\gamma$$ (distaste for uncertainty across states) and the elasticity of intertemporal substitution $$\psi$$ (willingness to reschedule consumption over time) are forced to be reciprocals of each other, $$\gamma=1/\psi$$. An investor who hates risk is thereby forced to also hate consumption *growth*, which is absurd — and quantitatively fatal, because persistent good news about growth would then crush stock prices through a soaring interest rate. Epstein and Zin (1989) and Weil (1989) cut the knot. Their marginal rate of substitution — the exchange rate at which the investor trades consumption tomorrow for consumption today, the object usually written $$M_{t+1}$$ — is

$$
M_{t+1}=\delta^\theta (C_{t+1}/C_t)^{-\theta/\psi} R_{c,t+1}^{\theta-1},
\qquad
\theta=\frac{1-\gamma}{1-1/\psi}.
$$

Read it in English: marginal utility falls with consumption growth, as always — but it also moves with $$R_{c,t+1}$$, the return on a claim to *all future consumption*, the wealth portfolio. That return is forward-looking by construction: it drops on bad news about the future even if today's consumption is untouched. Table II sets $$\delta=0.999$$, $$\gamma=10$$, $$\psi=1.5$$.

```python
delta, gamma, psi = 0.999, 10.0, 1.5
theta = (1.0 - gamma) / (1.0 - 1.0 / psi)
gamma, 1.0 / psi, theta
```

```text
(10.0, 0.667, -27.0)
```

$$\theta = -27$$, not 1. That is the whole trick. With $$\gamma > 1/\psi$$, the wealth-return term is alive, and the investor dreads assets that fall *when there is bad news about long-run consumption growth*, not merely when this year's consumption dips. Under power utility $$\theta=1$$, the wealth term vanishes, only next period's consumption enters marginal utility — and next period's consumption barely moves, so no amount of persistence in $$x_t$$ produces a premium worth mentioning.

The entire pricing theory is then one line, the Euler equation:

$$
\mathrm{E}_t\left[M_{t+1}R_{i,t+1}\right]=1.
$$

In English: for every claim $$i$$, the expected product of the return and the investor's exchange rate must equal one — otherwise she would want to buy more or less of it, and prices would move until she doesn't. Feed it cash flows and it hands back prices and risk premia together.

## The security market line

The cash-flow model for an individual claim is one equation:

$$
\Delta d_{t+1}=\mu_d+\phi x_t+\varphi_\sigma\sigma_t u_{t+1}.
$$

Dividend growth inherits expected consumption growth, magnified by the leverage $$\phi$$ we met in the last chapter, plus its own noise. $$\phi$$ is where firms differ: it measures how much slow-moving, long-run consumption risk is built into a firm's cash flows. It is the model's answer to a question the CAPM answers differently. The CAPM — the workhorse model of discount rates — says a claim's risk premium is proportional to its *beta*, the slope of a regression of its return on the market's return. Here the premium is earned by a property of *dividends*, measurable without ever looking at a return.

Approximate the model around its average — log-linearize, in the jargon — and the log price–dividend ratio becomes a straight-line function of the state, $$z_t=\bar z+A_1 x_t+\cdots$$, with slope

$$
A_1=\frac{\phi-1/\psi}{1-\kappa_1\rho}.
$$

Stop and look at this expression, because it is where the two halves of the model — and the two halves of your DCF — meet in a single fraction. $$\phi$$ is the cash-flow model: how hard dividends lever long-run news. $$1/\psi$$ is the investor: how hard the interest rate pushes back when expected growth rises. $$\rho$$ is the persistence of the news, and $$\kappa_1\approx 0.96$$ is a constant thrown off by the approximation, close to one because dividends far in the future still carry weight. Good news about $$x_t$$ raises expected cash flows (the $$\phi$$ term — your $$g$$) and raises the discount rate a little (the $$1/\psi$$ term — your $$r$$); with $$\phi>1/\psi$$ and $$\rho$$ near one, the cash-flow effect wins by a wide margin and the price responds strongly. In a DCF, $$r$$ and $$g$$ never talk to each other. Here they are two terms of the same numerator.

The long-run risk premium is then $$A_1$$ times the price of long-run news. So the model draws its own security market line — the CAPM's famous straight line of premium against beta, except the horizontal axis is now cash-flow leverage $$\phi$$. Draw it, then place Table II's three claims on it.

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

<p class="caption">The model's security market line. The horizontal axis is the exposure of dividends to long-run consumption news, not CAPM $$\beta$$. Value sits far to the right; growth does not.</p>

```text
A1 growth 43.1, market 37.5, value 88.9
Lambda_eps  5.95
```

Value's $$A_1$$ is about twice growth's. The same cash-flow leverage that earns value a high premium makes its price more fragile: its price–dividend ratio swings harder on long-run news, so the claim must offer high expected compensation up front. Notice what this is *not*: a prediction that value has a larger CAPM beta. Often it does not — market betas mostly pick up transitory price wiggles, not the permanent cash-flow risk that carries the big reward here.

`lrr.solve_analytical` is this linearization for every claim in `ModelParams`. The points on the figure come from Table II: $$\phi_G=2.6$$, $$\phi_m=2.8$$, $$\phi_V=6.2$$.

One rule, and it is the book's discipline: do **not** estimate $$\phi$$ from returns. $$\phi$$ is a cash-flow exposure, measured from dividends and consumption. Average returns, Sharpe ratios (return per unit of volatility), and CAPM betas stay out of that step, so that the Euler equation remains a *test*: given those cash-flow numbers, do prices and premia look like the data? [The Time Series]({{ '/time-series.html' | relative_url }}) runs the test on the market. [The Cross Section]({{ '/cross-section.html' | relative_url }}) runs it on value and growth.

## Key takeaways

- The consumption process is where growth comes from: a small, slow-dying component $$x_t$$ under the noise, plus drifting uncertainty. $$x_t$$ is the DCF's $$g$$, made a measurable condition of the economy.
- The Epstein–Zin investor is where the discount rate comes from: with risk aversion above $$1/\psi$$, her marginal utility responds to the return on total wealth, so the risk she fears most is bad news about the *long run*.
- The halves meet in $$A_1=(\phi-1/\psi)/(1-\kappa_1\rho)$$: cash-flow leverage and the investor's interest-rate response in one fraction. Because the news is persistent, small shocks move prices a lot.
- Firms differ only in how much long-run consumption risk their dividends carry. That dispersion — not return covariances — is what the model turns into prices and premia.
- $$\phi$$ is estimated from cash flows. Returns are the test.

## Exercises

1. Set $$\psi=1/\gamma=0.1$$ so that $$\theta=1$$. Recompute the premium-versus-$$\phi$$ line. What happens to the slope?
2. Lower $$\rho$$ from 0.98 to 0.90 and recompute $$A_1$$ for $$\phi=6.2$$. How much of the value claim's price sensitivity came from persistence?
3. Set $$\varphi_x=0$$ (no long-run risk in consumption) and recompute the premium-versus-$$\phi$$ line. Where did the slope go?
