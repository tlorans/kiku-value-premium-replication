---
title: Home
nav_order: 1
permalink: /
---

# Is the Value Premium a Puzzle?

Dana Kiku  
Job Market Paper — January 17, 2006  
Companion package `kiku_value_premium` 0.3.0

[Time series]({% link time-series.md %}) · [Cross section]({% link cross-section.md %}) · [Other risk premia]({% link further.md %}) · [Climate]({% link climate.md %})  
[The replica]({% link replica.md %}) · [Package]({% link package.md %}) · [Installation]({% link installation.md %}) · [API]({% link api.md %})  
[Section 2]({% link empirical.md %}) · [Section 3]({% link model.md %}) · [Section 4]({% link calibration.md %}) · [Section 5]({% link implications.md %}) · [Other portfolios]({% link generalization.md %}) · [Value]({% link value.md %})

The documentation is four objects. [Time series]({% link time-series.md %}) is the long-run risks model and the market claim. [Cross section]({% link cross-section.md %}) is value versus growth: methods and results from the paper, repackaged as one argument. [Other risk premia]({% link further.md %}) asks the same investor to price size, profitability, and investment. [Climate]({% link climate.md %}) asks it to price transition and physical sorts.

## Abstract

This paper provides an economic explanation of the value premium puzzle, differences in price/dividend and Sharpe ratios of value and growth assets, volatilities of ex-post returns on the two stocks and their correlation. I consider a model that features two equally important ingredients: a small persistent component in cash-flow growth dynamics and the Epstein–Zin recursive utility preferences.

In the model, as in the data, cash flows of value firms are highly exposed to low-frequency fluctuations in aggregate consumption, whereas growth firms’ dividends are mainly driven by short-lived consumption news and risks related to fluctuating economic uncertainty. I show that the dispersion in long-run risks is the key mechanism that allows the model to quantitatively replicate the magnitude of the historical value premium, resolving the puzzle. Furthermore, heterogeneity in systematic risks across firms helps account for the whole transitional dynamics of value and growth returns, as well as the empirical failure of the CAPM and C-CAPM.

The model generates a value premium of about 5.3 percent per annum against about 6 percent in the 1930–2003 sample. In addition, the model is able to successfully accommodate the time-series behavior of the aggregate equity market.

```python
from kiku_value_premium.model import get_table_ii_params, solve_analytical, print_value_premium

print_value_premium(solve_analytical(get_table_ii_params()))
```

## 1. Introduction

One of the most robust features of financial data is the finding that value firms, on average, have higher returns than growth firms. Over 1930–2003 the high book-to-market quintile earned 13.88 percent a year and the low book-to-market quintile 7.81 percent. Market betas of both portfolios sit near one. A model that prices only covariance with the market cannot justify a six-percent gap. That is the value premium puzzle.

I introduce value, growth, and market portfolios into a general equilibrium model that features long-run consumption risks, in the sense of Bansal and Yaron (2004). Once time-series dynamics of aggregate and asset-specific cash flows are calibrated to annual consumption and dividends, the model is asked to account for both time-series and cross-sectional properties of assets’ prices and returns.

The time-series object is the market claim. Preferences, the consumption process, and market dividends are chosen from consumption and dividend moments. The Euler equation is then asked for the equity premium, the risk-free rate, and market $$\log(P/D)$$. That check is [Time series]({% link time-series.md %}). Matching it is the usual test of a consumption-based model. It is not the test that resolves the value premium.

The cross-sectional object is value versus growth. The two claims have market betas near one. They do not have the same loading $$\phi$$ on $$x_t$$. An Epstein–Zin investor with $$\gamma \neq 1/\psi$$ prices that difference. Methods and results are [Cross section]({% link cross-section.md %}).

Two ingredients do the work, and both are necessary. Consumption and dividend growth contain a small persistent component $$x_t$$. Preferences are recursive. Under power utility the price of long-run news is zero, and a gap in $$\phi$$ does not generate a large premium.

The six-percent premium is a fact to be explained. It is not a calibration target. If it appears after the cash-flow step, it is a prediction.

Table II long-run leverages are $$\phi_V=6.2$$ and $$\phi_G=2.6$$. Persistence of expected consumption growth is $$\rho=0.98$$. With those numbers the model produces about 5.3 percent of value premium, a lower mean $$\log(P/D)$$ on value than on growth, and a value-to-growth CAPM-beta ratio below one. The same calibration accommodates the time-series behavior of the market.

Fama and French (2015) isolate further CAPM failures — profitability, investment, and size. Those facts, and the mapping onto $$(\mu,\phi,\varphi,\alpha)$$, are [Other risk premia]({% link further.md %}). They have not been used as calibration targets. Melin and Zhang (2026) put climate into consumption and price the market. [Climate]({% link climate.md %}) writes the corresponding cross-sectional test.

[The replica]({% link replica.md %}) keeps Sections 2–5 in paper order. Core installation solves Table II with no data credentials; see [Installation]({% link installation.md %}).

## References

Kiku, D. 2006. “Is the Value Premium a Puzzle?” Job Market Paper, Duke University / Wharton.

Bansal, R., and A. Yaron. 2004. “Risks for the Long Run: A Potential Resolution of Asset Pricing Puzzles.” *Journal of Finance* 59 (4): 1481–1509.

Epstein, L., and S. Zin. 1989. “Substitution, Risk Aversion, and the Temporal Behavior of Consumption and Asset Returns.” *Econometrica* 57 (4): 937–969.

Fama, E., and K. French. 1993. “Common Risk Factors in the Returns on Stocks and Bonds.” *Journal of Financial Economics* 33 (1): 3–56.

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Melin, L., and F. Zhang. 2026. “Quantifying Climate Risk Premia.” EDHEC Climate Institute.
