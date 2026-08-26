---
title: Home
nav_order: 1
permalink: /
---

# Long-run risks and the cross section

Companion package `lrrcs`

[Time series]({{ '/time-series.html' | relative_url }}) · [Cross section]({{ '/cross-section.html' | relative_url }}) · [Other risk premia]({{ '/other-risk-premia.html' | relative_url }}) · [Climate]({{ '/climate.html' | relative_url }})  
[Package]({{ '/package.html' | relative_url }}) · [Installation]({{ '/installation.html' | relative_url }}) · [API]({{ '/api.html' | relative_url }}) · [Other portfolios]({{ '/generalization.html' | relative_url }})  
[Section 2]({{ '/empirical.html' | relative_url }}) · [Section 3]({{ '/model.html' | relative_url }}) · [Section 4]({{ '/calibration.html' | relative_url }}) · [Section 5]({{ '/implications.html' | relative_url }}) · [further.html]({{ '/further.html' | relative_url }})

## Introduction

Asset prices should equal expected discounted cash flows. If discount rates were constant, prices would move when cash-flow news arrives and not otherwise. They do not. Prices are too volatile. Returns are forecastable. Stocks earn far more than bonds. That is the field (Cochrane 2017).

The facts that started it are time-series facts about the market. The equity premium is 4 to 8 percent. Even 4 percent is large. Power utility over aggregate consumption cannot produce it without absurd risk aversion (Mehra and Prescott 1985). The risk-free rate is too smooth and too low. Prices move more than dividends (Shiller 1981). Hansen and Jagannathan (1991) said the same thing with a bound: the discount factor has to be more volatile than $$C^{-\gamma}$$ at any sensible $$\gamma$$.

The models that followed share one idea. The market’s ability to bear risk is higher in good times and lower in bad times. They differ in the mechanism. Habits put the variation in surplus consumption (Campbell and Cochrane 1999). Disasters put it in a tail. Long-run risks put it in a small, persistent component of consumption growth, priced by recursive utility (Bansal and Yaron 2004; Bansal, Kiku, and Yaron 2012).

Look at what those papers are asked to match. The equity premium. The risk-free rate. The volatility of the market return and of $$\log(P/D)$$. Predictability by the dividend yield. That is a time-series test of one claim — the market. It is still how the model is usually judged.

The same discount factor implies a cross section. If claim A’s dividends load more on the persistent component $$x_t$$ than claim B’s, A covaries more with the shock the investor cares about. Then A must earn more, and A must sell cheaper relative to current dividends. That is not a separate theory. It is the Euler equation applied twice.

That column is often overlooked. Book-to-market, profitability, investment, and size live in a factor literature. They are priced by returns on other portfolios, not by consumption. I show the overlooked column is the same investor, applied to claims that differ only in cash-flow loadings.

The first pair is value versus growth. 1930–2003: high book-to-market earned 13.88 percent a year, low book-to-market 7.81 percent. Both CAPM betas sit near one. Covariance with the market cannot be the story. Value dividends move with the slow part of consumption. Growth dividends barely do. Kiku (2006) measures that gap in cash flows, not in returns, and reads prices off the Euler equation. About 5.3 percent of value premium against about 6 percent in the sample. The market column still matches.

Two ingredients, both required. Consumption growth is not i.i.d. Preferences are recursive. Under power utility the price of long-run news is zero. Then a gap in leverage does nothing.

```python
from lrrcs.model import get_table_ii_params, solve_analytical, print_long_short_premium

print_long_short_premium(solve_analytical(get_table_ii_params()))
```

[Time series]({{ '/time-series.html' | relative_url }}) is the usual test. [Cross section]({{ '/cross-section.html' | relative_url }}) is the overlooked one. [Other risk premia]({{ '/other-risk-premia.html' | relative_url }}) asks the same question of size, profitability, and investment. [Climate]({{ '/climate.html' | relative_url }}) asks it after climate is put into consumption. A 20 percent rise in the *market* premium is still a time-series statement. It does not rank firms.

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
