---
title: Other risk premia
nav_order: 4
---

# Other risk premia
{: .no_toc }

1. TOC
{:toc}

Value is one pair. It is not the only CAPM failure.

Fama and French (2015) isolate three more in the same CRSP/Compustat universe: size, operating profitability, and investment. None of those average returns is an input to Table II. The question is the same question. Measure cash-flow loadings. Ask the Euler equation. Do the signs of $$\phi$$ and $$\mu$$ line up with both the premium and the price?

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

| Sort | `short=` | `long=` |
|:---|:---|:---|
| Size | big | small |
| Profitability | weak | robust |
| Investment | aggressive | conservative |
| Five-factor leftover | small-robust-conservative | small-weak-aggressive |

```python
from kiku_value_premium.calibration import calibrate_from_data
from kiku_value_premium.model import get_table_ii_params, solve_analytical, print_value_premium

dividends = calibrate_from_data(
    dc, frequency="annual", window=2,
    short=dd_big, long=dd_small, market=dd_market,
)
for name, d in dividends.items():
    print(name, d.mu, d.phi, d.phi_sigma, d.alpha)
params = get_table_ii_params()
params.dividends = dividends
print_value_premium(solve_analytical(params))
```

Compare `long.phi` to `short.phi` and `long.mu` to `short.mu` before you read the premium. Construction and the Size-OP-Inv leftover: [further.html]({{ '/further.html' | relative_url }}).
