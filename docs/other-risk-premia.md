---
title: Other risk premia
nav_order: 4
---

# Other risk premia
{: .no_toc }

1. TOC
{:toc}

Value is one pair. It is not the only CAPM failure.

Fama and French (2015) isolate three more in the same CRSP/Compustat universe: size, operating profitability, and investment. Fama and French also publish industry portfolios — 5, 10, 12, 17, 30, 48 — from the same files. Industries are not a long–short factor. They are a cross-section of claims with different cash-flow processes. None of those average returns is an input to Table II.

The question is the same question. Measure cash-flow loadings. Ask the Euler equation. Do the signs of $$\phi$$ and $$\mu$$ line up with both the premium and the price?

This page states the facts and the mapping. It does not claim the test has been passed.

## The facts

Table 2 of Fama and French (2015). Monthly 2×3 factors, July 1963–December 2013.

|  | Mean | σ | $$t$$ |
|:---|---:|---:|---:|
| $$R_m-R_f$$ | 0.50 | 4.49 | 2.74 |
| SMB | 0.29 | 3.07 | 2.31 |
| HML | 0.37 | 2.88 | 3.20 |
| RMW | 0.25 | 2.14 | 2.92 |
| CMA | 0.33 | 2.01 | 4.07 |

Percent per month. Annualized: size about three and a half, profitability about three, investment about four. Smaller than the 1930–2003 value gap. Still not CAPM facts.

HML’s intercept disappears once RMW and CMA are in the regression. SMB’s does not. The leftover the five-factor model cannot price is specific: small stocks that invest a lot despite low profitability, $$-0.47$$ percent per month ($$t=-5.89$$).

Do not treat HML, RMW, and CMA as three independent mysteries. The dividend-discount identity already ties expected return to book-to-market, expected profitability, and expected investment. Size is the leftover.

## Industries

Characteristic sorts pick the long and short legs by the characteristic. Industry portfolios do not. Ken French assigns each NYSE–AMEX–NASDAQ ordinary share to an industry from Compustat SIC (and CRSP SIC when Compustat is missing), value-weights inside the industry, and leaves the portfolios on the website. Fama and French (1997) used them to talk about industry costs of equity. Asset-pricing papers use them as test assets because they are not sorted on the same characteristics the factors were built from.

That is the point. A model that prices HML because HML was the sort can still fail on Smoke versus Utilities. Average-return gaps across industries are smaller and less stable than HML. Cash-flow gaps are not. Durable goods, energy, and manufacturing move with the cycle. Food, utilities, and health care do not. Bansal, Dittmar, and Lundblad (2005) already measured consumption cash-flow betas on industry portfolios and found that those betas line up with average returns. That is the long-run risks prediction, stated in cash flows.

Do not pick `long=` and `short=` by which industry earned more. Pick them after equation (19). The high-$$\tilde\phi$$ industry is the long-run-risk claim. Then ask whether that claim also earned more, and whether $$\mu$$ matches the valuation ranking. If the high-$$\phi$$ industry is the expensive, high-$$\mu$$ industry and the premium is small, the model can match the price and will not manufacture a large premium. That is a success, not a failure — provided the Euler equation does not then demand a premium the data do not have.

Twelve industries is enough for a first pass. Thirty or forty-eight is the usual test-asset grid. Dividends are still Campbell–Shiller, built from the industry return series with and without dividends on French’s site, or from CRSP inside each SIC bucket as in Section 2.

## What to look at

Same investor. Same consumption process. Four numbers.

| Loading | From | Premium | $$\log(P/D)$$ |
|:---|:---|:---|:---|
| $$\mu$$ | mean $$\Delta d$$ | almost nothing | rises |
| $$\phi$$ | slope (19) on lagged $$\Delta c$$ | rises | falls |
| $$\varphi$$ | residual dividend vol | little | little |
| $$\alpha$$ | residual correlation with consumption news | short-run | little |

**Size.** You need $$\phi_{\text{small}}>\phi_{\text{big}}$$. $$\mu$$ is not signed. A gap only in $$\varphi$$ is noise. The leftover corner is a *low* return. A large $$\phi$$ there is the wrong ranking.

**Profitability.** You need both. $$\phi_{\text{robust}}>\phi_{\text{weak}}$$ or there is no premium. $$\mu_{\text{robust}}>\mu_{\text{weak}}$$ by enough that the high-return claim stays expensive. Relabel value and rerun Table II and you will get the premium and the wrong price.

**Investment.** Looks like value. $$\phi_{\text{conservative}}>\phi_{\text{aggressive}}$$. A higher $$\mu$$ on the conservative leg is not required.

**Industry.** There is no named premium. Rank industries by estimated $$\phi$$. The Euler equation must then rank expected returns the same way, and rank $$\log(P/D)$$ the opposite way unless $$\mu$$ offsets. A cyclical industry with large $$\phi$$ and low $$\mu$$ should look like value. A defensive industry with small $$\phi$$ and high $$\mu$$ should look like growth. If $$\phi$$ is flat across industries, industry is not a long-run-risk cross-section. If $$\phi$$ ranks and average returns do not, the investor of Table II cannot be recycled — or the sample is too short to see the premium the loadings imply.

| Sort | `short=` | `long=` |
|:---|:---|:---|
| Size | big | small |
| Profitability | weak | robust |
| Investment | aggressive | conservative |
| Five-factor leftover | small-robust-conservative | small-weak-aggressive |
| Industry | low $$\tilde\phi$$ industry | high $$\tilde\phi$$ industry |

```python
from kiku_value_premium.calibration import calibrate_from_data, estimate_long_run_leverage
from kiku_value_premium.model import get_table_ii_params, solve_analytical, print_value_premium

# Industry dividends: Campbell-Shiller from French industry returns
# with and without dividends, or CRSP inside each SIC bucket.
phis = {
    name: estimate_long_run_leverage(dc, dd, window=2)
    for name, dd in industry_dividends.items()
}
lo, hi = min(phis, key=phis.get), max(phis, key=phis.get)

dividends = calibrate_from_data(
    dc, frequency="annual", window=2,
    short=industry_dividends[lo],
    long=industry_dividends[hi],
    market=dd_market,
)
for name, d in dividends.items():
    print(name, d.mu, d.phi, d.phi_sigma, d.alpha)
params = get_table_ii_params()
params.dividends = dividends
print_value_premium(solve_analytical(params))
```

Compare `long.phi` to `short.phi` and `long.mu` to `short.mu` before you read the premium. Construction and the Size-OP-Inv leftover: [further.html]({{ '/further.html' | relative_url }}).

## References

Fama, E., and K. French. 1993. “Common Risk Factors in the Returns on Stocks and Bonds.” *Journal of Financial Economics* 33 (1): 3–56.

Fama, E., and K. French. 1997. “Industry Costs of Equity.” *Journal of Financial Economics* 43 (2): 153–193.

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Bansal, R., R. Dittmar, and C. Lundblad. 2005. “Consumption, Dividends, and the Cross Section of Equity Returns.” *Journal of Finance* 60 (4): 1639–1672.

Novy-Marx, R. 2013. “The Other Side of Value: The Gross Profitability Premium.” *Journal of Financial Economics* 108 (1): 1–28.
