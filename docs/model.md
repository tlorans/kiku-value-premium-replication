---
title: The Long-Run Risks Model
nav_order: 4
---

# The Long-Run Risks Model
{: .no_toc }

Kiku’s Section 3. She adopts Bansal and Yaron (2004). Two ingredients matter equally: a small persistent component in cash-flow growth, and Epstein–Zin preferences that break the link between risk aversion and the IES.

1. TOC
{:toc}

## 3.1 Epstein–Zin preferences

Lifetime utility is recursive:

$$
V_t=\left[(1-\delta)C_t^{\frac{1-\gamma}{\theta}}+\delta\left(\mathrm{E}_t[V_{t+1}^{1-\gamma}]\right)^{\frac{1}{\theta}}\right]^{\frac{\theta}{1-\gamma}},
\qquad
\theta=\frac{1-\gamma}{1-1/\psi}.
$$

Budget constraint: $W_{t+1}=(W_t-C_t)R_{c,t+1}$. The IMRS is her (3),

$$
M_{t+1}=\delta^\theta (C_{t+1}/C_t)^{-\theta/\psi} R_{c,t+1}^{\theta-1},
$$

or in logs, her (5),

$$
m_{t+1}=\theta\log\delta-\frac{\theta}{\psi}\Delta c_{t+1}+(\theta-1)r_{c,t+1}.
$$

{: .paper }
When $\gamma=1/\psi$, $\theta=1$ and the wealth-return term drops: power utility. With $\gamma\neq 1/\psi$, “good” and “bad” times depend not only on today’s consumption but on future investment and growth opportunities inside $r_{c,t+1}$.

Euler equation for any return: $\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1$.

```python
from kiku_value_premium.model import get_table_ii_params, EpsteinZinPreferences
params = get_table_ii_params()
ez = EpsteinZinPreferences(params.prefs)
# Table II: δ=0.999, γ=10, ψ=1.5
```

## 3.2 Cash-flow growth rates

Predictable variation in growth is an AR(1) $x_t$; variation in second moments is a common variance $\sigma_t^2$. Her (6):

$$
\begin{aligned}
\Delta c_{t+1}&=\mu_c+x_t+\sigma_t\eta_{t+1},\\
\Delta d_{t+1}&=\mu+\phi x_t+\varphi\sigma_t u_{t+1},\\
x_{t+1}&=\rho x_t+\varphi_x\sigma_t\epsilon_{t+1},\\
\sigma_{t+1}^2&=\sigma^2(1-\nu)+\nu\sigma_t^2+\sigma_w w_{t+1}.
\end{aligned}
$$

Shocks are Gaussian. $\alpha=\mathrm{Corr}(\eta_t,u_t)$ is the only allowed contemporaneous correlation. $\phi$ is long-run leverage on expected consumption growth — the cross-sectional object that will produce the value premium. $\varphi$ loads dividends on volatility and short-run consumption news.

Table II (monthly): $\rho=0.98$, $\phi_{\text{value}}=6.2$, $\phi_{\text{growth}}=2.6$, $\phi_{\text{market}}=2.8$.

```python
from kiku_value_premium.model import get_table_ii_params, Dynamics
params = get_table_ii_params()
params.dividends["value"].phi   # 6.2
params.dividends["growth"].phi  # 2.6
dyn = Dynamics(params, seed=42)
path = dyn.simulate_cashflows(T=12 * 74)
```

## 3.3 Solving for equilibrium prices

Growth rates are exogenous. Price/consumption and price/dividend ratios are enough. She discretizes $(x,\sigma^2)$ with Tauchen and Hussey (1991): 30-point Gauss–Hermite on $x$, 4-point on $\sigma^2$. Euler equations are solved on that chain. The package adds a 7-point Gauss–Hermite integral over the short-run innovation $\eta$ inside every Euler evaluation.

```python
from kiku_value_premium.model import ModelSolver, get_table_ii_params
solver = ModelSolver(get_table_ii_params(), n_x=30, n_s=4, n_quad=7)
solver.solve()
# solver.z_c, solver.z["value"], solver.z["growth"], solver.stationary
```

Install `[fast]` for Numba kernels. `examples/run_paper.py` uses $n_x=15$ so it finishes.

## 3.4 Model intuition

Log $P/C$ is approximately linear in the states, her (7):

$$
z_{c,t}=A_{c,0}+A_{c,1}x_t+A_{c,2}\sigma_t^2.
$$

Campbell–Shiller wealth return (8) plus the log Euler equation (9) give, her (10)–(11),

$$
A_{c,1}=\frac{1-1/\psi}{1-\kappa_{c,1}\rho},\qquad
A_1=\frac{\phi-1/\psi}{1-\kappa_1\rho}.
$$

{: .paper }
$A_{c,1}>0$ when $\psi>1$: substitution dominates, and good news about future growth raises the price of the consumption claim. The effect is larger the closer $\rho$ is to one. For a dividend claim the same news is scaled by leverage $\phi$. That is why value, with $\phi=6.2$, has a much larger elasticity to $x_t$ than growth.

Innovations in the IMRS, her (13)–(14):

$$
m_{t+1}-\mathrm{E}_t[m_{t+1}]=-\Lambda_\eta\sigma_t\eta_{t+1}-\Lambda_\epsilon\sigma_t\epsilon_{t+1}-\Lambda_w\sigma_w w_{t+1},
$$

with $\Lambda_\eta=\gamma$ (short-run consumption news) and

$$
\Lambda_\epsilon=\left(\gamma-\frac{1}{\psi}\right)\frac{\kappa_{c,1}\varphi_x}{1-\kappa_{c,1}\rho}
$$

the price of long-run expected-growth news. With $\gamma=10$ and $\psi=1.5$, long-run news is priced; with power utility it is not.

```python
from kiku_value_premium.model import solve_analytical, print_value_premium, get_table_ii_params
print_value_premium(solve_analytical(get_table_ii_params()))
```

`solve_analytical` ranks the long-run risk premium value > growth and uses linearization points $\log(P/D)$ of 3.65 / 3.10 / 3.24 (growth / value / market).

Next: [Calibration]({% link calibration.md %}).
