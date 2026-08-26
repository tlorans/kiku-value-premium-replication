---
title: Calibration
nav_order: 5
---

# Calibration of the Model
{: .no_toc }

Kiku’s Section 4. The discipline is the whole paper: match time-series cash-flow moments, then *read* returns and valuations off the model. Premia never enter the calibration.

1. TOC
{:toc}

## Table II

Preferences and consumption are monthly. Decision interval of the investor is one month.

|  |  |  |
|:---|---:|---:|
| $$\delta$$ | 0.999 | time discount |
| $$\gamma$$ | 10 | risk aversion |
| $$\psi$$ | 1.5 | IES |
| $$\mu_c$$ | 0.0015 | mean consumption growth |
| $$\rho$$ | 0.98 | persistence of $$x_t$$ |
| $$\varphi_x$$ | 0.032 | vol of expected-growth shocks |
| $$\sigma$$ | 0.0064 | mean consumption vol |
| $$\nu$$ | 0.99 | persistence of variance |
| $$\sigma_w$$ | 0.0000017 | vol of variance shocks |

Dividend processes (bottom panel of Table II):

|  | $$\mu$$ | $$\phi$$ | $$\varphi_\sigma$$ | $$\alpha$$ |
|:---|---:|---:|---:|---:|
| Growth | 0.0009 | 2.6 | 8.4 | 0.27 |
| Value | 0.0019 | 6.2 | 7.4 | 0.15 |
| Market | 0.0012 | 2.8 | 7.5 | 0.55 |

Residual correlations of orthogonalized dividend shocks: GV 0.20, GM 0.80, VM 0.45.

```python
from kiku_value_premium.calibration import get_table_ii_dividends
from kiku_value_premium.model import get_table_ii_params
get_table_ii_dividends()["value"].phi  # 6.2
get_table_ii_params().cons.rho         # 0.98
```

## Equation (19)

{: .paper }
She estimates long-run leverage from the data by projecting dividend growth on a two-year moving average of lagged consumption, “in order to capture risks related to low-frequency (rather than short-term) fluctuations in consumption.”

$$
\Delta d_t=d_0+\tilde\phi\sum_{k=1}^{2}\Delta c_{t-k}+\varepsilon_t.
$$

Printed $$\tilde\phi$$: growth $$-0.38$$ (1.34), value $$2.16$$ (1.44), market $$0.66$$ (1.20). She then picks monthly $$\phi$$ so that the *model*, simulated and time-averaged the same way, matches that check. Table II’s 6.2 / 2.6 / 2.8 are those monthly loadings, not the OLS coefficients themselves. The package never puts OLS $$\tilde\phi$$ into the solver.

`calibrate_from_data` on an arbitrary cross-section:

1. $$\mu=\mathrm{mean}(\Delta d)$$ (divided by 12 if the series is annual)
2. $$\phi$$ from (19)
3. $$\alpha$$ from the correlation of (19) residuals with an AR(1) consumption innovation
4. $$\varphi_\sigma$$ from the ratio of residual volatility to consumption-innovation volatility (fallback 7.5 if that scale is degenerate)

There is no returns argument.

```python
from kiku_value_premium.calibration import (
    estimate_long_run_leverage, calibrate_from_data, simulate_cashflow_moments,
)
from kiku_value_premium.model import get_table_ii_params

phi = estimate_long_run_leverage(dc, dd_value, window=2)
dividends = calibrate_from_data(
    dc, {"growth": dd_growth, "value": dd_value, "market": dd_market},
    frequency="annual", window=2,
)
print(simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=get_table_ii_params()))
```

## Tables III–V

She reports means and cross-simulation standard deviations across 1000 samples of $$74\times 12$$ months, aggregated to annual. Paper data versus model for consumption:

|  | Data | Model |
|:---|---:|---:|
| E[Δc] % | 1.96 (0.32) | 1.86 (0.64) |
| σ(Δc) % | 2.20 (0.45) | 2.16 (0.48) |
| AC(1) | 0.44 (0.12) | 0.43 (0.12) |
| AC(2) | 0.16 (0.15) | 0.20 (0.15) |

Dividend-growth model column (Table IV): value mean growth higher than growth’s, value more volatile, market more correlated with $$\Delta c$$ (0.57) than value (0.38) or growth (0.33). Table V model Δd correlations: GV 0.31, GM 0.80, VM 0.50.

{: .package }
`simulate_cashflow_moments` returns `consumption["E[dc]"]`, `"sigma(dc)"`, `"AC1"`, and `dividends[name]["E[dd]"]` / `"sigma(dd)"` / `"AC1"` / `"corr(dc,dd)"`. The default in examples is 20 simulations so a laptop finishes; her table is 1000. Tests only require simulated E[Δc] in a 1–3 percent annual range. Those are model-column rankings, not the empirical SE gate.

Next: [Asset pricing implications]({% link implications.md %}).
