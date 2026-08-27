---
title: 3. The Long-Run Risks Model
parent: The replica
nav_order: 2
---

# 3. The Long-Run Risks Model
{: .no_toc }

1. TOC
{:toc}

I specify preferences, consumption, and the three dividend claims, and I state the Euler equation that determines prices. The six-percent premium is still not an input.

An Epstein–Zin investor prices news about the persistent expected-growth factor $$x_t$$. Dividend claims differ by their loading $$\phi$$ on that factor. Value’s larger $$\phi$$ raises its risk premium and lowers its price–dividend ratio. Under power utility the price of long-run news is zero, and a gap in $$\phi$$ does not generate a large premium.

[Section 2]({% link empirical.md %}) established that value cash flows load more on slow consumption. That is not yet a risk premium. This section is the mapping from a cash-flow loading to a required return.

## 3.1 Preferences

Lifetime utility is Epstein and Zin (1989), Weil (1989):

$$
V_t=\left[(1-\delta)C_t^{\frac{1-\gamma}{\theta}}+\delta\left(\mathrm{E}_t[V_{t+1}^{1-\gamma}]\right)^{\frac{1}{\theta}}\right]^{\frac{\theta}{1-\gamma}},
\qquad
\theta=\frac{1-\gamma}{1-1/\psi}.
$$

Wealth tomorrow is what is not consumed, grown at the return on the wealth portfolio: $$W_{t+1}=(W_t-C_t)R_{c,t+1}$$. The intertemporal marginal rate of substitution — equation (3) — is

$$
M_{t+1}=\delta^\theta (C_{t+1}/C_t)^{-\theta/\psi} R_{c,t+1}^{\theta-1},
$$

or in logs, equation (5),

$$
m_{t+1}=\theta\log\delta-\frac{\theta}{\psi}\Delta c_{t+1}+(\theta-1)r_{c,t+1}.
$$

When $$\gamma=1/\psi$$, $$\theta=1$$ and the wealth-return term drops: power utility. Then only contemporaneous consumption news is priced. With $$\gamma\neq 1/\psi$$, news that revises the outlook for wealth — including news in $$x_t$$ — is priced as well.

Any asset satisfies $$\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1$$. That is the entire pricing theory of the paper.

```python
import lrrcs as lrr
params = lrr.get_table_ii_params()
ez = lrr.EpsteinZinPreferences(params.prefs)
# Table II: δ=0.999, γ=10, ψ=1.5, so θ ≠ 1
```

## 3.2 Cash-flow dynamics

Consumption growth has a small persistent expected-growth component $$x_t$$ and a stochastic variance $$\sigma_t^2$$. Dividend growth of each claim loads on $$x_t$$ with its own leverage $$\phi$$. Equation (6):

$$
\begin{aligned}
\Delta c_{t+1}&=\mu_c+x_t+\sigma_t\eta_{t+1},\\
\Delta d_{t+1}&=\mu+\phi x_t+\varphi\sigma_t u_{t+1},\\
x_{t+1}&=\rho x_t+\varphi_x\sigma_t\epsilon_{t+1},\\
\sigma_{t+1}^2&=\sigma^2(1-\nu)+\nu\sigma_t^2+\sigma_w w_{t+1}.
\end{aligned}
$$

$$\phi$$ scales how hard a shift in the outlook hits this asset’s dividends. Value and growth are the same machine except for $$(\mu,\phi,\varphi,\alpha)$$. Table II: $$\phi_{\text{value}}=6.2$$, $$\phi_{\text{growth}}=2.6$$, $$\phi_{\text{market}}=2.8$$. The short-run correlation $$\alpha=\mathrm{Corr}(\eta,u)$$ is a different risk.

I give value a larger $$\phi$$ because Section 2 found a larger annual $$\tilde\phi$$, not because value had a larger average return.

```python
import lrrcs as lrr
params = lrr.get_table_ii_params()
params.dividends["value"].phi   # 6.2
params.dividends["growth"].phi  # 2.6
path = lrr.Dynamics(params, seed=42).simulate_cashflows(T=12 * 74)
```

## 3.3 Numerical solution

Cash-flow laws are given. The unknowns are the price–consumption and price–dividend ratios as functions of $$(x,\sigma^2)$$. I replace the continuous state by a discrete Markov chain (Tauchen and Hussey 1991): 30 Gauss–Hermite nodes on $$x$$, four points on $$\sigma^2$$. At each grid point the Euler equation must hold. The short-run innovation $$\eta$$ is integrated with a 7-point Gauss–Hermite rule inside every Euler evaluation.

```python
import lrrcs as lrr
solver = lrr.ModelSolver(lrr.get_table_ii_params(), n_x=30, n_s=4, n_quad=7)
solver.solve()
# solver.z["value"] is log(P/D) on the grid
```

`examples/run_paper.py` uses $$n_x=15$$ so a laptop finishes. Install `[fast]` for Numba on the Euler loops.

## 3.4 Approximate analytical solution

Log $$P/C$$ is approximately linear in the states, equation (7):

$$
z_{c,t}=A_{c,0}+A_{c,1}x_t+A_{c,2}\sigma_t^2.
$$

Matching coefficients in the log Euler equation gives, equations (10)–(11),

$$
A_{c,1}=\frac{1-1/\psi}{1-\kappa_{c,1}\rho},\qquad
A_1=\frac{\phi-1/\psi}{1-\kappa_1\rho}.
$$

$$A_{c,1}>0$$ when $$\psi>1$$: good news about future growth raises the price of the consumption claim (substitution dominates). The closer $$\rho$$ is to one, the more a blip in $$x$$ looks permanent, so the price reaction is larger. For a dividend claim the same news is multiplied by $$\phi$$. Value ($$\phi=6.2$$) therefore has a much larger elasticity to $$x_t$$ than growth.

The IMRS innovation, equations (13)–(14), prices three shocks. Short-run consumption news has price $$\Lambda_\eta=\gamma$$. Long-run news has price

$$
\Lambda_\epsilon=\left(\gamma-\frac{1}{\psi}\right)\frac{\kappa_{c,1}\varphi_x}{1-\kappa_{c,1}\rho}.
$$

With Table II ($$\gamma=10$$, $$\psi=1.5$$), $$\Lambda_\epsilon\neq 0$$. Under power utility it is zero.

Two consequences follow from the same gap in $$\phi$$. Value’s dividends fall harder when the outlook turns bad, which is when $$M_{t+1}$$ is high, so the Euler equation requires a higher average return. The investor pays less today per unit of current dividend, so value’s price–dividend ratio is lower.

```python
import lrrcs as lrr
lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

`solve_analytical` is this linearization. It already ranks value’s long-run premium above growth’s. Campbell–Shiller points for $$\log(P/D)$$: 3.65 (growth), 3.10 (value), 3.24 (market). The 5.3 percent in Table VII comes from the numerical solver after the cash-flow parameters are locked.

[Section 4]({% link calibration.md %}) chooses those parameters.
