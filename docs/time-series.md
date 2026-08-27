---
title: Time series
nav_order: 2
---

# Time series
{: .no_toc }

1. TOC
{:toc}

**Question.** Can this household price the *market* — the value-weighted claim on all listed stocks — year after year?

**What is measured.** How consumption and *market* dividends grow. Not the average stock return.

**What is asked next.** The pricing equation (defined below) for four numbers: the extra return of stocks over a safe bond (the equity premium), the safe rate itself, how much the market return jumps around, and the average log price–dividend ratio. The price–dividend ratio is the price of the claim divided by this year’s dividend. We work with its log, $$\log(P/D)$$.

That is the test Bansal and Yaron (2004) wrote the model for. One claim. Not a ranking of firms.

## The household

The household has *recursive* preferences (Epstein and Zin 1989; Weil 1989). Risk aversion and the willingness to shift consumption across time are two different numbers.

- $$\delta$$ — how much the household discounts next month relative to this month.
- $$\gamma$$ — relative risk aversion. Larger means more dislike of wealth gambles.
- $$\psi$$ — elasticity of intertemporal substitution (EIS). Larger means more willingness to move consumption from today to tomorrow when the safe rate rises.

Lifetime value is

$$
V_t=\left[(1-\delta)C_t^{\frac{1-\gamma}{\theta}}+\delta\left(\mathrm{E}_t[V_{t+1}^{1-\gamma}]\right)^{\frac{1}{\theta}}\right]^{\frac{\theta}{1-\gamma}},
\qquad
\theta=\frac{1-\gamma}{1-1/\psi}.
$$

The *intertemporal marginal rate of substitution* (IMRS) is the discount factor that prices every asset. Call it $$M_{t+1}$$.

$$
M_{t+1}=\delta^\theta (C_{t+1}/C_t)^{-\theta/\psi} R_{c,t+1}^{\theta-1}.
$$

$$R_{c,t+1}$$ is the unobserved return on the claim to future consumption (wealth). In logs,

$$
m_{t+1}=\theta\log\delta-\frac{\theta}{\psi}\Delta c_{t+1}+(\theta-1)r_{c,t+1}.
$$

If $$\gamma=1/\psi$$, then $$\theta=1$$ and the wealth-return term drops. That case is *power utility*. Only this month’s consumption surprise is priced. If $$\gamma\neq 1/\psi$$, news that revises the outlook for wealth is priced too.

The *Euler equation* is the pricing equation. For any return $$R_{i,t+1}$$,

$$
\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1.
$$

That is the whole theory. Table II of Kiku (2006) uses $$\delta=0.999$$, $$\gamma=10$$, $$\psi=1.5$$, so $$\theta\neq 1$$.

```python
import lrrcs as lrr
params = lrr.get_table_ii_params()
ez = lrr.EpsteinZinPreferences(params.prefs)
```

## Cash flows of the market

Consumption growth is not white noise. It has a small persistent expected-growth piece $$x_t$$ and a variance that itself moves, $$\sigma_t^2$$. Market dividends are consumption with extra leverage on those shocks.

- $$\Delta c_{t+1}$$ — log consumption growth.
- $$\Delta d_{t+1}$$ — log dividend growth of the claim.
- $$\mu_c$$, $$\mu_m$$ — means of those two growth rates.
- $$\phi_m$$ — how many times more the market’s expected dividend growth moves with $$x_t$$ than consumption does. Call this *long-run leverage*.
- $$\rho$$ — how persistent $$x_t$$ is. Close to one means a shock to expected growth lasts for years.
- $$\varphi$$, $$\varphi_x$$, $$\sigma$$ — scales of the short-run shocks.

$$
\begin{aligned}
\Delta c_{t+1}&=\mu_c+x_t+\sigma_t\eta_{t+1},\\
\Delta d_{t+1}&=\mu_m+\phi_m x_t+\varphi_m\sigma_t u_{t+1},\\
x_{t+1}&=\rho x_t+\varphi_x\sigma_t\epsilon_{t+1},\\
\sigma_{t+1}^2&=\sigma^2(1-\nu)+\nu\sigma_t^2+\sigma_w w_{t+1}.
\end{aligned}
$$

Table II: $$\phi_m=2.8$$, $$\rho=0.98$$. Persistence is why $$x_t$$ is valuable. The *price of long-run news* — how much extra expected return you demand for a unit of exposure to the shock in $$x$$ — is

$$
\Lambda_\epsilon=\left(\gamma-\frac{1}{\psi}\right)\frac{\kappa_{c,1}\varphi_x}{1-\kappa_{c,1}\rho}.
$$

$$\kappa_{c,1}$$ is a linearization weight near one. Power utility sets $$\Lambda_\epsilon=0$$. Then $$\phi_m=2.8$$ does not produce an equity premium worth talking about. With $$\gamma=10$$ and $$\psi=1.5$$, $$\Lambda_\epsilon\neq 0$$.

```python
import lrrcs as lrr
params = lrr.get_table_ii_params()
params.dividends["market"].phi  # 2.8
params.cons.rho                 # 0.98
```

## The cash-flow test

**Question.** Do the consumption numbers look like 1930–2003 consumption?

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

Market dividends: $$\mu=0.0012$$, $$\phi=2.8$$, $$\varphi_\sigma=7.5$$, $$\alpha=0.55$$. The last two are short-run scale and the correlation of the dividend shock with the consumption shock.

**Result.** Simulated consumption, 1000 samples of 74 years: mean growth 1.86 percent against 1.96 in the data; volatility 2.16 against 2.20; first autocorrelation 0.43 against 0.44.

If those fail, stop. The premium that comes next would then be a free parameter in disguise.

```python
import lrrcs as lrr
print(lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=lrr.get_table_ii_params()))
```

## The pricing test

**Question.** Given those locked cash-flow numbers, what prices does the Euler equation assign to the market and the safe bond?

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

**How to read it.** E[R] is the average simple return, percent per year. E[pd] is average $$\log(P/D)$$. Numbers in parentheses are standard errors across simulated samples.

**Result.** Market return volatility is 20.1 percent in both. The safe rate is about seventy basis points too high. The equity premium is a little short of the sample. Close enough to ask a second question.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
lrr.print_long_short_premium(lrr.solve_analytical(params))
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
lrr.print_asset_pricing_moments(lrr.compute_asset_pricing_moments(solver))
```

The market column on that printout is this page. Value and growth are the [cross section]({{ '/cross-section.html' | relative_url }}).

## What this does not settle

Two firms can move one-for-one with the market and still earn different average returns. Matching the market does not explain that. Stop here and the ranking across firms is empty.

Melin and Zhang (2026) keep this object and put climate into consumption. At three degrees the *market* equity premium is about twenty percent higher than in a no-climate run. Still one claim. Still not a ranking of brown against green.
