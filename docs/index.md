---
title: Home
nav_order: 1
permalink: /
---

# Is the Value Premium a Puzzle?

**In a nutshell.** Cheap stocks have historically paid their owners more than expensive stocks. The usual risk measure — how much a stock bounces with the market — cannot explain that gap. Dana Kiku’s answer is that cheap stocks are more tied to *slow* news about the real economy. This package rebuilds her argument, in her order.

{: .idea }
Think of two landlords. One owns a shiny new building (growth). The other owns a tired building that the market already marked down (value). Over 1930–2003 the tired building paid more. If both buildings rise and fall with the city by about the same amount, a simple “market risk” story says they should pay the same. They did not. Either the extra rent is a free lunch, or we are measuring the wrong kind of risk.

## If you are lost, start here

We are not building a trading strategy. We are not fitting a model to the 6 percent extra return. We are asking one question:

> If value firms’ **dividends** really load more on long-run consumption than growth firms’ dividends do, must investors who care about the long run demand a higher return on value — even when CAPM betas look the same?

The site is that question, split into four steps. Skip a step and the later numbers become uninterpretable. Feed the 6 percent into the third step and the fourth step is no longer a test.

```
1. Measure the facts                 Empirical
2. Write the pricing machine         Model
3. Fit cash flows only               Calibration
4. Read off prices and returns       Implications
```

## Words we will keep using

| Word | Plain meaning |
|:---|:---|
| Value | The cheap fifth of listed US stocks (high book equity relative to price). |
| Growth | The expensive fifth (low book-to-market). |
| Value premium | Extra average return of value over growth: about 6 percent a year in 1930–2003. |
| CAPM beta | How tightly a stock moves with the market. Both groups sit near 1. |
| Dividend | Cash the portfolio paid that year (from CRSP return minus capital-gain return). |
| Consumption | Real per-capita spending on nondurables and services — a stand-in for the real economy. |
| $$x_t$$ | A small, persistent piece of consumption growth: the *outlook*, not this month’s blip. |
| $$\phi$$ | Long-run leverage: how hard a shift in $$x_t$$ hits this portfolio’s dividends. |

## The puzzle

Sort listed US firms by book-to-market. The top quintile is value, the bottom is growth, and the market is the CRSP value-weighted portfolio of ordinary shares. Over 1930–2003, value earned about 14 percent a year and growth about 8 percent. Both had market betas near 1. A model that prices only covariance with the market cannot justify a 6 percent gap.

That is the puzzle. Either the extra return is a free lunch, or beta is the wrong risk measure.

## The story we are testing

{: .idea }
Consumption growth is not pure noise. Most of it is this month’s weather. A small piece, $$x_t$$, is the climate: it shifts the outlook for years. A rainy Tuesday is annoying. A multi-year drought changes what a farm is worth. Value firms, in her data, behave more like farms that depend on the climate.

Investors with Epstein–Zin preferences have two separate knobs: how much they dislike a bumpy ride (risk aversion $$\gamma$$), and how willing they are to wait for consumption (the IES $$\psi$$). They dislike news about the climate more than a one-month blip.

Firms differ in how much their dividends load on $$x_t$$. That loading is $$\phi$$. If value has a larger $$\phi$$ than growth, value *must* pay a higher premium and sell at a lower price–dividend ratio. CAPM beta can still fail, because beta measures comovement with the *market*, not with $$x_t$$.

With $$\rho=0.98$$ and Table II loadings, her model produces about 5.3 percent of value premium against about 6 percent in the data.

## How the replica is organized

Each page answers three questions: **what** we are doing, **why** that step exists, and **how** to run it.

1. [Empirical evidence]({% link empirical.md %}). Build value, growth, and the market. Document the 6 percent spread, the P/D ranking, and whether value dividends really track long-run consumption.
2. [The long-run risks model]({% link model.md %}). Write the preferences and the cash-flow processes, then solve for prices.
3. [Calibration]({% link calibration.md %}). Fit only consumption and dividend dynamics. Do not target the premium. If the premium appears afterward, it is a prediction.
4. [Asset pricing implications]({% link implications.md %}). Check expected returns, valuations, and whether CAPM betas still fail.

[Install]({% link installation.md %}) with `uv`. Table II solves without WRDS. Table I and Figures 1–4 need `[data]` and a repo-root `.env`. [API]({% link api.md %}). [Other portfolios]({% link generalization.md %}).

## References

Kiku, D. 2006. “Is the Value Premium a Puzzle?” Job Market Paper, Duke University.

Bansal, R., and A. Yaron. 2004. “Risks for the Long Run: A Potential Resolution of Asset Pricing Puzzles.” *Journal of Finance* 59 (4): 1481–1509.
