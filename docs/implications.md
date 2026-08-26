---
layout: default
title: Asset Pricing Implications
---

# Section 5 – Asset Pricing Implications

## What she does

Once the Euler equations are solved, she reads asset-pricing moments off the stationary distribution of the Markov chain, integrating the short-run innovation with the same Gauss–Hermite quadrature. Tables VII–X report expected returns, volatilities, mean \(\log(P/D)\), the risk-free rate, Sharpe ratios, CAPM and C-CAPM betas (Table VIII is \(\beta_V/\beta_G\)), and return correlations (Table IX).

Figure 5 is the model-implied analogue of Figure 2 on a long simulated sample (her 1000 annual observations): the expected value premium projected on lagged P/D and Δd, plotted against a rescaled 3-year moving average of squared AR(1) consumption residuals.

The mechanism is differential long-run leverage. Value’s higher \(\phi\) raises its elasticity to \(x_t\) and therefore its long-run risk premium; growth is cheaper in expected-return space and richer in \(\log(P/D)\). CAPM betas do not explain the spread.

## What you call

```python
from kiku_value_premium.model import get_table_ii_params, ModelSolver, solve_analytical
from kiku_value_premium.implications import (
    compute_asset_pricing_moments,
    print_asset_pricing_moments,
    figure_lr_premium,
    figure_mean_pd,
    figure5,
)

params = get_table_ii_params()
# Paper default is n_x=30; examples/run_paper.py uses 15 so it finishes.
solver = ModelSolver(params, n_x=30, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))

figure_lr_premium("docs/figures/lr_premium_decomposition.svg")
figure_mean_pd(solver, "docs/figures/mean_log_pd.svg")
figure5("docs/figures/figure5.svg")
```

`solve_analytical(params)` is the fast Section 3.4 decomposition behind `figure_lr_premium`.

## What you should see

Paper model column (Tables VII–X):

| Quantity | Paper (model) |
|----------|----------------|
| Value premium | 5.3% |
| E[R] Growth / Value / Market | 6.1 / 11.4 / 7.5% |
| log(P/D) Growth / Value / Market | 3.65 / 3.10 / 3.24 |
| log-PD Value − Growth | ≈ −0.55 |
| CAPM \(\beta_V/\beta_G\) | < 1 |

The package recovers the ranking: expected returns value > market > growth, value \(\log(P/D)\) < growth in the Section 3.4 linearization, and \(\beta_V/\beta_G<1\) (CAPM failure).

![Long-run risk premium decomposition](figures/lr_premium_decomposition.svg)

*Analytical long-run risk premia. The spread is the \(\phi_V=6.2\) versus \(\phi_G=2.6\) channel amplified by \(\rho=0.98\) and the Epstein–Zin price of long-run risk.*

![Mean log(P/D) ranking](figures/mean_log_pd.svg)

*Mean log price–dividend ratios at the Section 3.4 linearization points: value 3.10 < market 3.24 < growth 3.65.*

![Figure 5. Model-implied expected value premium](figures/figure5.svg)

*Figure 5. Model analogue of Figure 2: expected value premium versus rescaled consumption uncertainty on a long simulated sample.*
