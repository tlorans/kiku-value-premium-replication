---
title: Time series
nav_order: 2
---

# Time series
{: .no_toc }

1. TOC
{:toc}

The time-series object is the market claim. I specify an Epstein–Zin investor and a consumption process with a small persistent component $$x_t$$, calibrate those laws to aggregate consumption and market dividends, and ask the Euler equation for the equity premium, the risk-free rate, market return volatility, and market $$\log(P/D)$$. Average market returns are not used to choose the parameters.

That is the usual test of a consumption-based model. Bansal and Yaron (2004) already showed that this investor can accommodate the time-series behavior of the aggregate equity market. I record the same check in Kiku (2006). It does not rank firms. The [cross section]({% link cross-section.md %}) is a different object.

## Preferences and the IMRS

Lifetime utility is Epstein and Zin (1989), Weil (1989):

$$
V_t=\left[(1-\delta)C_t^{\frac{1-\gamma}{\theta}}+\delta\left(\mathrm{E}_t[V_{t+1}^{1-\gamma}]\right)^{\frac{1}{\theta}}\right]^{\frac{\theta}{1-\gamma}},
\qquad
\theta=\frac{1-\gamma}{1-1/\psi}.
$$

The intertemporal marginal rate of substitution — equation (3) — is

$$
M_{t+1}=\delta^\theta (C_{t+1}/C_t)^{-\theta/\psi} R_{c,t+1}^{\theta-1},
$$

or in logs, equation (5),

$$
m_{t+1}=\theta\log\delta-\frac{\theta}{\psi}\Delta c_{t+1}+(\theta-1)r_{c,t+1}.
$$

When $$\gamma=1/\psi$$, $$\theta=1$$ and the wealth-return term drops: power utility. Then only contemporaneous consumption news is priced. With $$\gamma\neq 1/\psi$$, news that revises the outlook for wealth — including news in $$x_t$$ — is priced as well. Any asset satisfies $$\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1$$.

```python
from kiku_value_premium.model import get_table_ii_params, EpsteinZinPreferences
params = get_table_ii_params()
ez = EpsteinZinPreferences(params.prefs)
# Table II: δ=0.999, γ=10, ψ=1.5, so θ ≠ 1
```

## Aggregate cash flows

Consumption growth has a small persistent expected-growth component $$x_t$$ and a stochastic variance $$\sigma_t^2$$. Market dividends are levered consumption. Equation (6) restricted to the market claim:

$$
\begin{aligned}
\Delta c_{t+1}&=\mu_c+x_t+\sigma_t\eta_{t+1},\\
\Delta d_{t+1}&=\mu_m+\phi_m x_t+\varphi_m\sigma_t u_{t+1},\\
x_{t+1}&=\rho x_t+\varphi_x\sigma_t\epsilon_{t+1},\\
\sigma_{t+1}^2&=\sigma^2(1-\nu)+\nu\sigma_t^2+\sigma_w w_{t+1}.
\end{aligned}
$$

Table II: $$\phi_m=2.8$$, $$\mu_m=0.0012$$, $$\rho=0.98$$. The persistence of $$x_t$$ is what makes long-run news valuable. Under power utility $$\Lambda_\epsilon=0$$ and the same $$\phi_m$$ does not generate a large equity premium.

The price of long-run news, equations (13)–(14), is

$$
\Lambda_\epsilon=\left(\gamma-\frac{1}{\psi}\right)\frac{\kappa_{c,1}\varphi_x}{1-\kappa_{c,1}\rho}.
$$

With $$\gamma=10$$ and $$\psi=1.5$$, $$\Lambda_\epsilon\neq 0$$.

```python
from kiku_value_premium.model import get_table_ii_params, Dynamics
params = get_table_ii_params()
params.dividends["market"].phi  # 2.8
params.cons.rho                 # 0.98
```

## Calibration of the market

I choose preference and cash-flow parameters so that consumption and *market* dividend dynamics match the 1930–2003 sample. The equity premium is not a target.

Matched: mean and persistence of consumption growth, persistence of $$x_t$$, market dividend volatility, and the loading of market dividends on slow consumption. Not matched: mean market return, the Sharpe ratio, or the CAPM beta of the market.

|  |  | Meaning |
|:---|---:|:---|
| $$\delta$$ | 0.999 | time discount |
| $$\gamma$$ | 10 | relative risk aversion |
| $$\psi$$ | 1.5 | EIS |
| $$\mu_c$$ | 0.0015 | mean monthly consumption growth |
| $$\rho$$ | 0.98 | persistence of $$x_t$$ |
| $$\varphi_x$$ | 0.032 | scale of shocks to $$x$$ |
| $$\sigma$$ | 0.0064 | unconditional consumption volatility |

Market dividends: $$\mu=0.0012$$, $$\phi=2.8$$, $$\varphi_\sigma=7.5$$, $$\alpha=0.55$$.

Simulated consumption over 1000 samples of 74 years: mean growth 1.86 percent against 1.96 in the data; volatility 2.16 against 2.20; AC(1) 0.43 against 0.44. If those moments failed, the equity-premium prediction would not be to be trusted.

```python
from kiku_value_premium.calibration import simulate_cashflow_moments
from kiku_value_premium.model import get_table_ii_params
print(simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=get_table_ii_params()))
```

## Market moments

Cash-flow parameters locked, the Euler equation is asked for prices. Table VII, market row and the risk-free rate:

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

Market return volatility: 20.1 percent in the data and in the model. The same investor produces a risk-free rate that is too high by about seventy basis points and an equity premium that is a little short of the sample. That is the time-series record of the paper. It is close enough that the investor can be asked a second question.

```python
from kiku_value_premium.model import get_table_ii_params, ModelSolver, solve_analytical, print_value_premium
from kiku_value_premium.implications import compute_asset_pricing_moments, print_asset_pricing_moments

params = get_table_ii_params()
print_value_premium(solve_analytical(params))
solver = ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))
```

The printed market column is the time-series check. The value and growth columns on the same printout are not. They belong to the [cross section]({% link cross-section.md %}).

## What this object does not settle

Matching the market does not explain why two claims with market betas near one earn different average returns. Melin and Zhang (2026) keep this object and put climate into consumption: at $$3^{\circ}$$C the *market* equity premium is about twenty percent higher than in a no-climate counterfactual. That is still a time-series statement. It does not rank brown against green.

[The replica]({% link replica.md %}) keeps Sections 2–5 of the paper in her order.
