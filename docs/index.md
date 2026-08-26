---
title: Home
nav_order: 1
permalink: /
---

# Is the Value Premium a Puzzle?

Dana Kiku  
Job Market Paper — January 17, 2006  
Companion package `kiku_value_premium` 0.3.0

[Time series]({{ '/time-series.html' | relative_url }}) · [Cross section]({{ '/cross-section.html' | relative_url }}) · [Other risk premia]({{ '/other-risk-premia.html' | relative_url }}) · [Climate]({{ '/climate.html' | relative_url }})  
[Package]({{ '/package.html' | relative_url }}) · [Installation]({{ '/installation.html' | relative_url }}) · [API]({{ '/api.html' | relative_url }}) · [Other portfolios]({{ '/generalization.html' | relative_url }})  
[Section 2]({{ '/empirical.html' | relative_url }}) · [Section 3]({{ '/model.html' | relative_url }}) · [Section 4]({{ '/calibration.html' | relative_url }}) · [Section 5]({{ '/implications.html' | relative_url }}) · [Value]({{ '/value.html' | relative_url }}) · [further.html]({{ '/further.html' | relative_url }})

## Abstract

This paper provides an economic explanation of the value premium puzzle, differences in price/dividend and Sharpe ratios of value and growth assets, volatilities of ex-post returns on the two stocks and their correlation. I consider a model that features two equally important ingredients: a small persistent component in cash-flow growth dynamics and the Epstein–Zin recursive utility preferences.

In the model, as in the data, cash flows of value firms are highly exposed to low-frequency fluctuations in aggregate consumption, whereas growth firms’ dividends are mainly driven by short-lived consumption news and risks related to fluctuating economic uncertainty. I show that the dispersion in long-run risks is the key mechanism that allows the model to quantitatively replicate the magnitude of the historical value premium, resolving the puzzle. Furthermore, heterogeneity in systematic risks across firms helps account for the whole transitional dynamics of value and growth returns, as well as the empirical failure of the CAPM and C-CAPM.

The model generates a value premium of about 5.3 percent per annum against about 6 percent in the 1930–2003 sample. In addition, the model is able to successfully accommodate the time-series behavior of the aggregate equity market.

```python
from kiku_value_premium.model import get_table_ii_params, solve_analytical, print_value_premium

print_value_premium(solve_analytical(get_table_ii_params()))
```

## 1. Introduction

Macro-finance studies the link between asset prices and economic fluctuations (Cochrane 2017). The facts that organized the field are time-series facts about the market. Stocks earn more than bonds by more than power utility over aggregate consumption can justify (Mehra and Prescott 1985). The risk-free rate is too low. Prices move more than dividends (Shiller 1981). The discount factor implied by returns is more volatile than consumption growth raised to a modest power — the Hansen and Jagannathan (1991) bound. Cochrane’s survey is explicit about the common mechanism that later models share: the market’s ability to bear risk varies over time, with the business cycle. The frameworks differ. Habits (Campbell and Cochrane 1999) put that variation in surplus consumption. Rare disasters put it in a tail. Long-run risks put it in a small persistent component of consumption growth, priced by recursive utility.

Bansal and Yaron (2004) is the long-run risks model as a *time-series* resolution. Consumption and dividends contain a slowly moving expected-growth factor $$x_t$$ and fluctuating uncertainty. Preferences are Epstein and Zin (1989): risk aversion is no longer the reciprocal of the elasticity of intertemporal substitution, so news about $$x_t$$ is priced. The objects the paper is asked to match are the equity premium, the risk-free rate, the volatility of the market return and of $$\log(P/D)$$, and the predictability of market returns by the dividend yield. Bansal, Kiku, and Yaron (2012) take the same objects to estimation. That is how the model is usually judged. Cochrane (2017) lists long-run risks in that sampling — recursive utility, Bansal and Yaron, Bansal, Kiku, and Yaron — next to habits and disasters, as competing accounts of the *market*.

The same IMRS implies a cross-section. A claim whose dividends load more on $$x_t$$ covaries more with the priced long-run shock. The Euler equation requires a higher expected return and a lower price–dividend ratio. That implication is often overlooked. Evaluations of long-run risks stop at the market column. Book-to-market, profitability, investment, and size are treated as a different literature, to be priced by factors rather than by consumption. I show that the overlooked column is not a separate theory. It is the same investor, applied to claims that differ only in cash-flow loadings.

The first such pair is value versus growth. Over 1930–2003 the high book-to-market quintile earned 13.88 percent a year and the low book-to-market quintile 7.81 percent. Market betas of both portfolios sit near one. A model that prices only covariance with the market cannot justify the gap. Value dividends move with the slow part of consumption; growth dividends barely do. I introduce those two claims into the Bansal–Yaron economy, choose their loadings from consumption and dividends, and read premia and valuations off the Euler equation. Average returns do not enter the cash-flow step.

Two ingredients do the work, and both are necessary. Consumption growth is not i.i.d. Preferences are recursive. Under power utility the price of long-run news is zero, and a gap in long-run leverage does not generate a large premium.

[Time series]({{ '/time-series.html' | relative_url }}) is the standard test: the model, the market claim, and the moments Bansal and Yaron were written to match. [Cross section]({{ '/cross-section.html' | relative_url }}) is the overlooked test: value versus growth under that investor. [Other risk premia]({{ '/other-risk-premia.html' | relative_url }}) asks whether the same mapping extends to size, profitability, and investment (Fama and French 2015). [Climate]({{ '/climate.html' | relative_url }}) asks it of transition and physical sorts after Melin and Zhang (2026) put climate into consumption — still a time-series statement about the market until the loadings are allowed to differ across firms.

## References

Kiku, D. 2006. “Is the Value Premium a Puzzle?” Job Market Paper, Duke University / Wharton.

Bansal, R., and A. Yaron. 2004. “Risks for the Long Run: A Potential Resolution of Asset Pricing Puzzles.” *Journal of Finance* 59 (4): 1481–1509.

Bansal, R., D. Kiku, and A. Yaron. 2012. “An Empirical Evaluation of the Long-Run Risks Model for Asset Prices.” *Critical Finance Review* 1: 183–221.

Campbell, J., and J. Cochrane. 1999. “By Force of Habit: A Consumption-Based Explanation of Aggregate Stock Market Behavior.” *Journal of Political Economy* 107 (2): 205–251.

Cochrane, J. 2017. “Macro-Finance.” *Review of Finance* 21 (3): 945–985.

Epstein, L., and S. Zin. 1989. “Substitution, Risk Aversion, and the Temporal Behavior of Consumption and Asset Returns.” *Econometrica* 57 (4): 937–969.

Fama, E., and K. French. 1993. “Common Risk Factors in the Returns on Stocks and Bonds.” *Journal of Financial Economics* 33 (1): 3–56.

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Hansen, L., and R. Jagannathan. 1991. “Implications of Security Market Data for Models of Dynamic Economies.” *Journal of Political Economy* 99 (2): 225–262.

Mehra, R., and E. Prescott. 1985. “The Equity Premium: A Puzzle.” *Journal of Monetary Economics* 15 (2): 145–161.

Melin, L., and F. Zhang. 2026. “Quantifying Climate Risk Premia.” EDHEC Climate Institute.

Shiller, R. 1981. “Do Stock Prices Move Too Much to Be Justified by Subsequent Changes in Dividends?” *American Economic Review* 71 (3): 421–436.
