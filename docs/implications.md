---
title: Asset Pricing Implications
nav_order: 6
---

# Asset Pricing Implications
{: .no_toc }

Kiku’s Section 5. Once cash-flow dynamics are calibrated, the model has to speak to expected returns, valuations, volatilities, Sharpe ratios, the failure of the CAPM and C-CAPM, return correlations, and predictability.

{: .paper }
“I show that the model goes a long way towards resolving the value premium puzzle — it quantitatively replicates the observed magnitude of the value premium and, at the same time, accommodates the empirical failure of the CAPM and C-CAPM.” Model value premium about 5.3 percent versus about 6 percent in the data. Sharpe ratios 0.34 versus 0.20; $P/D$ 24.7 versus 39.8; return volatilities 20–30 percent; market premium about 6 percent with a low, stable risk-free rate.

1. TOC
{:toc}

## What the solver returns

Moments come from the stationary distribution of the solved Markov chain, integrating the short-run innovation with the same Gauss–Hermite rule used in the Euler loop.

```python
from kiku_value_premium.model import get_table_ii_params, ModelSolver, solve_analytical
from kiku_value_premium.implications import (
    compute_asset_pricing_moments, print_asset_pricing_moments,
    figure_lr_premium, figure_mean_pd, figure5,
)

params = get_table_ii_params()
solver = ModelSolver(params, n_x=30, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))
figure_lr_premium("docs/figures/lr_premium_decomposition.svg")
figure_mean_pd(solver, "docs/figures/mean_log_pd.svg")
figure5("docs/figures/figure5.svg")
```

`solve_analytical` is Section 3.4, used for the long-run premium figure. On a tiny $5\times 2$ grid the Euler map floors numerical $\log(P/D)$; the published mean-$\log(P/D)$ figure is the Section 3.4 linearization (3.65 / 3.10 / 3.24).

## Table VII — expected returns and valuations

Printed data versus her model column (Newey–West 8 lags on the data; model is mean and SD across 1000 simulated 74-year histories):

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Growth | 7.81 (1.98) | 6.07 (2.91) | 3.61 (0.18) | 3.65 (0.06) |
| Value | 13.88 (1.74) | 11.36 (4.30) | 3.25 (0.12) | 3.10 (0.15) |
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

σ(r): data 20.2 / 29.9 / 20.1; model 21.5 / 29.0 / 20.1. The package recovers the ranking E[R] value > market > growth and $\log(P/D)$ value < market < growth at the 3.4 points.

## Table VIII — CAPM / C-CAPM

{: .paper }
The model-implied ratio of value to growth CAPM betas is 0.92; for the C-CAPM, 0.85. Market and consumption betas of value stocks are, on average, *lower* than those of growth firms. The value premium is not a beta story in either traditional model.

The package asserts $\beta_V/\beta_G<1$ on the solved grid.

## Tables IX–X

Printed return correlations: GV 0.75 (0.05), GM 0.95 (0.01), VM 0.87 (0.04). Model: 0.44, 0.82, 0.60. She notes the model undershoots the value–growth return correlation. Table X (not rebuilt as a separate object here) is 1- and 5-year return predictability on $\log(P/D)$.

## The long-run channel

Value’s higher $\phi$ raises $A_1$ in (11) and therefore the compensation for $\epsilon$-news in (14). That is the mechanism she isolates before the numerical tables.

![Long-run risk premia](figures/lr_premium_decomposition.svg)

<p class="caption">Analytical long-run risk premia. The spread is $\phi_V=6.2$ versus $\phi_G=2.6$, amplified by $\rho=0.98$ and the Epstein–Zin price of long-run risk.</p>

![Mean log(P/D)](figures/mean_log_pd.svg)

<p class="caption">Section 3.4 linearization points: growth 3.65, market 3.24, value 3.10.</p>

## Figure 5 — model-implied expected value premium

{: .paper }
Figure 5 is Figure 2 run on 1000 annual observations simulated from the model: the expected value premium still comoves with consumption uncertainty.

![Figure 5](figures/figure5.svg)

<p class="caption">Figure 5. Model analogue of Figure 2 on a long simulated sample.</p>
