---
title: Time series
nav_order: 2
---

# Time series
{: .no_toc }

1. TOC
{:toc}

The question this page asks is the usual one. Can the model price the market?

Equity premium, risk-free rate, volatility of returns and of $$\log(P/D)$$, predictability by the dividend yield. Those are the objects Bansal and Yaron (2004) and Bansal, Kiku, and Yaron (2012) were written to match. Cochrane (2017) puts long-run risks in a list with habits and disasters for that reason. One claim. Time-series moments. That is not a ranking of firms.

Average market returns do not choose the parameters. Consumption and market dividends do. Then the Euler equation is asked for prices.

## Preferences and the IMRS

Lifetime utility is Epstein and Zin (1989), Weil (1989):

$$
V_t=\left[(1-\delta)C_t^{\frac{1-\gamma}{\theta}}+\delta\left(\mathrm{E}_t[V_{t+1}^{1-\gamma}]\right)^{\frac{1}{\theta}}\right]^{\frac{\theta}{1-\gamma}},
\qquad
\theta=\frac{1-\gamma}{1-1/\psi}.
$$

The discount factor — equation (3) — is

$$
M_{t+1}=\delta^\theta (C_{t+1}/C_t)^{-\theta/\psi} R_{c,t+1}^{\theta-1}.
$$

In logs, equation (5),

$$
m_{t+1}=\theta\log\delta-\frac{\theta}{\psi}\Delta c_{t+1}+(\theta-1)r_{c,t+1}.
$$

If $$\gamma=1/\psi$$, $$\theta=1$$. The wealth-return term drops. That is power utility. Only today’s consumption news is priced. If $$\gamma\neq 1/\psi$$, news that revises the outlook for wealth is priced too — including news in $$x_t$$. Every asset satisfies $$\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1$$. That is the whole theory.

```python
from kiku_value_premium.model import get_table_ii_params, EpsteinZinPreferences
params = get_table_ii_params()
ez = EpsteinZinPreferences(params.prefs)
# Table II: δ=0.999, γ=10, ψ=1.5, so θ ≠ 1
```

## Aggregate cash flows

Consumption growth is not white noise. It has a small persistent expected-growth piece $$x_t$$ and a stochastic variance. Market dividends are levered consumption.

$$
\begin{aligned}
\Delta c_{t+1}&=\mu_c+x_t+\sigma_t\eta_{t+1},\\
\Delta d_{t+1}&=\mu_m+\phi_m x_t+\varphi_m\sigma_t u_{t+1},\\
x_{t+1}&=\rho x_t+\varphi_x\sigma_t\epsilon_{t+1},\\
\sigma_{t+1}^2&=\sigma^2(1-\nu)+\nu\sigma_t^2+\sigma_w w_{t+1}.
\end{aligned}
$$

Table II: $$\phi_m=2.8$$, $$\rho=0.98$$. Persistence is the whole point. The price of long-run news is

$$
\Lambda_\epsilon=\left(\gamma-\frac{1}{\psi}\right)\frac{\kappa_{c,1}\varphi_x}{1-\kappa_{c,1}\rho}.
$$

Power utility sets $$\Lambda_\epsilon=0$$. Then $$\phi_m=2.8$$ does not produce an equity premium worth talking about. With $$\gamma=10$$ and $$\psi=1.5$$, $$\Lambda_\epsilon\neq 0$$.

```python
from kiku_value_premium.model import get_table_ii_params, Dynamics
params = get_table_ii_params()
params.dividends["market"].phi  # 2.8
params.cons.rho                 # 0.98
```

## Calibration of the market

Match consumption and *market* dividends, 1930–2003. Do not match the equity premium.

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

Simulated consumption, 1000 samples of 74 years: mean growth 1.86 percent against 1.96 in the data; volatility 2.16 against 2.20; AC(1) 0.43 against 0.44. If those fail, stop. The premium prediction is then a free parameter in disguise.

```python
from kiku_value_premium.calibration import simulate_cashflow_moments
from kiku_value_premium.model import get_table_ii_params
print(simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=get_table_ii_params()))
```

## Market moments

Parameters locked. Ask the Euler equation.

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

Market return volatility: 20.1 percent in both. The risk-free rate is about seventy basis points too high. The equity premium is a little short. That is the time-series record. Close enough to ask a second question.

```python
from kiku_value_premium.model import get_table_ii_params, ModelSolver, solve_analytical, print_value_premium
from kiku_value_premium.implications import compute_asset_pricing_moments, print_asset_pricing_moments

params = get_table_ii_params()
print_value_premium(solve_analytical(params))
solver = ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))
```

The market column on that printout is this page. Value and growth are not. They are the [cross section]({{ '/cross-section.html' | relative_url }}).

## What this does not settle

Two claims can have market betas near one and different average returns. Matching the market does not explain that. Stop here and the cross-sectional column is empty.

Melin and Zhang (2026) keep this object and put climate into consumption. At $$3^{\circ}$$C the *market* equity premium is about twenty percent higher than in a no-climate counterfactual. Still one claim. Still not a ranking of brown against green.
