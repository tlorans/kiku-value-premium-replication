---
title: From DCF to general equilibrium
nav_order: 2
---

# From DCF to general equilibrium
{: .no_toc }

1. TOC
{:toc}


**Hook.** A bankable DCF at $$r-g=4\%$$ prices the firm at 25 times dividends. Shave the discount rate by one point and a third of the value moves. Where did that point come from?

**Naive take.** Pick $$g$$ from an analyst note and $$r$$ from a CAPM beta, independently. The two numbers are "just inputs."

**Outcomes this page.**
- F — say why $$r$$ and $$g$$ are not independent once cash-flow risk is priced.
- Q — compute Gordon $$P/D=1/(r-g)$$ at 4% and at 3% by hand.
- P — install `lrrcs`, solve Table II, and read the printed long-run premia as an output, not a target.


You already know how to price a stock. Forecast the cash flows, pick a discount rate, divide. Every valuation you have ever built runs on those two numbers. This book is about where the two numbers come from — and why, in the end, they are really one number.

## Two numbers you made up

Start with the workhorse. If dividends grow at a constant rate $$g$$ and you discount at a constant rate $$r$$, the price–dividend ratio is

$$\frac{P}{D} = \frac{1}{r - g}.$$

Everything interesting in asset pricing hides inside $$r-g$$. And the DCF is silent about both halves. Where did you get $$r$$? A CAPM regression, a corporate hurdle rate, or "eight percent seems reasonable." Where did you get $$g$$? Analyst forecasts, a historical average, a terminal-value convention. Nothing in the framework stops you from pairing any $$g$$ with any $$r$$.

The numbers are not innocent. At $$r-g = 4\%$$ the price–dividend ratio is 25. Shave the discount rate by one percentage point and the price jumps by a third. A third of the firm's value, riding on a number you made up.

Worse, the two numbers are not independent, and the DCF cannot see why. A firm whose cash flows collapse in bad times *should* carry a high discount rate — the discount rate is compensation for exactly the risk that sits in the cash flows. Choose the numerator and the denominator separately and you have assumed away the entire question: why do risky cash flows command high expected returns, and how high?

## One primitive instead

General equilibrium replaces the two free numbers with one measurable primitive: aggregate consumption.

Consumption growth, in this economy, is not white noise. It carries a small but highly persistent component $$x_t$$ — long-run risks — and its volatility moves over time. Two modelling decisions then split the DCF's job between them:

- **The cash-flow model.** Each asset's dividend growth loads on $$x_t$$ with a leverage coefficient $$\phi$$. That loading is *estimated* from consumption and dividend data. This is where $$g$$ comes from — not a constant you assume, but a process tied to the macroeconomy.
- **The discount-rate model.** A household with Epstein–Zin preferences owns every claim and fears news about long-run growth. Its marginal utility, driven by the *same* $$x_t$$, prices the cash flows. This is where $$r$$ comes from.

One shock to $$x_t$$ moves expected dividends for decades and moves marginal utility at the same instant. That comovement — not either piece alone — is the risk premium. Prices and premia stop being inputs and become outputs, and outputs can be wrong. That is the point: the model is falsifiable, claim by claim, in both prices and premia. Average returns never enter the inputs.

## Install

Python 3.11+. Clone the repository and install in editable mode with `uv`.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

```python
import numpy as np
import lrrcs as lrr

lrr.__version__
```

Nothing below needs credentials or downloads. Data construction starts in [Financial data]({{ '/financial-data.html' | relative_url }}).

## An economy in five lines

Kiku (2006, Table II) is the default economy: Epstein–Zin preferences, a persistent component $$x_t$$ in consumption growth, time-varying consumption volatility, and three dividend claims — growth, value, market — that differ *only* in how hard their cash flows load on $$x_t$$. The numbers are monthly.

```python
delta, gamma, psi = 0.999, 10.0, 1.5
theta = (1.0 - gamma) / (1.0 - 1.0 / psi)
mu_c, rho, phi_x, sigma = 0.0015, 0.98, 0.032, 0.0064
phi = {"growth": 2.6, "value": 6.2, "market": 2.8}
theta, rho, phi
```

```text
(-27.0, 0.98, {'growth': 2.6, 'value': 6.2, 'market': 2.8})
```

Look at what is *not* in that block. No expected returns. No risk premia. No prices. Preferences ($$\delta,\gamma,\psi$$), a consumption process ($$\mu_c,\rho,\varphi_x,\sigma$$), and three cash-flow loadings. Value's dividends lever long-run consumption news at 6.2; growth's at 2.6. That dispersion in cash-flow risk — not the six-percent gap in average returns — is the only cross-sectional input the equilibrium gets.

Why $$\theta = -27$$? Because Epstein–Zin preferences separate aversion to risk ($$\gamma = 10$$) from aversion to substitution over time ($$\psi = 1.5$$), which power utility welds together. The household's marginal rate of substitution then depends not only on consumption tomorrow but on the return on total wealth — on news about the *entire future*. A small piece of bad news about $$x_t$$ lowers expected consumption for decades, and this household will pay dearly to avoid assets that fall on exactly that news.

Now solve the economy.

```python
params = lrr.get_table_ii_params()
params.prefs.gamma, params.cons.rho
params.dividends["value"].phi, params.dividends["growth"].phi
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

**What that did.** It solved for prices and premia jointly. The premia line is the discount-rate model at work: one price of long-run risk, $$\Lambda_\epsilon = 5.95$$, times each claim's exposure. The $$A_1$$ line is the same solution read as a valuation statement: value's price–dividend ratio is more than twice as elastic to long-run news as growth's. One solve, both objects — the DCF's $$r$$ and $$g$$, fused.

**What that did not do.** It estimated nothing and matched nothing. The loadings were Kiku's, taken on faith. The 0.40 percent is only the long-run *piece* of the value premium; the full Euler-equation spread is about 5.3 percent against roughly 6 in the data, and value's price–dividend ratio sits below growth's — that scoreboard is [The Cross Section]({{ '/cross-section.html' | relative_url }}). Getting from raw data to those loadings, honestly, is the work of the next three chapters.

## Key takeaways

- The DCF takes $$E[CF]$$ and $$r$$ as two independent inputs. The equilibrium derives both from one primitive — the consumption process — and they are not independent: the risk in cash flows *is* what the discount rate prices.
- The cash-flow model lives in the dividend loadings on $$x_t$$; the discount-rate model lives in Epstein–Zin marginal utility. Both are disciplined by data before any return is looked at.
- Assets differ only in cash-flow exposure. Prices and premia — value's low $$P/D$$ and high expected return together — are outputs, and can fail.
- `lrr.solve_analytical` is the whole equilibrium in one call: risk premia and valuation elasticities from the same solution.

Next: [Financial data]({{ '/financial-data.html' | relative_url }}), where we construct consumption, dividends, and the value and growth cash flows from the raw records.

## Pitfalls

- Finance — treating APR-style annualization as harmless when Table II is monthly.
- Finance — reading the 0.40 percent long-run *piece* as the whole value premium.
- Python — importing `from lrrcs.model import ...`. Documented code stays at `lrr.`.
