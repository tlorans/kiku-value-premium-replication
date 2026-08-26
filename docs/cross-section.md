---
title: Cross section
nav_order: 3
---

# Cross section
{: .no_toc }

1. TOC
{:toc}

The last page priced one claim. This page prices two.

Value and growth have market betas near one. They do not have the same loading on $$x_t$$. Measure that loading in dividends. Do not use returns. Feed the two claims to the [time-series]({{ '/time-series.html' | relative_url }}) investor. Read expected returns and price–dividend ratios off the Euler equation.

The six-percent premium is a fact. It is not a target. If it shows up after the cash-flow step, it is a prediction. Put it in the cash-flow step and you have assumed the answer.

## Facts, 1930–2003

Five book-to-market quintiles, end of June, NYSE breakpoints, NYSE–AMEX–NASDAQ ordinary shares, Fama and French (1993). Growth is the bottom quintile. Value is the top. Dividends are Campbell–Shiller series from CRSP `ret` and `retx`.

|  | E[R] % | σ(R) % | E[log P/D] |
|:---|---:|---:|---:|
| Growth | 7.81 (1.98) | 20.2 | 3.61 (0.18) |
| Value | 13.88 (1.74) | 29.9 | 3.25 (0.12) |
| Market | 8.56 (1.79) | 20.1 | 3.34 (0.13) |

Six percent a year. Value is cheaper. Both CAPM betas sit near 1.03. So the first fact is not a CAPM fact. The value-minus-growth return was positive in about seventy percent of those seventy-four years.

Value dividend growth is higher (3.63 percent against 0.68) and more volatile. Dividend growth comoves much less across the two claims than returns do. Prices share a discount-rate factor that dividends do not. That is the Shiller point, inside the sort.

```python
from kiku_value_premium.empirical import START, END, build_annual_panel, table_i
bm = build_annual_panel(refresh=False)
print(table_i(bm, START, END))
```

## Cash-flow exposure

If consumption growth were i.i.d., its spectrum would be flat. It is not. Mass sits near frequency zero. Simple question: when past consumption has been high for two years, do this year’s dividends rise?

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2} \Delta c_{t-k} + \varepsilon_t. \tag{19}
$$

Printed $$\tilde\phi$$: growth $$-0.38$$ (1.34), value $$2.16$$ (1.44), market $$0.66$$ (1.20). Value moves with the slow part of consumption. Growth does not. Three-year average dividend growth tracks consumption at 0.52 for value and 0.25 for growth.

$$\tilde\phi$$ is an annual slope. It is not the monthly $$\phi$$ in the solver. The ranking is what matters.

```python
from kiku_value_premium.calibration import estimate_long_run_leverage
print(estimate_long_run_leverage(dc, dd_value, window=2))
print(estimate_long_run_leverage(dc, dd_growth, window=2))
```

## Heterogeneous loadings

Same investor. Same consumption process. Four numbers differ.

$$
\Delta d_{t+1}=\mu+\phi x_t+\varphi\sigma_t u_{t+1},\qquad \alpha=\mathrm{Corr}(\eta,u).
$$

Table II: $$\phi_V=6.2$$, $$\phi_G=2.6$$; $$\mu_V=0.0019$$, $$\mu_G=0.0009$$. Value gets the larger $$\phi$$ because (19) said so, not because value had a larger average return. The OLS slope never enters the solver.

$$\phi$$ raises the premium and lowers $$\log(P/D)$$. $$\mu$$ raises $$\log(P/D)$$ and barely moves the premium. In this sort both are larger on value. $$\phi$$ wins the valuation ranking. Value stays cheap.

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

No argument for returns.

## What the Euler equation produces

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Growth | 7.81 (1.98) | 6.07 (2.91) | 3.61 (0.18) | 3.65 (0.06) |
| Value | 13.88 (1.74) | 11.36 (4.30) | 3.25 (0.12) | 3.10 (0.15) |

About 5.3 percent against about 6 percent. Sharpe ratios 0.34 versus 0.20. Mean P/D about 24.7 on value versus 39.8 on growth. Return volatilities: data 20.2 / 29.9; model 21.5 / 29.0.

High return and low price together. That is what leverage on $$x_t$$ is supposed to do.

Do not confuse $$\phi$$ with a CAPM beta. The model-implied ratio of value to growth CAPM betas is 0.92. For consumption betas, 0.85. Value’s market beta is *lower*, as in the data. The priced risk is exposure to $$x_t$$.

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

Value earns less than growth, or the gap is noise. Value’s price–dividend ratio sits *above* growth’s. Value’s CAPM beta is much larger, so the market would have been enough.

The paper avoids all three. Reverse $$\phi$$ and the sort is not a long-run cash-flow sort. Reverse $$\mu$$ with $$\phi$$ intact and you can match the premium while missing the price.

Same investor, different characteristic: [other risk premia]({{ '/other-risk-premia.html' | relative_url }}). Climate adds two states.
