---
title: Value versus growth
nav_order: 5
---

# Value versus growth
{: .no_toc }

1. TOC
{:toc}

**Question.** Why do cheap stocks (high book-to-market, *value*) earn more than expensive stocks (low book-to-market, *growth*) when both move about one-for-one with the market?

The last page priced one claim. This page prices two, with the same household. Kiku (2006) is the worked example. The six-percent gap in average returns is a fact to be explained. It is not a number you feed the calibrator.

## Data

Each June, sort ordinary shares on NYSE, AMEX, and NASDAQ by book-to-market, using NYSE cutoffs (Fama and French 1993). Growth is the bottom fifth. Value is the top fifth. Dividends are inferred from the gap between the return with dividends and the return without dividends (Campbell and Shiller). Sample: 1930–2003.

|  | E[R] % | σ(R) % | E[log P/D] |
|:---|---:|---:|---:|
| Growth | 7.81 (1.98) | 20.2 | 3.61 (0.18) |
| Value | 13.88 (1.74) | 29.9 | 3.25 (0.12) |
| Market | 8.56 (1.79) | 20.1 | 3.34 (0.13) |

Value earned about six percent more per year. Value was cheaper (3.25 against 3.61). Both CAPM betas sit near 1.03, so the return gap is not a market-beta fact.

```python
import lrrcs as lrr

bm = lrr.build_annual_panel(refresh=False)
print(lrr.table_i(bm))
```

![Figure 1](figures/figure1.svg)

<p class="caption">Figure 1. Realized value minus growth, 1930–2003. The bars are positive in most years.</p>

## Calibrate cash flows

The household and the consumption process stay those of [the market]({{ '/time-series.html' | relative_url }}). Each claim differs only in four cash-flow numbers: mean dividend growth $$\mu$$, monthly loading $$\phi$$ on $$x_t$$, residual scale $$\varphi$$, and short-run correlation $$\alpha$$.

The data give an *annual* slope of dividend growth on two lags of consumption, equation (19). Printed $$\tilde\phi$$: growth $$-0.38$$ (1.34), value $$2.16$$ (1.44), market $$0.66$$ (1.20). That ranking is the check. The solver wants monthly $$\phi$$. Table II: $$\phi_{\text{value}}=6.2$$, $$\phi_{\text{growth}}=2.6$$. Value gets the larger $$\phi$$ because (19) said so, not because value had a larger average return. The annual slope never enters the solver as a number.

```python
import lrrcs as lrr

dividends = lrr.calibrate_from_data(
    dc, frequency="annual", window=2,
    long=dd_value, short=dd_growth, market=dd_market,
)
params = lrr.get_table_ii_params()
params.dividends["value"].phi   # 6.2 at Table II
params.dividends["growth"].phi  # 2.6
```

There is no argument for returns.

## Solve

Same preferences as the market pass. `solve_analytical` and `ModelSolver` resolve either pair. The market key remains the time-series check on this calibration.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
lrr.print_long_short_premium(lrr.solve_analytical(params))
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
```

## Compare pricing moments

With those four numbers locked, what expected returns and price–dividend ratios does the Euler equation assign?

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Growth | 7.81 (1.98) | 6.07 (2.91) | 3.61 (0.18) | 3.65 (0.06) |
| Value | 13.88 (1.74) | 11.36 (4.30) | 3.25 (0.12) | 3.10 (0.15) |
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

The model gap is about 5.3 percent against about 6 percent in the data. Mean price–dividend levels are about 24.7 on value versus 39.8 on growth. Value is both the high-return claim and the low price–dividend claim. The market row is the time-series check that the same investor still prices the aggregate claim.

Do not confuse $$\phi$$ with a CAPM beta. The model’s ratio of value to growth CAPM betas is 0.92. Value’s market beta is *lower*, as in the data. The priced risk is exposure to $$x_t$$.

Failure would be: value earns less than growth; value’s price–dividend ratio sits above growth’s; or value’s CAPM beta is much larger, so covariance with the market would have been enough.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
lrr.print_asset_pricing_moments(lrr.compute_asset_pricing_moments(solver))
```

![Long-run risk premia](figures/lr_premium_decomposition.svg)

<p class="caption">Analytical long-run premia. The gap is $$\phi_V=6.2$$ versus $$\phi_G=2.6$$, scaled by $$\rho=0.98$$ and the Epstein–Zin price of long-run news.</p>
