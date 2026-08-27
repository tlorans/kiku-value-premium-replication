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

A *claim* is a stream of cash flows — here, dividends — and the price people pay for it. Asset pricing says that price should equal expected discounted cash flows. The *discount factor* is the random variable that turns a future payoff into a present value. If that discount factor did not move around, prices would move only when cash-flow news arrived. They do not. Prices are too volatile. Returns can be forecast. Stocks earn more than bonds. That is the field (Cochrane 2017).

The first facts are facts about *one* claim over time: the market portfolio of stocks. Call those *time-series* facts. The *equity premium* is the extra average return of stocks over a safe bond. It is 4 to 8 percent a year. Even 4 percent is large. A household that dislikes risk in the simplest way — power utility over this year’s aggregate consumption — cannot produce that premium unless it is implausibly risk averse (Mehra and Prescott 1985). The safe rate is too low and too smooth. Prices move more than dividends (Shiller 1981). Hansen and Jagannathan (1991) put the same point as a bound: the discount factor has to bounce around more than consumption raised to any modest power.

Later models share one idea. The market’s willingness to bear risk is higher in good times and lower in bad times. They differ in the mechanism. *Habits* put that variation in how close consumption sits to a slowly moving standard of living (Campbell and Cochrane 1999). *Disasters* put it in a rare crash. *Long-run risks* put it in a small, persistent piece of expected consumption growth, which I will call $$x_t$$. That piece is priced only if households care separately about risk and about substituting consumption across time. That preference is *recursive utility* (Epstein and Zin 1989; Bansal and Yaron 2004).

Look at what the long-run risks papers are asked to match. The equity premium. The safe rate. How much the market return and the log price–dividend ratio bounce. Whether a high dividend yield forecasts a high return. All of that is a test of *one claim through time*. It is still how the model is usually judged.

The same discount factor implies a *cross section*: a ranking across claims at a date. If firm A’s dividends move more with $$x_t$$ than firm B’s, A covaries more with the shock the household cares about. Then A must earn a higher average return, and A must sell cheaper relative to its current dividend. That is not a new theory. It is the same pricing equation used twice. The pricing equation is the *Euler equation*: expected discount factor times gross return equals one.

That second column is often overlooked. Sorts on book-to-market, profitability, investment, and size are usually priced by *factors* — returns on other portfolios — not by consumption. I show the overlooked column is the same household, applied to claims that differ only in how their dividends are written.

The first pair is value versus growth. *Book-to-market* is the accounting book value of equity divided by its market price. *Value* stocks have a high ratio (cheap relative to books). *Growth* stocks have a low ratio. Over 1930–2003 the top book-to-market fifth earned 13.88 percent a year and the bottom fifth 7.81 percent. A *CAPM beta* is the slope of a stock’s return on the market return. Both fifths have betas near one, so covariance with the market cannot be the story. Value dividends move with the slow part of consumption. Growth dividends barely do. Kiku (2006) measures that gap in cash flows, not in returns, and then reads prices from the Euler equation. About 5.3 percent of extra return on value against about 6 percent in the sample. The market column still matches.

Two ingredients, both required. Consumption growth is not independent from year to year, or there is no $$x_t$$. Preferences are recursive, or news about $$x_t$$ is not priced. Under power utility that price is zero. Then a gap in how dividends load on $$x_t$$ does nothing.

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

[Time series]({{ '/time-series.html' | relative_url }}) is the usual test: can this household price the market? [Cross section]({{ '/cross-section.html' | relative_url }}) is the overlooked test: can the same household rank value above growth? [Other risk premia]({{ '/other-risk-premia.html' | relative_url }}) asks the same question of size, profitability, investment, and industries. [Climate]({{ '/climate.html' | relative_url }}) asks it after climate is put into consumption. A 20 percent rise in the *market* premium is still a time-series statement. It does not rank firms.

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
