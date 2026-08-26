---
title: Home
nav_order: 1
permalink: /
---

# Is the Value Premium a Puzzle?

Dana Kiku — Job Market Paper, January 17, 2006  
Companion package `kiku_value_premium` 0.3.0

**In a nutshell.** Value firms earn a higher average return than growth firms, sell at a lower price–dividend ratio, and load more heavily on the persistent component of consumption growth. I show that this dispersion in long-run cash-flow risk, priced by Epstein–Zin preferences, accounts for the historical value premium and for the failure of the CAPM.

This site is the paper, in paper order, with the code that implements each equation. The four sections map onto four subpackages.

| Paper | Site | Package |
|:---|:---|:---|
| 2. Empirical evidence | [Empirical]({% link empirical.md %}) | `kiku_value_premium.empirical` |
| 3. The long-run risks model | [Model]({% link model.md %}) | `kiku_value_premium.model` |
| 4. Calibration | [Calibration]({% link calibration.md %}) | `kiku_value_premium.calibration` |
| 5. Asset pricing implications | [Implications]({% link implications.md %}) | `kiku_value_premium.implications` |

[Installation]({% link installation.md %}) · [API]({% link api.md %}) · [Other portfolios]({% link generalization.md %})

## Abstract

This paper provides an economic explanation of the value premium puzzle, differences in price/dividend and Sharpe ratios of value and growth assets, volatilities of ex-post returns on the two stocks and their correlation. I consider a model that features two equally important ingredients: a small persistent component in cash-flow growth dynamics and the Epstein–Zin recursive utility preferences.

In the model, as in the data, cash flows of value firms are highly exposed to low-frequency fluctuations in aggregate consumption, whereas growth firms’ dividends are mainly driven by short-lived consumption news and risks related to fluctuating economic uncertainty. I show that the dispersion in long-run risks is the key mechanism that allows the model to quantitatively replicate the magnitude of the historical value premium, resolving the puzzle. Furthermore, heterogeneity in systematic risks across firms helps account for the whole transitional dynamics of value and growth returns, as well as the empirical failure of the CAPM and C-CAPM.

The model generates a value premium of about 5.3 percent per annum against about 6 percent in the 1930–2003 sample.

```python
from kiku_value_premium.model import get_table_ii_params, solve_analytical, print_value_premium

print_value_premium(solve_analytical(get_table_ii_params()))
```

Table II long-run leverages are $$\phi_V=6.2$$ and $$\phi_G=2.6$$. Calibration uses cash-flow moments only. Expected returns never enter.

## 1. Introduction

One of the most robust features of financial data is the finding that value firms, on average, have higher returns than growth firms. Over 1930–2003 the high book-to-market quintile earned 13.88 percent a year and the low book-to-market quintile 7.81 percent. Market betas of both portfolios sit near one. A model that prices only covariance with the market cannot justify a six-percent gap.

I introduce value, growth, and market portfolios into a general equilibrium model that features long-run consumption risks, in the sense of Bansal and Yaron (2004), and show that the model accounts for the differences in their expected returns, valuations, and the failure of the CAPM and C-CAPM.

The argument has four steps, and only four.

1. Measure cash flows and returns of book-to-market portfolios, without treating the six-percent premium as a calibration target ([Section 2]({% link empirical.md %})).
2. Write preferences and cash-flow laws in which dividend claims differ by their loading $$\phi$$ on the persistent expected-growth factor $$x_t$$ ([Section 3]({% link model.md %})).
3. Choose those loadings, and the remaining cash-flow parameters, from consumption and dividend moments only ([Section 4]({% link calibration.md %})).
4. Read expected returns and price–dividend ratios off the Euler equation ([Section 5]({% link implications.md %})).

If the premium appears in step 4, it is a prediction. Feeding the premium into step 3 would assume the puzzle away.

The companion package follows the same order. Core installation solves the model at the Table II calibration with no data credentials. Reconstructing Table I from CRSP/Compustat requires the optional `[data]` extra and a WRDS login; see [Installation]({% link installation.md %}).

## Notation used throughout

| Symbol | Meaning |
|:---|:---|
| Value / Growth | Top / bottom NYSE book-to-market quintile, June sort, 1930–2003. |
| Market | CRSP value-weighted portfolio of ordinary shares. |
| $$x_t$$ | Persistent expected-growth component of consumption. |
| $$\phi$$ | Loading of dividend growth on $$x_t$$ (long-run leverage). |
| $$\tilde\phi$$ | Slope in the annual projection (19); a check, not the monthly input. |
| $$\gamma,\psi,\delta$$ | Risk aversion, IES, and time discount of the Epstein–Zin investor. |
| $$M_{t+1}$$ | Intertemporal marginal rate of substitution. |

## References

Kiku, D. 2006. “Is the Value Premium a Puzzle?” Job Market Paper, Duke University / Wharton.

Bansal, R., and A. Yaron. 2004. “Risks for the Long Run: A Potential Resolution of Asset Pricing Puzzles.” *Journal of Finance* 59 (4): 1481–1509.
