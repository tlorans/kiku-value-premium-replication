---
title: From DCF to general equilibrium
nav_order: 2
---

# From DCF to general equilibrium
{: .no_toc }

1. TOC
{:toc}

You already know how to price a stock. Forecast the cash flows, pick a discount rate — the annual return you demand for holding something this risky — and divide. That is the discounted-cash-flow recipe, DCF for short, and every valuation you have ever built runs on those two numbers. This chapter is about where the two numbers come from, and why, in a coherent model of the economy, they are really one number.

## Two numbers you made up

Start with the workhorse. Suppose dividends grow forever at a constant rate $$g$$ and you discount them at a constant rate $$r$$. Then the price–dividend ratio — the price of the stock per dollar of current dividend — is

$$\frac{P}{D} = \frac{1}{r - g}.$$

Everything interesting in asset pricing hides inside $$r-g$$. And the DCF is silent about both halves. Where did you get $$r$$? A corporate hurdle rate, a regression, or "eight percent seems reasonable." Where did you get $$g$$? Analyst forecasts, a historical average, a terminal-value convention. Nothing in the framework stops you from pairing any $$g$$ with any $$r$$.

The numbers are not innocent. At $$r-g = 4\%$$ the price–dividend ratio is 25. Shave the discount rate by one percentage point and the price jumps by a third. A third of the firm's value, riding on a number you made up.

Worse, the two numbers should not be independent, and the DCF cannot say why. The discount rate on a risky asset is the safe interest rate plus a *risk premium* — extra expected return, demanded as compensation for bearing the risk. And where does the risk live? In the cash flows. A firm whose dividends collapse in bad times *should* carry a high discount rate; the premium is payment for exactly the danger that sits in the numerator. Choose numerator and denominator separately and you have assumed away the central question of the field: which cash-flow risks command high expected returns, and how high?

## One primitive instead

A general-equilibrium model closes the loop. Put one investor in the economy — a stand-in for everybody. Give the economy a consumption stream, and define each asset by the dividends it pays; call such an asset a *claim*, since that is what it is, a claim to a stream of cash. Now require that prices adjust until the investor is content to hold exactly the assets that exist. That requirement — that is all "general equilibrium" means here — leaves nothing for you to choose. Prices, and the risk premia inside them, are whatever makes the investor's books balance.

One measurable primitive drives everything: aggregate consumption. Its growth is not pure noise. It carries a small, stubbornly slow-moving component — call it $$x_t$$, and call the risk of news about it *long-run risk*, since a shock to $$x_t$$ is news about growth for the next decade, not just this year. Two modelling decisions then split the DCF's job between them:

- **The cash-flow model.** Each claim's dividend growth moves with $$x_t$$, scaled by a coefficient $$\phi$$ — its cash-flow *leverage*, the number of units dividend growth moves per unit of expected consumption growth. That coefficient is *estimated* from consumption and dividend data. This is where $$g$$ comes from: not a constant you assume, but a process tied to the economy.
- **The discount-rate model.** The investor fears bad news about long-run growth and must be paid to hold claims that suffer on such news. How much? That depends on preferences — and preferences plus the *same* consumption process pin it down. This is where $$r$$ comes from.

One shock to $$x_t$$ moves expected dividends for decades and makes the investor poorer at the same instant. That comovement — not either piece alone — is the risk premium. Prices and premia stop being inputs and become outputs, and outputs can be wrong. That is the point: the model is falsifiable, claim by claim, in both prices and premia. Average returns never enter the inputs.

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

Kiku (2006) is the paper this book replicates; her Table II lists the parameters of the benchmark economy, and we take it as our default. The economy has the slow component $$x_t$$ in consumption growth, volatility that itself drifts over time, and three claims — growth, value, market — that differ *only* in cash-flow leverage. The numbers are monthly.

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

Read the first line as the investor: $$\delta$$ is patience, $$\gamma$$ is risk aversion (how painful uncertainty is), and $$\psi$$ is the willingness to shift consumption across time. Read the third line as the economy: mean growth $$\mu_c$$, the persistence $$\rho$$ of the slow component (0.98 per month — news about $$x_t$$ takes years to die out), and the sizes of the shocks. Read the fourth line as the assets: value's dividends lever the slow component at 6.2, growth's at 2.6.

Now look at what is *not* in the block. No expected returns. No risk premia. No prices. An investor, an economy, and three cash-flow exposures. That dispersion in cash-flow risk — not the six-percentage-point gap in average returns you may already know about — is the only cross-sectional input the model gets.

Why does $$\theta = -27$$ matter? Standard "power utility" preferences force one parameter to do two jobs: your distaste for risk and your distaste for moving consumption across time must be the same number. The preferences here — Epstein–Zin, after their inventors — cut those apart, and $$\theta$$ measures the gap. With $$\gamma=10$$ and $$\psi=1.5$$ the investor hates risk far more than she hates rescheduling consumption, and — this is the consequence that drives the whole book — she especially hates *news that the future has gotten worse*, even when today's consumption is untouched. A claim that pays badly on such news must offer her a premium.

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

**What that did.** It solved for prices and premia jointly. The premia lines are the discount-rate model at work: one price of long-run risk — the premium earned per unit of exposure to $$x$$-news, printed as `Lambda_eps` — times each claim's exposure. The `A1` line is the same solution read as a statement about prices: it is the sensitivity of each claim's price–dividend ratio to the slow component, and value's is more than twice growth's. One solve, both objects — the DCF's $$r$$ and $$g$$, fused.

**What that did not do.** It estimated nothing and matched nothing. The loadings were Kiku's, taken on faith. And the 0.40 percent is only the piece of the value premium earned for long-run risk under this quick linear approximation; solving the model in full puts the value-minus-growth spread near 5.3 percent, against roughly 6 in the data, with value's price–dividend ratio below growth's — prices and premia both. That scoreboard is [The Cross Section]({{ '/cross-section.html' | relative_url }}). Getting from raw data to those loadings, honestly, is the work of the next three chapters.

## Key takeaways

- The DCF takes expected cash flows and the discount rate as two independent inputs. The equilibrium derives both from one primitive — the consumption process — and they are not independent: the risk in the cash flows *is* what the discount rate prices.
- The cash-flow model lives in each claim's leverage on the slow component of consumption growth. The discount-rate model lives in an investor who fears long-run bad news. Both are disciplined by data before any return is looked at.
- Claims differ only in cash-flow exposure. Prices and premia — value's low price–dividend ratio and high expected return together — are outputs, and can fail.
- `lrr.solve_analytical` is the whole equilibrium in one call: risk premia and price sensitivities from the same solution.

Next: [Financial data]({{ '/financial-data.html' | relative_url }}), where we construct consumption, dividends, and the value and growth cash flows from the raw records.
