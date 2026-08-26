---
title: Asset Pricing Implications
nav_order: 6
---

# Asset Pricing Implications
{: .no_toc }

{: .here }
Cash flows are locked. This page is the exam: we ask the Euler equation what returns and price–dividend ratios *must* be. We are not allowed to retune $$\phi$$ if the premium comes out wrong.

**In a nutshell.** If the story is right we should see a large value premium, a *lower* P/D for value, and CAPM betas that still fail.

{: .idea }
You trained the weather model on temperature and humidity. Now you open the window. Success is not “we got some numbers.” Success is three things together: (1) value still pays more than growth, by about the right amount; (2) value still looks cheap relative to its current harvest; (3) the usual market-beta ranking still fails, because the risk we priced was climate, not co-movement with the market.

{: .why }
This is the test, not another calibration. Section 4 never saw mean returns. If Table VII’s model column is close to the data, the premium is coming from differential $$\phi$$ and Epstein–Zin prices of $$x_t$$, not from having fitted 6 percent directly.

1. TOC
{:toc}

## What would count as failure

- Value’s expected return below growth’s, or a tiny gap.
- Value’s P/D *above* growth’s (the model would then miss the “cheap” half of the fact).
- Value’s CAPM beta much larger than growth’s, so that a CAPM person could say “we did not need long-run risk.”

The paper claims it avoids all three.

## How moments are read off the grid

The solver gives log price–dividend $$z$$ at each state $$(x,\sigma^2)$$. The Markov chain has a stationary distribution — how often the climate sits in each bin. Average the one-period returns implied by $$z$$ under that distribution, integrating the short-run shock with the same Gauss–Hermite rule as the Euler loop. That is Table VII’s *model* column (mean and SD across 1000 simulated 74-year histories in the paper).

```python
from kiku_value_premium.model import get_table_ii_params, ModelSolver
from kiku_value_premium.implications import (
    compute_asset_pricing_moments, print_asset_pricing_moments,
    figure_lr_premium, figure_mean_pd, figure5,
)

params = get_table_ii_params()
solver = ModelSolver(params, n_x=30, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))
```

`solve_analytical` is the Section 3.4 shortcut used for the long-run premium figure. On a tiny $$5\times 2$$ grid the Euler map floors numerical $$\log(P/D)$$; the published mean-P/D figure uses the linearization points 3.65 / 3.10 / 3.24.

## Expected returns and valuations (Table VII)

{: .paper }
“I show that the model goes a long way towards resolving the value premium puzzle — it quantitatively replicates the observed magnitude of the value premium and, at the same time, accommodates the empirical failure of the CAPM and C-CAPM.” Model value premium about 5.3 percent versus about 6 percent in the data. Sharpe ratios 0.34 versus 0.20. Mean P/D about 24.7 (value) versus 39.8 (growth).

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Growth | 7.81 (1.98) | 6.07 (2.91) | 3.61 (0.18) | 3.65 (0.06) |
| Value | 13.88 (1.74) | 11.36 (4.30) | 3.25 (0.12) | 3.10 (0.15) |
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

Return volatilities: data 20.2 / 29.9 / 20.1; model 21.5 / 29.0 / 20.1. The package recovers the ranking: expected returns value above market above growth, and $$\log(P/D)$$ value below market below growth.

Value is both the high-return claim *and* the expensive-looking-cheap claim (low P/D). That pair is what leverage on $$x_t$$ is supposed to deliver.

## CAPM and C-CAPM still fail (Table VIII)

{: .why }
A skeptic’s last move is “value just has a higher market beta.” In the data it does not. The model must fail the CAPM *for the same reason*: the risk being priced is exposure to $$x_t$$, which is not the same object as covariance with the market portfolio.

The model-implied ratio of value to growth CAPM betas is 0.92; for consumption betas, 0.85. Value’s market beta is *lower* than growth’s, as in the data. A larger $$\phi$$ is not the same object as a larger CAPM beta. The package asserts $$\beta_V/\beta_G<1$$ on the solved grid.

## Return correlations (Table IX)

Printed: GV 0.75 (0.05), GM 0.95 (0.01), VM 0.87 (0.04). Model: 0.44, 0.82, 0.60. She notes the model undershoots the value–growth return correlation. Table X is return predictability on $$\log(P/D)$$ at 1- and 5-year horizons (not a separate object in the package).

## The long-run channel, isolated

Before trusting the 30×4 grid, look at the linearization. Value’s larger $$\phi$$ raises $$A_1$$ in (11) and therefore compensation for $$\epsilon$$-news in (14). That is the mechanism, stripped of short-run noise.

![Long-run risk premia](figures/lr_premium_decomposition.svg)

<p class="caption">Figure. Analytical long-run premia. The gap is $$\phi_V=6.2$$ versus $$\phi_G=2.6$$, scaled up by $$\rho=0.98$$ and the Epstein–Zin price of long-run news. This is not yet the 5.3 percent in Table VII; it is why that number is not a mystery.</p>

![Mean log(P/D)](figures/mean_log_pd.svg)

<p class="caption">Section 3.4 points: growth 3.65, market 3.24, value 3.10. Value is cheaper per unit of current dividend because more of its cash-flow risk is long-run risk.</p>

## Does the model also move the *expected* premium? (Figure 5)

Figure 2 in the data said the expected value premium rises with consumption uncertainty. Figure 5 runs the same construction on 1000 simulated annual observations. If the model’s $$\sigma_t^2$$ and $$\phi$$ gap are doing real work, the two series should still comove.

![Figure 5](figures/figure5.svg)

<p class="caption">Figure 5. Model analogue of Figure 2. The expected value premium still lines up with consumption uncertainty on simulated histories.</p>

> **Check.** Name two numbers the model is *not* allowed to target, and two numbers it *is* supposed to get approximately right after calibration. Why is a *lower* model CAPM beta on value a success rather than a problem?
