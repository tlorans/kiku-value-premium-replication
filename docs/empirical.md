---
title: Empirical Evidence
nav_order: 3
---

# Empirical Evidence: Value / Growth / Market
{: .no_toc }

{: .here }
No model yet. This page only builds three stock portfolios and US consumption, then reports how they behaved from 1930 to 2003. Later pages are not allowed to treat the 6 percent extra return as something to fit.

**In a nutshell.** Before writing a model, we have to see the facts: value paid more than growth, sold cheaper relative to dividends, and its dividends moved more with slow consumption.

{: .idea }
Imagine filing every listed US firm into two drawers each June: “the market already pays a high price for this firm, relative to its books” (growth) and “the market pays a low price” (value). Then record, year after year, (i) how much each drawer returned, (ii) how much cash it paid out, and (iii) how that cash moved when the country’s spending outlook had been strong. Those three records are this page. They are not yet a theory.

{: .why }
If we skip this step and jump to prices, we cannot tell whether the model is explaining the value premium or just assuming it. Section 2 of Kiku (2006) is the evidence the later pages may use as *cash-flow* targets, and must not use as *return* targets.

1. TOC
{:toc}

## What we are trying to measure

Three portfolios, one label each:

- **Growth**: firms the market already pays a high price for, relative to book equity (bottom book-to-market quintile).
- **Value**: firms the market pays a low price for (top quintile).
- **Market**: the CRSP value-weighted portfolio of ordinary shares.

We need, for each, a long annual history of *real returns*, *real dividend growth*, and the *price–dividend ratio*. We also need real per-capita consumption growth, because “long-run risk” means risk about future consumption, not about the stock market itself.

Three facts, in order:

1. Value paid about 6 percent a year more than growth, with market betas near 1.
2. Value still sold cheaper relative to the dividends it paid (lower P/D).
3. Value’s dividends moved more with slow consumption than growth’s did.

Fact 1 is the puzzle. Facts 2 and 3 are why a cash-flow story could be the resolution rather than a free lunch.

{: .paper }
“One of the most robust features of financial data is the finding that value firms, on average, have higher returns than growth firms.” Over 74 years the value strategy won about 70 percent of the time. Growth offered about 8 percent, value about 14 percent.

## 2.1 How the portfolios are built

Think of book-to-market as a filing rule, not as the risk measure. Each June we sort NYSE, AMEX, and NASDAQ ordinary shares using NYSE breakpoints, as in Fama and French (1993). Book equity is last fiscal year’s book, market equity is last December’s price times shares. Compustat does not start in 1930, so book equity through 1962 comes from the Davis–Fama–French Moody’s file.

{: .why }
We sort on price relative to books because that is how the literature defines value. We do **not** sort on past returns, and we do **not** sort on consumption betas. If we sorted on the thing we later call risk, the “test” would be circular.

Dividends are not taken from Compustat cash items. CRSP reports a return *with* dividends (`ret`) and a capital-gain return (`retx`). The gap is the cash the portfolio paid. Campbell and Shiller (1988) turn that gap into a per-share dividend series:

$$
D_{t+1}=y_{t+1}V_t,\qquad V_{t+1}=h_{t+1}V_t,\qquad V_0=100.
$$

Here $$y$$ is the dividend yield implied by `ret` versus `retx`, and $$h$$ is the capital-gain return. $$V$$ is a synthetic price index that starts at 100, so $$D$$ is the cash paid by one “share” of the portfolio.

{: .why }
We need a *per-share* dividend, not a firm’s total cash budget, because the present-value identity is about the price of a claim relative to the cash it pays. Using returns to *construct* dividends is not the same as using returns to *calibrate* risk premia. Calibration still sees only $$\Delta d$$ and $$\Delta c$$.

We then sum months to calendar years and deflate with the PCE deflator. Dividend growth is $$\Delta\log D$$. $$\log(P/D)$$ is year-end price over that year’s cumulative dividend. The real T-bill is the 90-day yield minus a 12-month average of inflation. Consumption is real per-capita nondurables plus services.

Table I uses Newey–West **8** lags. Table VI uses **4**. Figure 2 is **1952–2003**, as in her caption.

```python
from kiku_value_premium.empirical import (
    START, END, build_annual_panel, table_i, table_vi_data,
    figure1, figure2, figure3, figure4,
)
import pandas as pd

bm = build_annual_panel(refresh=False)
print(table_i(bm, START, END))
dc = pd.read_csv("data/consumption_annual.csv").set_index("year")["dc"]
print(table_vi_data(bm, dc, START, END))
```

`START, END = 1930, 2003`. `refresh=True` hits WRDS.

## 2.2 The value premium

This is the number the model later has to produce without being told it.

|  | E[R] % |  | σ(R) % |  | E[log P/D] |  |
|:---|---:|---:|---:|---:|---:|---:|
|  | Printed | Package | Printed | Package | Printed | Package |
| Growth | 7.81 (1.98) | 7.49 | 20.2 (2.00) | 20.0 | 3.61 (0.18) | 3.62 |
| Value | 13.88 (1.74) | 13.67 | 29.9 (4.34) | 29.7 | 3.25 (0.12) | 3.34 |
| Market | 8.56 (1.79) | 8.52 | 20.1 (2.23) | 20.1 | 3.34 (0.13) | 3.33 |

Printed cells are Newey–West 8-lag standard errors. Package returns and $$\log(P/D)$$ sit inside those bands. In her sample both CAPM betas are about 1.03, so volatility of returns does not rescue the CAPM either.

Return correlations (printed / package): GV 0.75 (0.05) / 0.72; GM 0.95 (0.01) / 0.95; VM 0.87 (0.04) / 0.86.

![Figure 1](figures/figure1.svg)

<p class="caption">Figure 1. Year by year, value minus growth. The bars are usually positive. That is the puzzle in the time series, not only in the average.</p>

## 2.3 Prices, dividend growth, and a tension

Value pays *more* on average and still sells *cheaper* relative to current dividends (mean $$\log(P/D)$$ 3.25 versus 3.61). That only makes sense if value’s cash flows are riskier in a way investors care about, or if expected growth is lower. We measure the cash-flow side next.

|  | E[Δd] % |  | σ(Δd) % |  |
|:---|---:|---:|---:|---:|
|  | Printed | Package | Printed | Package |
| Growth | 0.68 (1.25) | 0.33 | 13.9 (2.24) | 14.3 |
| Value | 3.63 (3.06) | 3.53 | 18.1 (2.69) | <mark class="out">47.7</mark> |
| Market | 0.85 (0.95) | 0.92 | 10.9 (2.41) | 11.0 |

Δd correlations (printed / package): GV 0.32 (0.17) / 0.29; GM 0.80 (0.09) / 0.78; VM 0.53 (0.10) / <mark class="out">0.64</mark>. Dividend growth comoves much less than returns. Prices share a discount-rate factor that dividends do not.

{: .caution }
1933 Value is a genuine zero-dividend year: every month has `ret = retx`, so Campbell–Shiller $$D_t=0$$, and that year’s $$P/D$$ and $$\Delta d$$ are missing. The collapse and rebound around that year push Value $$\sigma(\Delta d)$$, the Value–Market $$\Delta d$$ correlation, Value $$\tilde\phi$$, and Value innovation correlation outside her printed SEs. Those four cells are ranking and sign checks. Printed goldens are not edited.

## 2.4 The market, the T-bill, and consumption

The market earned about 8.5 percent; the real T-bill about 0.9 percent. That equity-premium fact is the *time-series* sibling of the value puzzle. Consumption growth is the quantity both must eventually be tied to:

|  | Printed | Package |
|:---|---:|---:|
| E[Δc] % | 1.96 (0.32) | 1.75 |
| σ(Δc) % | 2.20 (0.45) | 2.37 |
| AC(1) | 0.44 (0.12) | 0.41 |
| AC(2) | 0.16 (0.15) | 0.10 |

Autocorrelation of consumption is not zero. That is a hint that $$x_t$$ is in the data, not only in the model: this year’s growth partly forecasts next year’s.

## 2.5 Does the expected value premium move with consumption uncertainty?

{: .why }
If the extra return on value is compensation for risk that gets worse in bad times, the *expected* value premium should rise when consumption is harder to forecast. Figure 2 is that check, not a plot of raw returns.

She projects realized value-minus-growth on lagged P/D and dividend growth of the two portfolios, and plots the fitted series against a three-year average of squared AR(1) consumption residuals (rescaled). Sample: 1952–2003. Post-war correlation is about 40 percent.

![Figure 2](figures/figure2.svg)

<p class="caption">Figure 2. Expected value premium (solid) against consumption uncertainty (dashed), 1952–2003. They tend to rise together after the war.</p>

## Do value dividends track long-run consumption?

If consumption growth were i.i.d., its spectrum would be flat. Figure 3 is not flat: mass sits near frequency zero. That is the “long run” in the data.

Equation (19) asks a simpler question: when past consumption has been high for two years, do this year’s dividends rise, and by how much?

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2} \Delta c_{t-k} + \varepsilon_t.
$$

$$\tilde\phi$$ is *not* the monthly $$\phi$$ that later enters the solver. It is an annual check: a slope, not a price. Printed values: growth $$-0.38$$ (1.34), value $$2.16$$ (1.44), market $$0.66$$ (1.20). Value’s dividends move with the slow part of consumption; growth’s barely do.

|  | $$\tilde\phi$$ printed | Package | Innov. printed | Package |
|:---|---:|---:|---:|---:|
| Growth | −0.38 (1.34) | −0.27 | 0.37 (0.14) | 0.33 |
| Value | 2.16 (1.44) | <mark class="out">12.13</mark> | 0.30 (0.07) | <mark class="out">0.56</mark> |
| Market | 0.66 (1.20) | 0.72 | 0.58 (0.15) | 0.58 |

The ranking is what the model needs: value’s long-run loading exceeds growth’s.

![Figure 3](figures/figure3.svg)

<p class="caption">Figure 3. Spectrum of annual consumption growth. A peak at low frequency means some of the variation is persistent, which is what $$x_t$$ is for.</p>

![Figure 4](figures/figure4.svg)

<p class="caption">Figure 4. Three-year average dividend growth versus consumption. Value tracks consumption more closely (her correlation 0.52) than growth (0.25).</p>

> **Check.** Can you state, without looking up, (i) what the 6 percent *is*, (ii) why we are not allowed to feed it into calibration, and (iii) what $$\tilde\phi$$ measures that an average return does not?

[The long-run risks model]({% link model.md %}) turns these loadings into prices.
