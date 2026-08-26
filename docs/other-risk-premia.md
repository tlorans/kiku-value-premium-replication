---
title: Other risk premia
nav_order: 4
---

# Other risk premia
{: .no_toc }

1. TOC
{:toc}

[Time series]({{ '/time-series.html' | relative_url }}) prices the market. [Cross section]({{ '/cross-section.html' | relative_url }}) prices value versus growth. Fama and French (2015) isolate three further CAPM failures in the same CRSP/Compustat universe: size, operating profitability, and investment. None of those premia is an input to Table II. I record the published moments and the mapping onto $$(\mu,\phi,\varphi,\alpha)$$. The test has not been run as a calibration target.

## Published moments

Table 2 of Fama and French (2015), monthly 2×3 factors, July 1963–December 2013.

|  | Mean | σ | $$t$$ |
|:---|---:|---:|---:|
| $$R_m-R_f$$ | 0.50 | 4.49 | 2.74 |
| SMB | 0.29 | 3.07 | 2.31 |
| HML | 0.37 | 2.88 | 3.20 |
| RMW | 0.25 | 2.14 | 2.92 |
| CMA | 0.33 | 2.01 | 4.07 |

Units are percent per month. Annualized, size is about three and a half percent, profitability about three, investment about four. HML’s intercept is absorbed once RMW and CMA are included. SMB’s is not. The five-factor leftover is the low average return on small stocks that invest a great deal despite low profitability ($$-0.47$$ percent per month, $$t=-5.89$$).

## Mapping

Preferences and aggregate consumption stay at Table II. Only the four cash-flow numbers change. Average returns do not enter.

| Loading | Estimated from | Effect on E$$[R]$$ | Effect on $$\log(P/D)$$ |
|:---|:---|:---|:---|
| $$\mu$$ | mean $$\Delta d$$ | negligible | rises with $$\mu$$ |
| $$\phi$$ | projection (19) of $$\Delta d$$ on lagged $$\Delta c$$ | rises with $$\phi$$ | falls with $$\phi$$ |
| $$\varphi$$ | residual dividend volatility | small | weak |
| $$\alpha$$ | residual correlation with consumption news | short-run | weak |

**Size.** Requires $$\phi_{\text{small}}>\phi_{\text{big}}$$. $$\mu$$ is not signed. A gap only in $$\varphi$$ is noise, not long-run risk. The leftover corner is a *low* return: a large estimated $$\phi$$ there is the wrong ranking.

**Profitability.** Requires $$\phi_{\text{robust}}>\phi_{\text{weak}}$$ and $$\mu_{\text{robust}}>\mu_{\text{weak}}$$ by enough to keep the robust claim expensive.

**Investment.** The value configuration: $$\phi_{\text{conservative}}>\phi_{\text{aggressive}}$$. A higher $$\mu$$ on the conservative leg is not required.

| Sort | `short=` | `long=` |
|:---|:---|:---|
| Size | big | small |
| Profitability | weak | robust |
| Investment | aggressive | conservative |
| Five-factor leftover | small-robust-conservative | small-weak-aggressive |

```python
from kiku_value_premium.calibration import calibrate_from_data, estimate_long_run_leverage
from kiku_value_premium.model import get_table_ii_params, ModelSolver, solve_analytical, print_value_premium
from kiku_value_premium.implications import compute_asset_pricing_moments, print_asset_pricing_moments

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

The long form of this page, including construction and the Size-OP-Inv leftover, is [further.html]({{ '/further.html' | relative_url }}).
