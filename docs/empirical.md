---
title: Empirical Evidence
nav_order: 3
---

# Empirical Evidence: Value / Growth / Market
{: .no_toc }

Kiku’s Section 2. Sample 1930–2003. Growth is the bottom book-to-market quintile, value the top, market the CRSP value-weighted market.

{: .paper }
“One of the most robust features of financial data is the finding that value firms, on average, have higher returns than growth firms.” Over 74 years the value strategy delivered superior returns about 70 percent of the time. Growth offers about 8 percent, value about 14 percent; the value premium is about 6 percent.

1. TOC
{:toc}

## 2.1 Data construction

She forms five portfolios on a monthly basis as in Fama and French (1993), NYSE, AMEX, and NASDAQ ordinary shares, NYSE breakpoints, June formation. Book-to-market is book equity at the last fiscal year-end of the prior calendar year over December market equity of the prior year. Book equity is stockholders’ equity plus deferred taxes and investment tax credit minus preferred stock (redemption, then liquidation, then par). Compustat does not go back to 1930; the package uses the Davis–Fama–French Moody’s file through 1962.

Per-share dividends follow Campbell and Shiller (1988) and Bansal, Dittmar, and Lundblad (2005). Extract the dividend yield from CRSP returns with and without dividends, then

$$
D_{t+1}=y_{t+1}V_t,\qquad V_{t+1}=h_{t+1}V_t,\qquad V_0=100.
$$

Monthly returns and dividends are time-aggregated to calendar years and converted to real with the personal consumption deflator. Dividend growth is $$\Delta\log D$$. $$\log(P/D)$$ is end-of-year price over that year’s cumulative dividend. The real risk-free rate is the 90-day T-bill minus a 12-month moving average of inflation (CRSP). Consumption is real per-capita nondurables plus services (NIPA).

Table I uses Newey–West **8** lags. Table VI data-column standard errors use **4** lags. Figure 2 is **1952–2003**, as in her caption.

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

`START, END = 1930, 2003`. `refresh=True` hits WRDS. CI never does.

## 2.2 The value premium in the data

{: .paper }
Growth on average offers about 8 percent; value delivers about 14 percent. The CAPM cannot explain the spread: in her sample both market betas are virtually 1.03.

|  | E[R] % |  | σ(R) % |  | E[log P/D] |  |
|:---|---:|---:|---:|---:|---:|---:|
|  | Printed | Package | Printed | Package | Printed | Package |
| Growth | 7.81 (1.98) | 7.49 | 20.2 (2.00) | 20.0 | 3.61 (0.18) | 3.62 |
| Value | 13.88 (1.74) | 13.67 | 29.9 (4.34) | 29.7 | 3.25 (0.12) | 3.34 |
| Market | 8.56 (1.79) | 8.52 | 20.1 (2.23) | 20.1 | 3.34 (0.13) | 3.33 |

Printed cells are Newey–West 8-lag standard errors. Package returns and $$\log(P/D)$$ sit inside those bands.

Return correlations (printed, then package): GV 0.75 (0.05) / 0.72; GM 0.95 (0.01) / 0.95; VM 0.87 (0.04) / 0.86.

![Figure 1](figures/figure1.svg)

<p class="caption">Figure 1. Spread in realized value-minus-growth returns, 1930–2003. Value is the highest book-to-market quintile of NYSE, AMEX, and NASDAQ; growth is the lowest. Returns are value-weighted, annual, real.</p>

## 2.3 Other phenomena of value and growth

{: .paper }
Value usually sells at prices that are low relative to current dividends: mean $$\log(P/D)$$ 3.25 versus 3.61 for growth (levels about 27.6 versus 43.2). Dividend-growth volatility is about 14 percent for growth and 18 percent for value. The correlation of dividend growth between the two is about 0.32, against 0.75 for returns.

|  | E[Δd] % |  | σ(Δd) % |  |
|:---|---:|---:|---:|---:|
|  | Printed | Package | Printed | Package |
| Growth | 0.68 (1.25) | 0.33 | 13.9 (2.24) | 14.3 |
| Value | 3.63 (3.06) | 3.53 | 18.1 (2.69) | <mark class="out">47.7</mark> |
| Market | 0.85 (0.95) | 0.92 | 10.9 (2.41) | 11.0 |

Δd correlations (printed / package): GV 0.32 (0.17) / 0.29; GM 0.80 (0.09) / 0.78; VM 0.53 (0.10) / <mark class="out">0.64</mark>.

{: .caution }
1933 Value is a genuine zero-dividend year: every month has `ret = retx`, so Campbell–Shiller $$D_t=0$$, and that year’s $$P/D$$ and $$\Delta d$$ are missing. The 1931–32 collapse and 1935–36 rebound then push Value $$\sigma(\Delta d)$$, the Value–Market $$\Delta d$$ correlation, Value $$\tilde\phi$$, and Value innovation correlation outside her printed SEs. Those four cells are ranking/sign checks. Printed goldens are not edited.

## 2.4 The market and the risk-free rate

{: .paper }
Average market return about 8.5 percent; short-term T-bill about 0.9 percent.

Package market E[R] is 8.52 percent (printed 8.56). Consumption growth, Table III:

|  | Printed | Package |
|:---|---:|---:|
| E[Δc] % | 1.96 (0.32) | 1.75 |
| σ(Δc) % | 2.20 (0.45) | 2.37 |
| AC(1) | 0.44 (0.12) | 0.41 |
| AC(2) | 0.16 (0.15) | 0.10 |

## 2.5 Time-varying premia

{: .paper }
The spread in expected compensations on value and growth displays countercyclical fluctuations, especially post-war. She constructs the expected value premium by projecting the realized value-minus-growth return on lagged price/dividend ratios and dividend growth of the two stocks, and plots it against a three-year moving average of squared residuals from an AR(1) fitted to consumption growth, rescaled to the premium’s mean and standard deviation. Sample in her Figure 2: 1952–2003. Post-war correlation with consumption uncertainty is about 40 percent.

![Figure 2](figures/figure2.svg)

<p class="caption">Figure 2. Expected value premium and consumption uncertainty, 1952–2003, her construction.</p>

## Low-frequency consumption and cash-flow exposures

{: .paper }
If consumption growth were i.i.d., its spectral density would be flat. Figure 3 plots an ARMA(1,1) spectrum and a Bartlett kernel estimate; both peak near frequency zero.

Equation (19) is the cash-flow check she uses in calibration:

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2} \Delta c_{t-k} + \varepsilon_t.
$$

Printed $$\tilde\phi$$: growth $$-0.38$$ (1.34), value $$2.16$$ (1.44), market $$0.66$$ (1.20). Innovation exposures (correlation of those residuals with AR(1) consumption news): 0.37, 0.30, 0.58.

|  | $$\tilde\phi$$ printed | Package | Innov. printed | Package |
|:---|---:|---:|---:|---:|
| Growth | −0.38 (1.34) | −0.27 | 0.37 (0.14) | 0.33 |
| Value | 2.16 (1.44) | <mark class="out">12.13</mark> | 0.30 (0.07) | <mark class="out">0.56</mark> |
| Market | 0.66 (1.20) | 0.72 | 0.58 (0.15) | 0.58 |

Ranking is preserved: value’s long-run loading exceeds growth’s.

![Figure 3](figures/figure3.svg)

<p class="caption">Figure 3. Spectral density of annual consumption growth, 1930–2003. ARMA(1,1) and Bartlett kernel.</p>

![Figure 4](figures/figure4.svg)

<p class="caption">Figure 4. Three-year moving average of dividend growth versus rescaled consumption growth. Her correlations: 0.25 (growth) and 0.52 (value).</p>

Next: [The long-run risks model]({% link model.md %}).
