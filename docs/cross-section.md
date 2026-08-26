---
title: Cross section
nav_order: 3
---

# Cross section
{: .no_toc }

1. TOC
{:toc}

Evaluations of long-run risks usually stop at the market. Cochrane (2017) lists the model among competing accounts of the equity premium and of time-varying risk-bearing capacity. The same IMRS implies a ranking across claims. A dividend stream that loads more on $$x_t$$ covaries more with the priced long-run shock. That column is often overlooked. Book-to-market is treated as a factor literature, not as heterogeneous cash-flow leverage in the Bansal–Yaron investor.

The first pair is value versus growth. They have market betas near one. They do not have the same loading $$\phi$$ on $$x_t$$. I measure that gap in dividends, not in returns, give the [time-series]({% link time-series.md %}) investor those two claims, and read expected returns and price–dividend ratios off the Euler equation. The six-percent premium is a fact to be explained. It is not a calibration target. If it appears after the cash-flow step, it is a prediction.

## Facts, 1930–2003

I form five book-to-market quintiles at the end of June, NYSE breakpoints, NYSE–AMEX–NASDAQ ordinary shares, as in Fama and French (1993). Growth is the bottom quintile, value the top. Dividends are Campbell–Shiller series from CRSP `ret` and `retx`. The sample is 1930–2003.

|  | E[R] % | σ(R) % | E[log P/D] |
|:---|---:|---:|---:|
| Growth | 7.81 (1.98) | 20.2 | 3.61 (0.18) |
| Value | 13.88 (1.74) | 29.9 | 3.25 (0.12) |
| Market | 8.56 (1.79) | 20.1 | 3.34 (0.13) |

Value earned about six percent more per year than growth. Value sold cheaper relative to current dividends. Both CAPM betas sit near 1.03. The first fact is not a CAPM fact. Over seventy-four years the value-minus-growth return was positive about seventy percent of the time.

Value dividend growth is higher on average (3.63 percent against 0.68) and more volatile. Dividend growth comoves much less across the two claims than returns do. Prices share a discount-rate factor that dividends do not.

```python
from kiku_value_premium.empirical import START, END, build_annual_panel, table_i
bm = build_annual_panel(refresh=False)
print(table_i(bm, START, END))
```

## Cash-flow exposure

If consumption growth were i.i.d., its spectrum would be flat. It is not: mass sits near frequency zero. When past consumption has been high for two years, do this year’s dividends rise, and by how much?

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2} \Delta c_{t-k} + \varepsilon_t. \tag{19}
$$

Printed $$\tilde\phi$$: growth $$-0.38$$ (1.34), value $$2.16$$ (1.44), market $$0.66$$ (1.20). Value’s dividends move with the slow part of consumption; growth’s barely do. Three-year average dividend growth tracks consumption at 0.52 for value and 0.25 for growth.

$$\tilde\phi$$ is an annual slope. It is not the monthly $$\phi$$ that enters the solver. The ranking is what the model needs.

```python
from kiku_value_premium.calibration import estimate_long_run_leverage
print(estimate_long_run_leverage(dc, dd_value, window=2))
print(estimate_long_run_leverage(dc, dd_growth, window=2))
```

## Heterogeneous loadings

The investor and the consumption process stay those of the time-series page. Value and growth are the same machine except for four numbers,

$$
\Delta d_{t+1}=\mu+\phi x_t+\varphi\sigma_t u_{t+1},\qquad \alpha=\mathrm{Corr}(\eta,u).
$$

Table II: $$\phi_V=6.2$$, $$\phi_G=2.6$$; $$\mu_V=0.0019$$, $$\mu_G=0.0009$$. I give value the larger $$\phi$$ because the annual slope in (19) is larger, not because value had a larger average return. Monthly $$\phi$$ is chosen so that the model, simulated and time-aggregated as the data are, reproduces that ranking. The OLS slope is never passed to the solver.

$$\phi$$ raises the long-run premium and lowers $$\log(P/D)$$. $$\mu$$ raises $$\log(P/D)$$ and barely moves the premium. In this sort both loadings are larger on value, and $$\phi$$ wins the valuation ranking: value is still the cheap claim.

```python
from kiku_value_premium.calibration import calibrate_from_data
from kiku_value_premium.model import get_table_ii_params

dividends = calibrate_from_data(
    dc, frequency="annual", window=2,
    long=dd_value, short=dd_growth, market=dd_market,
)
for name, d in dividends.items():
    print(name, d.mu, d.phi, d.phi_sigma, d.alpha)
params = get_table_ii_params()
params.dividends["value"].phi   # 6.2 at Table II
params.dividends["growth"].phi  # 2.6
```

There is no argument for returns.

## What the Euler equation produces

Cash-flow parameters locked, I ask for prices. Table VII, value and growth:

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Growth | 7.81 (1.98) | 6.07 (2.91) | 3.61 (0.18) | 3.65 (0.06) |
| Value | 13.88 (1.74) | 11.36 (4.30) | 3.25 (0.12) | 3.10 (0.15) |

Model value premium about 5.3 percent against about 6 percent in the data. Sharpe ratios 0.34 versus 0.20. Mean P/D about 24.7 on value versus 39.8 on growth. Return volatilities: data 20.2 / 29.9; model 21.5 / 29.0.

Value is both the high-return claim and the low price–dividend claim. That pair is what leverage on $$x_t$$ is supposed to deliver.

A larger $$\phi$$ is not a larger CAPM beta. The model-implied ratio of value to growth CAPM betas is 0.92; for consumption betas, 0.85. Value’s market beta is *lower* than growth’s, as in the data. The priced risk is exposure to $$x_t$$.

```python
from kiku_value_premium.model import get_table_ii_params, ModelSolver, solve_analytical, print_value_premium
from kiku_value_premium.implications import compute_asset_pricing_moments, print_asset_pricing_moments

params = get_table_ii_params()
print_value_premium(solve_analytical(params))
solver = ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))
```

## What would count as failure

- Value’s expected return below growth’s, or a negligible gap.
- Value’s price–dividend ratio *above* growth’s.
- Value’s CAPM beta much larger than growth’s, so that market covariance would have been enough.

The paper avoids all three. A reversal on $$\phi$$ would mean the sort is not a long-run cash-flow sort. A reversal on $$\mu$$, with $$\phi$$ intact, would mean the model can match the premium and will miss the price.

The same investor, the same four loadings, and a different characteristic are [other risk premia]({% link further.md %}). Climate adds two states and is a different page.
