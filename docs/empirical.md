---
title: Empirical Evidence
nav_order: 3
---

# 2. Empirical Evidence
{: .no_toc }

{: .here }
Section 2 of Kiku (2006). I construct value, growth, and market claims and document their returns, valuations, and cash-flow exposure to consumption. The six-percent premium is a fact to be explained, not a parameter.

**In a nutshell.** Over 1930–2003 value earned about six percent more than growth, sold at a lower price–dividend ratio, and its dividends comoved more with slow consumption growth. Market betas of both portfolios are near one.

{: .idea }
The object of this section is a cash-flow fact: value dividends load more on low-frequency consumption than growth dividends do. That fact is admissible as a calibration target. The average-return gap is not.

{: .why }
If the six-percent premium were used to choose $$\phi$$, Section 5 would cease to be a test. I therefore record returns here and leave them unused until the Euler equation is solved.

1. TOC
{:toc}

## 2.1 Portfolio construction

I form five book-to-market quintiles at the end of June each year, following Fama and French (1993). Breakpoints are NYSE. The universe is NYSE, AMEX, and NASDAQ ordinary shares (`shrcd` in $$\{10,11\}$$). Growth is the bottom quintile, value the top quintile. The market is the CRSP value-weighted portfolio of ordinary shares.

Book-to-market is book equity at the last fiscal year-end of the prior calendar year divided by December market equity of the prior year. Compustat book equity does not reach 1930; through 1962 I use the Davis–Fama–French / Moody’s historical book-equity file.

Dividends are not Compustat cash items. CRSP reports a with-dividend return $$R$$ (`ret`) and a capital-gain return $$H$$ (`retx`). Campbell and Shiller (1988) and Bansal, Dittmar, and Lundblad (2005) convert that gap into a per-share dividend on a synthetic price index $$V$$:

$$
D_{t+1}=y_{t+1}V_t,\qquad V_{t+1}=H_{t+1}V_t,\qquad V_0=100,
$$

where $$y_{t+1}$$ is the dividend yield implied by $$R_{t+1}-H_{t+1}$$. I time-aggregate monthly returns and dividends to calendar years, deflate with the PCE deflator, and take $$\Delta d_t=\Delta\log D_t$$. Log price–dividend is year-end price over that year’s cumulative dividend. The real T-bill is the 90-day yield minus a twelve-month moving average of inflation. Consumption is real per-capita nondurables plus services.

The sample is 1930–2003. Table I uses Newey–West standard errors with eight lags. Table VI uses four. Figure 2 is 1952–2003, as in the paper caption.

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

`START, END = 1930, 2003`. `refresh=True` rebuilds the extracts from WRDS.

## 2.2 The value premium

{: .paper }
“One of the most robust features of financial data is the finding that value firms, on average, have higher returns than growth firms.” Over seventy-four years the value strategy won about seventy percent of the time.

|  | E[R] % |  | σ(R) % |  | E[log P/D] |  |
|:---|---:|---:|---:|---:|---:|---:|
|  | Printed | Package | Printed | Package | Printed | Package |
| Growth | 7.81 (1.98) | 7.49 | 20.2 (2.00) | 20.0 | 3.61 (0.18) | 3.62 |
| Value | 13.88 (1.74) | 13.67 | 29.9 (4.34) | 29.7 | 3.25 (0.12) | 3.34 |
| Market | 8.56 (1.79) | 8.52 | 20.1 (2.23) | 20.1 | 3.34 (0.13) | 3.33 |

Printed cells are Newey–West eight-lag standard errors. Package returns and $$\log(P/D)$$ sit inside those bands. In this sample both CAPM betas are about 1.03, so volatility of returns does not rescue the CAPM.

Return correlations (printed / package): GV 0.75 (0.05) / 0.72; GM 0.95 (0.01) / 0.95; VM 0.87 (0.04) / 0.86.

![Figure 1](figures/figure1.svg)

<p class="caption">Figure 1. Realized value minus growth, 1930–2003. The bars are positive in most years. The premium is a time-series object, not only a sample mean.</p>

## 2.3 Prices, dividend growth, and a tension

Value pays a higher average return and nonetheless sells cheaper relative to current dividends (mean $$\log(P/D)$$ 3.25 versus 3.61). That pair is consistent with value cash flows being riskier in a way the investor prices, or with lower expected growth. I measure the cash-flow side next.

|  | E[Δd] % |  | σ(Δd) % |  |
|:---|---:|---:|---:|---:|
|  | Printed | Package | Printed | Package |
| Growth | 0.68 (1.25) | 0.33 | 13.9 (2.24) | 14.3 |
| Value | 3.63 (3.06) | 3.53 | 18.1 (2.69) | <mark class="out">47.7</mark> |
| Market | 0.85 (0.95) | 0.92 | 10.9 (2.41) | 11.0 |

Δd correlations (printed / package): GV 0.32 (0.17) / 0.29; GM 0.80 (0.09) / 0.78; VM 0.53 (0.10) / <mark class="out">0.64</mark>. Dividend growth comoves much less than returns. Prices share a discount-rate factor that dividends do not.

{: .caution }
1933 Value is a genuine zero-dividend year: every month has `ret = retx`, so Campbell–Shiller $$D_t=0$$, and that year’s $$P/D$$ and $$\Delta d$$ are missing. The collapse and rebound around that year push Value $$\sigma(\Delta d)$$, the Value–Market $$\Delta d$$ correlation, Value $$\tilde\phi$$, and Value innovation correlation outside the printed standard errors. Those four cells are ranking and sign checks. Printed goldens are not edited.

## 2.4 The market, the T-bill, and consumption

The market earned about 8.5 percent; the real T-bill about 0.9 percent. Consumption growth is the quantity to which both the equity premium and the value premium must eventually be tied.

|  | Printed | Package |
|:---|---:|---:|
| E[Δc] % | 1.96 (0.32) | 1.75 |
| σ(Δc) % | 2.20 (0.45) | 2.37 |
| AC(1) | 0.44 (0.12) | 0.41 |
| AC(2) | 0.16 (0.15) | 0.10 |

Autocorrelation of consumption is not zero. A persistent expected-growth factor $$x_t$$ is already visible in the univariate consumption process.

## 2.5 Expected value premium and consumption uncertainty

If the extra return on value compensates for risk that worsens when consumption is harder to forecast, the *expected* value premium should rise with consumption uncertainty. I project realized value-minus-growth on lagged price–dividend ratios and dividend growth of the two portfolios, and plot the fitted series against a three-year average of squared AR(1) consumption residuals, rescaled to the premium’s mean and standard deviation. The window is 1952–2003. Post-war correlation is about forty percent.

![Figure 2](figures/figure2.svg)

<p class="caption">Figure 2. Expected value premium (solid) against consumption uncertainty (dashed), 1952–2003.</p>

## 2.6 Do value dividends track long-run consumption?

If consumption growth were i.i.d., its spectrum would be flat. Figure 3 is not flat: mass sits near frequency zero.

I then ask a simpler question. When past consumption has been high for two years, do this year’s dividends rise, and by how much?

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2} \Delta c_{t-k} + \varepsilon_t. \tag{19}
$$

$$\tilde\phi$$ is not the monthly $$\phi$$ that later enters the solver. It is an annual slope. Printed values: growth $$-0.38$$ (1.34), value $$2.16$$ (1.44), market $$0.66$$ (1.20). Value’s dividends move with the slow part of consumption; growth’s barely do.

|  | $$\tilde\phi$$ printed | Package | Innov. printed | Package |
|:---|---:|---:|---:|---:|
| Growth | −0.38 (1.34) | −0.27 | 0.37 (0.14) | 0.33 |
| Value | 2.16 (1.44) | <mark class="out">12.13</mark> | 0.30 (0.07) | <mark class="out">0.56</mark> |
| Market | 0.66 (1.20) | 0.72 | 0.58 (0.15) | 0.58 |

The ranking is what the model needs: value’s long-run loading exceeds growth’s. Section 4 converts that ranking into the monthly leverages of Table II. It does not put the OLS slope into the Euler loop.

![Figure 3](figures/figure3.svg)

<p class="caption">Figure 3. Spectrum of annual consumption growth, 1930–2003. Low-frequency mass is the empirical counterpart of $$x_t$$.</p>

![Figure 4](figures/figure4.svg)

<p class="caption">Figure 4. Three-year average dividend growth versus consumption. Value tracks consumption more closely (paper correlation 0.52) than growth (0.25).</p>

[Section 3]({% link model.md %}) turns these loadings into prices.
