---
title: Home
nav_order: 1
permalink: /
---

# Is the Value Premium a Puzzle?

Dana Kiku  
Job Market Paper — January 17, 2006  
Companion package `kiku_value_premium` 0.3.0

[Section 2]({% link empirical.md %}) · [Section 3]({% link model.md %}) · [Section 4]({% link calibration.md %}) · [Section 5]({% link implications.md %}) · [Section 6]({% link further.md %}) · [Section 7]({% link climate.md %})  
[Installation]({% link installation.md %}) · [API]({% link api.md %}) · [Other portfolios]({% link generalization.md %})

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

The time-series object is the market claim: the equity premium, the risk-free rate, return volatility, persistence of $$\log(P/D)$$, and the failure of a consumption CAPM fitted to the aggregate. Matching those moments is the usual test of a consumption-based model. It is not the test that resolves the value premium.

The cross-sectional object is a pair of claims that differ only in how their dividends load on the persistent component of consumption. Value is the first such pair, and it is the argument of the paper. Growth and value have market betas near one. They do not have the same loading $$\phi$$ on $$x_t$$. An Epstein–Zin investor with $$\gamma \neq 1/\psi$$ prices that difference. The Euler equation then requires a higher expected return on value and a lower price–dividend ratio.

Two ingredients do the work, and both are necessary. Consumption and dividend growth contain a small persistent component $$x_t$$. Preferences are recursive. Under power utility the price of long-run news is zero, and a gap in $$\phi$$ does not generate a large premium.

The argument has four steps.

1. Measure cash flows and returns of book-to-market portfolios. The six-percent premium is a fact to be explained. It is not a calibration target ([Section 2]({% link empirical.md %})).
2. Write preferences and cash-flow laws in which the three claims differ only by $$(\mu,\phi,\varphi,\alpha)$$ ([Section 3]({% link model.md %})).
3. Choose those loadings, and the remaining cash-flow parameters, from consumption and dividend moments only ([Section 4]({% link calibration.md %})).
4. Read expected returns and price–dividend ratios off the Euler equation ([Section 5]({% link implications.md %})). The market column of Table VII is the time-series check. The value–growth columns are the cross-section.

If the premium appears in step 4, it is a prediction. Feeding the premium into step 3 would assume the puzzle away.

Table II long-run leverages are $$\phi_V=6.2$$ and $$\phi_G=2.6$$. Persistence of expected consumption growth is $$\rho=0.98$$. With those numbers the model produces about 5.3 percent of value premium, a lower mean $$\log(P/D)$$ on value than on growth, and a value-to-growth CAPM-beta ratio below one. The same calibration accommodates the time-series behavior of the market.

Fama and French (2015) isolate further CAPM failures — profitability, investment, and size. [Section 6]({% link further.md %}) records those facts and states the same cross-sectional test. Melin and Zhang (2026) put climate into the consumption process and price the market. [Section 7]({% link climate.md %}) writes the corresponding test for transition and physical sorts. Those premia are not calibration targets either. Value remains the first argument. The later sections ask whether the same IMRS still has cross-sectional pricing power once the characteristic is no longer book-to-market.

The companion package follows the same order. Four subpackages implement Sections 2–5. Core installation solves the model at the Table II calibration with no data credentials. Reconstructing Table I from CRSP and Compustat requires the optional `[data]` extra and a WRDS login; see [Installation]({% link installation.md %}).

## References

Kiku, D. 2006. “Is the Value Premium a Puzzle?” Job Market Paper, Duke University / Wharton.

Bansal, R., and A. Yaron. 2004. “Risks for the Long Run: A Potential Resolution of Asset Pricing Puzzles.” *Journal of Finance* 59 (4): 1481–1509.

Epstein, L., and S. Zin. 1989. “Substitution, Risk Aversion, and the Temporal Behavior of Consumption and Asset Returns.” *Econometrica* 57 (4): 937–969.

Fama, E., and K. French. 1993. “Common Risk Factors in the Returns on Stocks and Bonds.” *Journal of Financial Economics* 33 (1): 3–56.

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Melin, L., and F. Zhang. 2026. “Quantifying Climate Risk Premia.” EDHEC Climate Institute.
