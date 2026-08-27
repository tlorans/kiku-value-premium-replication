---
title: Other risk premia
nav_order: 4
---

# Other risk premia
{: .no_toc }

1. TOC
{:toc}

Value versus growth is one pair. It is not the only pair whose average returns the CAPM — a model that prices only covariance with the market — cannot explain.

**Question.** Can the same household, with the same consumption process, rank other pairs that also beat the CAPM?

**What is measured.** The same four cash-flow numbers as on the cross-section page: mean dividend growth $$\mu$$, loading on the persistent consumption factor $$\phi$$, residual dividend scale $$\varphi$$, and residual correlation with consumption news $$\alpha$$. Average returns do not enter.

**What this page does not claim.** That the test has been passed. It states the published facts and what the signs of $$\mu$$ and $$\phi$$ would have to be.

## Characteristic sorts

Fama and French (2015) stay in the same CRSP/Compustat files. They keep size (market equity at the end of June) and add two accounting ratios.

- *Operating profitability* — last year’s sales minus costs, over book equity. Robust means high. Weak means low.
- *Investment* — last year’s growth in total assets. Conservative means slow. Aggressive means fast.

They form 2-by-3 sorts on size and each characteristic and average the corners into four traded factors.

- SMB — small minus big.
- HML — high book-to-market minus low (value minus growth).
- RMW — robust profitability minus weak.
- CMA — conservative investment minus aggressive.

Table 2 of that paper. Monthly returns, July 1963–December 2013.

|  | Mean | σ | $$t$$ |
|:---|---:|---:|---:|
| Market minus safe rate | 0.50 | 4.49 | 2.74 |
| SMB | 0.29 | 3.07 | 2.31 |
| HML | 0.37 | 2.88 | 3.20 |
| RMW | 0.25 | 2.14 | 2.92 |
| CMA | 0.33 | 2.01 | 4.07 |

**How to read it.** Units are percent per month. The $$t$$ column asks whether the mean is distinguishable from zero. Annualized, size is about three and a half percent, profitability about three, investment about four. Smaller than the 1930–2003 value gap. Still not CAPM facts: the high-return legs are not simply the high-market-beta legs.

A regression of each factor on the other four absorbs HML once RMW and CMA are included. SMB’s intercept stays. The observation the five-factor model cannot price is specific: small firms that invest a lot despite low profitability, $$-0.47$$ percent per month ($$t=-5.89$$).

Do not treat HML, RMW, and CMA as three independent mysteries. The identity price = expected discounted cash flows already ties the expected return to book-to-market, expected profits, and expected investment. Size is the leftover.

## Industry portfolios

A *characteristic sort* picks the long and short legs by a number you computed — book-to-market, profits, asset growth. An *industry portfolio* does not. Ken French assigns each ordinary share to an industry from its SIC code (the four-digit industry classifier on Compustat, or CRSP when Compustat is missing), value-weights inside the industry, and posts 5, 10, 12, 17, 30, and 48 portfolios. Fama and French (1997) used them as industry costs of equity. Later papers use them as *test assets*: claims that were not sorted on the same characteristics the factors were built from.

**Why they belong here.** A model that prices HML because HML was the sort can still fail on tobacco versus utilities. Average-return gaps across industries are smaller and less stable than HML. Cash-flow gaps are not. Durable goods, energy, and manufacturing move with the cycle. Food, utilities, and health care do not. Bansal, Dittmar, and Lundblad (2005) already measured how industry dividends load on consumption and found that those loadings line up with average returns. That is the long-run risks prediction, stated in cash flows.

**How to pick the legs.** Do not pick `long=` and `short=` by which industry earned more. Run equation (19) from the cross-section page — dividend growth on two years of lagged consumption growth — on each industry. The high-$$\tilde\phi$$ industry is the long-run-risk claim. Then ask whether that claim also earned more, and whether $$\mu$$ matches the price–dividend ranking.

If the high-$$\phi$$ industry is expensive and high-$$\mu$$, and the return gap is small, the model can match the price and will not invent a large premium. That is a success — provided the Euler equation does not then demand a premium the data do not have.

Twelve industries is a first pass. Thirty or forty-eight is the usual grid. Dividends are still inferred from returns with and without dividends, as on the cross-section page.

## What each loading does

Same household. Same consumption process. Four numbers.

| Loading | Measured from | Effect on average return | Effect on $$\log(P/D)$$ |
|:---|:---|:---|:---|
| $$\mu$$ | mean dividend growth | almost nothing | rises |
| $$\phi$$ | slope of dividends on lagged consumption | rises | falls |
| $$\varphi$$ | leftover dividend volatility | little | little |
| $$\alpha$$ | leftover correlation with consumption news | short-run only | little |

**Size.** Need $$\phi_{\text{small}}>\phi_{\text{big}}$$. $$\mu$$ is not signed in advance. A gap only in $$\varphi$$ is noise, not long-run risk. The leftover corner is a *low* return. A large $$\phi$$ there is the wrong ranking.

**Profitability.** Need both. $$\phi_{\text{robust}}>\phi_{\text{weak}}$$ or there is no premium. $$\mu_{\text{robust}}>\mu_{\text{weak}}$$ by enough that the high-return claim stays expensive. Copy value’s $$\phi$$ gap onto profitability and you will get the premium and the wrong price.

**Investment.** Looks like value. Need $$\phi_{\text{conservative}}>\phi_{\text{aggressive}}$$. A higher $$\mu$$ on the conservative leg is not required.

**Industry.** There is no named premium. Rank industries by estimated $$\phi$$. Expected returns should rank the same way. Log price–dividend ratios should rank the opposite way unless $$\mu$$ offsets. A cyclical industry with large $$\phi$$ and low $$\mu$$ should look like value. A defensive industry with small $$\phi$$ and high $$\mu$$ should look like growth. If $$\phi$$ is flat across industries, industry is not a long-run-risk cross-section. If $$\phi$$ ranks and average returns do not, either this household cannot be reused or the sample is too short to see the premium the loadings imply.

| Sort | `short=` | `long=` |
|:---|:---|:---|
| Size | big | small |
| Profitability | weak | robust |
| Investment | aggressive | conservative |
| Five-factor leftover | small, robust, conservative | small, weak, aggressive |
| Industry | low $$\tilde\phi$$ industry | high $$\tilde\phi$$ industry |

```python
import lrrcs as lrr

phis = {
    name: lrr.estimate_long_run_leverage(dc, dd, window=2)
    for name, dd in industry_dividends.items()
}
lo, hi = min(phis, key=phis.get), max(phis, key=phis.get)

dividends = lrr.calibrate_from_data(
    dc, frequency="annual", window=2,
    short=industry_dividends[lo],
    long=industry_dividends[hi],
    market=dd_market,
)
for name, d in dividends.items():
    print(name, d.mu, d.phi, d.phi_sigma, d.alpha)
params = lrr.get_table_ii_params()
params.dividends = dividends
lrr.print_long_short_premium(lrr.solve_analytical(params))
```

Read `long.phi` against `short.phi` and `long.mu` against `short.mu` before you read the printed spread. Construction detail: [further.html]({{ '/further.html' | relative_url }}).

## References

Fama, E., and K. French. 1993. “Common Risk Factors in the Returns on Stocks and Bonds.” *Journal of Financial Economics* 33 (1): 3–56.

Fama, E., and K. French. 1997. “Industry Costs of Equity.” *Journal of Financial Economics* 43 (2): 153–193.

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Bansal, R., R. Dittmar, and C. Lundblad. 2005. “Consumption, Dividends, and the Cross Section of Equity Returns.” *Journal of Finance* 60 (4): 1639–1672.

Novy-Marx, R. 2013. “The Other Side of Value: The Gross Profitability Premium.” *Journal of Financial Economics* 108 (1): 1–28.
