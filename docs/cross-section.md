---
title: Cross section
nav_order: 3
---

# Cross section
{: .no_toc }

1. TOC
{:toc}

The last page priced one claim. This page prices two.

**Question.** Why do cheap stocks (high book-to-market, *value*) earn more than expensive stocks (low book-to-market, *growth*) when both move about one-for-one with the market?

**What is measured.** How each portfolio’s *dividends* move with past consumption. Not how their *returns* move with the market.

**What is asked next.** Give those two dividend processes to the household of the [time-series]({{ '/time-series.html' | relative_url }}) page. Read the Euler equation — expected discount factor times return equals one — for expected returns and for log price–dividend ratios.

The six-percent gap in average returns is a fact to be explained. It is not a number you feed the calibrator. If it appears after the cash-flow step, it is a prediction. Put it in the cash-flow step and you have assumed the answer.

## The facts to be explained

Each June, sort ordinary shares on NYSE, AMEX, and NASDAQ by book-to-market, using NYSE cutoffs so the bins are not dominated by tiny firms (Fama and French 1993). Growth is the cheapest fifth of that ratio. Value is the dearest fifth. Dividends are inferred from the gap between the return *with* dividends and the return *without* dividends (Campbell and Shiller). Sample: 1930–2003.

|  | E[R] % | σ(R) % | E[log P/D] |
|:---|---:|---:|---:|
| Growth | 7.81 (1.98) | 20.2 | 3.61 (0.18) |
| Value | 13.88 (1.74) | 29.9 | 3.25 (0.12) |
| Market | 8.56 (1.79) | 20.1 | 3.34 (0.13) |

**How to read it.** E[R] is average annual return. σ(R) is the standard deviation of that return. E[log P/D] is the average log price–dividend ratio — a high number means a rich price relative to this year’s dividend.

**Result in the data.** Value earned about six percent more per year. Value was cheaper (3.25 against 3.61). Both CAPM betas — slopes of the portfolio return on the market return — sit near 1.03. So the return gap is not a market-beta fact. The value-minus-growth return was positive in about seventy percent of those seventy-four years.

Value dividend growth is higher (3.63 percent against 0.68) and more volatile. Dividend growth comoves much less across the two claims than returns do. Prices share a discount-rate factor that dividends do not.

```python
from lrrcs.empirical import START, END, build_annual_panel, table_i
bm = build_annual_panel(refresh=False)
print(table_i(bm, START, END))
```

## Measuring exposure to slow consumption

If consumption growth were independent from year to year, its spectrum would be flat. It is not. Mass sits at low frequencies: expected growth today depends on expected growth yesterday.

**Question.** When consumption has been high for the last two years, do this year’s dividends rise, and by how much?

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2} \Delta c_{t-k} + \varepsilon_t. \tag{19}
$$

$$\Delta d_t$$ is log dividend growth. $$\Delta c$$ is log consumption growth. $$\tilde\phi$$ is an *annual* slope. It is not the monthly leverage $$\phi$$ that the solver uses. The ranking of $$\tilde\phi$$ across claims is what the solver needs.

**Result.** Printed $$\tilde\phi$$: growth $$-0.38$$ (1.34), value $$2.16$$ (1.44), market $$0.66$$ (1.20). Value’s dividends move with the slow part of consumption. Growth’s do not. Three-year average dividend growth tracks consumption at 0.52 for value and 0.25 for growth.

```python
from lrrcs.calibration import estimate_long_run_leverage
print(estimate_long_run_leverage(dc, dd_value, window=2))
print(estimate_long_run_leverage(dc, dd_growth, window=2))
```

## Four numbers per claim

The household and the consumption process stay those of the time-series page. Each claim is the same machine except for four cash-flow numbers.

- $$\mu$$ — mean dividend growth. Raises the price–dividend ratio. Barely moves the expected return.
- $$\phi$$ — monthly loading on $$x_t$$. Raises the expected return. Lowers the price–dividend ratio.
- $$\varphi$$ — scale of the residual dividend shock. Mostly return volatility.
- $$\alpha$$ — correlation of that residual with the consumption surprise. A short-run premium, priced at $$\gamma$$.

$$
\Delta d_{t+1}=\mu+\phi x_t+\varphi\sigma_t u_{t+1},\qquad \alpha=\mathrm{Corr}(\eta,u).
$$

Table II: $$\phi_{\text{value}}=6.2$$, $$\phi_{\text{growth}}=2.6$$; $$\mu_{\text{value}}=0.0019$$, $$\mu_{\text{growth}}=0.0009$$. Value gets the larger $$\phi$$ because (19) said so, not because value had a larger average return. The annual slope $$\tilde\phi$$ never enters the solver as a number.

In this sort both $$\mu$$ and $$\phi$$ are larger on value. $$\phi$$ wins the valuation ranking: value stays cheap.

```python
from lrrcs.calibration import calibrate_from_data
from lrrcs.model import get_table_ii_params

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

## The pricing test

**Question.** With those four numbers locked, what expected returns and price–dividend ratios does the Euler equation assign?

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Growth | 7.81 (1.98) | 6.07 (2.91) | 3.61 (0.18) | 3.65 (0.06) |
| Value | 13.88 (1.74) | 11.36 (4.30) | 3.25 (0.12) | 3.10 (0.15) |

**Result.** The model gap is about 5.3 percent against about 6 percent in the data. Sharpe ratios — average excess return over return volatility — are 0.34 versus 0.20. Mean price–dividend levels are about 24.7 on value versus 39.8 on growth. Return volatilities: data 20.2 / 29.9; model 21.5 / 29.0.

High return and low price together. That is what extra loading on $$x_t$$ is supposed to do.

Do not confuse $$\phi$$ with a CAPM beta. The model’s ratio of value to growth CAPM betas is 0.92. For consumption betas — slopes on consumption growth — 0.85. Value’s market beta is *lower*, as in the data. The priced risk is exposure to $$x_t$$, not to the market return.

```python
from lrrcs.model import get_table_ii_params, ModelSolver, solve_analytical, print_long_short_premium
from lrrcs.implications import compute_asset_pricing_moments, print_asset_pricing_moments

params = get_table_ii_params()
print_long_short_premium(solve_analytical(params))
solver = ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))
```

## What would count as failure

- Value earns less than growth, or the gap is noise.
- Value’s price–dividend ratio sits *above* growth’s.
- Value’s CAPM beta is much larger, so covariance with the market would have been enough.

The paper avoids all three. Reverse the $$\phi$$ ranking and the sort is not a long-run cash-flow sort. Reverse the $$\mu$$ ranking with $$\phi$$ intact and you can match the premium while missing the price.

Same household, different characteristic: [other risk premia]({{ '/other-risk-premia.html' | relative_url }}).
