---
title: The Long-Run Risks Model
nav_order: 4
---

# The Long-Run Risks Model
{: .no_toc }

{: .here }
Section 2 showed the facts. This page is the economic machine: investors, consumption, dividends, and a fair-price rule. We still do not put the 6 percent premium into the machine.

**In a nutshell.** We write down investors who care about the long run, consumption that has a slow-moving outlook $$x_t$$, and three dividend claims that load differently on that outlook. Prices then drop out of Euler equations.

{: .idea }
Weather versus climate. A rainy Tuesday is a short-run shock: consumption is a bit lower this month. A multi-year shift in the growth outlook is climate: $$x_t$$. Value and growth are two farms. Value’s harvest (its dividends) depends more on the climate. If you hate droughts more than rainy Tuesdays, you will only hold the climate-sensitive farm if it pays you more — and you will pay less for it today per dollar of current harvest.

{: .why }
Section 2 showed that value *looks* more exposed to slow consumption. That is a cash-flow fact. It is not yet a risk premium. This page is what turns “more exposed” into “must pay a higher return and sell at a lower P/D.” Skip the preferences and a higher $$\phi$$ is just a description of dividends.

1. TOC
{:toc}

## Four ingredients (then the formulas)

1. **Preferences.** How painful is a bad future? Epstein–Zin, so dislike of risk is not glued to impatience.
2. **Consumption.** Growth has a small persistent piece $$x_t$$ (the climate) and a volatility that can wander.
3. **Dividends.** Each portfolio is the same machine except for how hard $$x_t$$ hits it ($$\phi$$) and a few short-run numbers.
4. **A fair-price rule.** You should not want to buy or sell a little more of any asset already priced: $$\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1$$.

The rest of the page is those four, in order.

## 3.1 Why Epstein–Zin, not power utility

{: .idea }
Imagine two knobs. One is “how much I hate a bumpy ride” (risk aversion $$\gamma$$). The other is “how willing I am to wait until next year to consume” (the IES $$\psi$$). Power utility welds the knobs together: if you hate risk you also refuse to wait, and the risk-free rate explodes. Epstein–Zin unscrews them. Empirically we need both a high equity premium (high $$\gamma$$) and a low, stable risk-free rate ($$\psi$$ not tiny).

Lifetime utility is recursive:

$$
V_t=\left[(1-\delta)C_t^{\frac{1-\gamma}{\theta}}+\delta\left(\mathrm{E}_t[V_{t+1}^{1-\gamma}]\right)^{\frac{1}{\theta}}\right]^{\frac{\theta}{1-\gamma}},
\qquad
\theta=\frac{1-\gamma}{1-1/\psi}.
$$

Wealth tomorrow is what you did not consume, grown at the return on the wealth portfolio: $$W_{t+1}=(W_t-C_t)R_{c,t+1}$$. The stochastic discount factor — the “how painful is a dollar in that future?” object, her (3) — is

$$
M_{t+1}=\delta^\theta (C_{t+1}/C_t)^{-\theta/\psi} R_{c,t+1}^{\theta-1},
$$

or in logs, her (5),

$$
m_{t+1}=\theta\log\delta-\frac{\theta}{\psi}\Delta c_{t+1}+(\theta-1)r_{c,t+1}.
$$

{: .paper }
When $$\gamma=1/\psi$$, $$\theta=1$$ and the wealth-return term drops: power utility. Then only this month’s consumption news is priced. With $$\gamma\neq 1/\psi$$, news that changes the *outlook* for wealth (including $$x_t$$) is priced too. That is why climate risk can command a premium that rainy-Tuesday risk cannot.

Any asset must satisfy $$\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1$$. That is the whole pricing theory on this page: today’s price is the one at which you are indifferent to holding a little more or a little less.

```python
from kiku_value_premium.model import get_table_ii_params, EpsteinZinPreferences
params = get_table_ii_params()
ez = EpsteinZinPreferences(params.prefs)
# Table II: δ=0.999, γ=10, ψ=1.5  so θ ≠ 1
```

## 3.2 Cash flows: the persistent piece and leverage $$\phi$$

Consumption growth is “usual 2 percent, plus a weather shock this month, plus a small change in the climate.” The climate is $$x_t$$: tiny, highly persistent ($$\rho=0.98$$). Variance $$\sigma_t^2$$ can also wander. Her (6):

$$
\begin{aligned}
\Delta c_{t+1}&=\mu_c+x_t+\sigma_t\eta_{t+1},\\
\Delta d_{t+1}&=\mu+\phi x_t+\varphi\sigma_t u_{t+1},\\
x_{t+1}&=\rho x_t+\varphi_x\sigma_t\epsilon_{t+1},\\
\sigma_{t+1}^2&=\sigma^2(1-\nu)+\nu\sigma_t^2+\sigma_w w_{t+1}.
\end{aligned}
$$

$$\phi$$ scales how hard a shift in the outlook hits *this asset’s* dividends. If $$x_t$$ ticks up 0.1 percent, value dividends tick up 0.62 percent and growth only 0.26 percent. That is leverage on the climate, not debt.

Value and growth are the same machine except for $$(\mu,\phi,\varphi,\alpha)$$. Table II: $$\phi_{\text{value}}=6.2$$, $$\phi_{\text{growth}}=2.6$$, $$\phi_{\text{market}}=2.8$$. $$\alpha=\mathrm{Corr}(\eta,u)$$ is short-run comovement with consumption, a different risk.

{: .why }
We give value a larger $$\phi$$ because Section 2 found a larger annual $$\tilde\phi$$, not because value had a larger average return. That distinction is the whole paper.

```python
from kiku_value_premium.model import get_table_ii_params, Dynamics
params = get_table_ii_params()
params.dividends["value"].phi   # 6.2
params.dividends["growth"].phi  # 2.6
path = Dynamics(params, seed=42).simulate_cashflows(T=12 * 74)
```

## 3.3 Solving for prices

Cash-flow laws are given. The unknowns are price–consumption and price–dividend ratios as functions of $$(x,\sigma^2)$$. Computers cannot store a continuous climate, so she replaces the states by a discrete Markov chain (Tauchen and Hussey 1991): 30 points on $$x$$, 4 on $$\sigma^2$$. At each grid point the Euler equation must hold. The package also integrates the short-run shock $$\eta$$ with 7-point Gauss–Hermite quadrature inside every Euler evaluation.

```python
from kiku_value_premium.model import ModelSolver, get_table_ii_params
solver = ModelSolver(get_table_ii_params(), n_x=30, n_s=4, n_quad=7)
solver.solve()
# solver.z["value"] is log(P/D) on the grid
```

`examples/run_paper.py` uses $$n_x=15$$ so a laptop finishes. Install `[fast]` for Numba.

## 3.4 Why a larger $$\phi$$ raises the premium and cuts P/D

Log $$P/C$$ is approximately linear in the states, her (7):

$$
z_{c,t}=A_{c,0}+A_{c,1}x_t+A_{c,2}\sigma_t^2.
$$

Matching coefficients in the log Euler equation gives, her (10)–(11),

$$
A_{c,1}=\frac{1-1/\psi}{1-\kappa_{c,1}\rho},\qquad
A_1=\frac{\phi-1/\psi}{1-\kappa_1\rho}.
$$

{: .paper }
$$A_{c,1}>0$$ when $$\psi>1$$: good news about future growth raises the price of the consumption claim (substitution dominates). The closer $$\rho$$ is to one, the more a blip in $$x$$ looks permanent, so the price reaction is larger. For a dividend claim the same news is multiplied by $$\phi$$. Value ($$\phi=6.2$$) therefore has a much larger elasticity to $$x_t$$ than growth.

The IMRS innovation, her (13)–(14), prices three shocks. Short-run consumption news has price $$\Lambda_\eta=\gamma$$. Long-run news has price

$$
\Lambda_\epsilon=\left(\gamma-\frac{1}{\psi}\right)\frac{\kappa_{c,1}\varphi_x}{1-\kappa_{c,1}\rho}.
$$

With Table II ($$\gamma=10$$, $$\psi=1.5$$), $$\Lambda_\epsilon\neq 0$$. Under power utility it is zero, and differential $$\phi$$ would not generate a large premium.

Two consequences, same $$\phi$$ gap:

- **Higher expected return.** Value’s dividends fall harder when the climate turns bad, which is exactly when a dollar is more painful ($$M$$ is high). The only way $$\mathrm{E}[MR]=1$$ still holds is if average $$R$$ is higher.
- **Lower P/D today.** You pay less now per dollar of current dividend, because more of the future harvest is climate-risk.

```python
from kiku_value_premium.model import solve_analytical, print_value_premium, get_table_ii_params
print_value_premium(solve_analytical(get_table_ii_params()))
```

`solve_analytical` is this linearization. It already ranks value’s long-run premium above growth’s. Campbell–Shiller points for $$\log(P/D)$$: 3.65 (growth), 3.10 (value), 3.24 (market). The full 5.3 percent in Table VII comes from the numerical solver on the next two pages.

> **Check.** Why does $$\phi_{\text{value}}>\phi_{\text{growth}}$$ raise expected returns *and* lower P/D? What would break if we set $$\gamma=1/\psi$$?

[Calibration]({% link calibration.md %}) chooses the numbers that feed this machine.
