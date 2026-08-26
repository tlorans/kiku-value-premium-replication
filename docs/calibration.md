---
title: 4. Calibration
parent: The replica
nav_order: 3
---

# 4. Calibration
{: .no_toc }

1. TOC
{:toc}

I choose preference and cash-flow parameters so that consumption and dividend dynamics match the 1930–2003 sample. Average returns are not targets.

Table II is the default used throughout the package. Monthly $$\phi$$ is chosen so that the model, simulated and time-aggregated as the data are, reproduces the annual projection (19). The OLS slope $$\tilde\phi$$ is never passed to the solver.

If $$\phi_V$$ is chosen so that the model mean value return equals 13.88 percent, [Section 5]({% link implications.md %}) is a restatement of the target, not a test.

## 4.1 What is chosen, and what is not

The investor’s decision interval is one month. Table II is the published calibration.

Matched: mean and persistence of consumption growth, persistence of $$x_t$$, dividend volatilities, and the loading of each portfolio’s dividends on slow consumption.

Not matched: mean returns, the six-percent value premium, Sharpe ratios, or CAPM betas. Those are read off in Section 5.

|  |  | Meaning |
|:---|---:|:---|
| $$\delta$$ | 0.999 | time discount |
| $$\gamma$$ | 10 | relative risk aversion |
| $$\psi$$ | 1.5 | elasticity of intertemporal substitution |
| $$\mu_c$$ | 0.0015 | mean monthly consumption growth |
| $$\rho$$ | 0.98 | persistence of $$x_t$$ |
| $$\varphi_x$$ | 0.032 | scale of shocks to $$x$$ |
| $$\sigma$$ | 0.0064 | unconditional consumption volatility |
| $$\nu$$ | 0.99 | persistence of variance |
| $$\sigma_w$$ | 0.0000017 | shocks to variance |

Dividends (bottom panel of Table II):

|  | $$\mu$$ | $$\phi$$ | $$\varphi_\sigma$$ | $$\alpha$$ |
|:---|---:|---:|---:|---:|
| Growth | 0.0009 | 2.6 | 8.4 | 0.27 |
| Value | 0.0019 | 6.2 | 7.4 | 0.15 |
| Market | 0.0012 | 2.8 | 7.5 | 0.55 |

Residual correlations of orthogonalized dividend shocks: GV 0.20, GM 0.80, VM 0.45. Those help match Table V (comovement of dividend growth), not Table VII (mean returns).

```python
from kiku_value_premium.calibration import get_table_ii_dividends
from kiku_value_premium.model import get_table_ii_params
get_table_ii_dividends()["value"].phi  # 6.2
get_table_ii_params().cons.rho         # 0.98
```

## 4.2 Equation (19) and monthly $$\phi$$

The solver wants a monthly loading $$\phi$$ of dividend growth on $$x_t$$. The data give annual dividends and annual consumption. $$x_t$$ is not observed.

Section 2 estimated the annual projection

$$
\Delta d_t=d_0+\tilde\phi\sum_{k=1}^{2}\Delta c_{t-k}+\varepsilon_t. \tag{19}
$$

Printed $$\tilde\phi$$: growth $$-0.38$$ (1.34), value $$2.16$$ (1.44), market $$0.66$$ (1.20). Value’s slope is larger. That coefficient is a check, not the monthly input.

I pick monthly $$\phi$$ so that, when the model is simulated monthly and time-averaged as the data are, the simulated (19) matches the data check. Table II’s 6.2 / 2.6 / 2.8 are those monthly numbers. The package never puts OLS $$\tilde\phi$$ into `ModelSolver`; it puts the Table II values.

`calibrate_from_data` on a new cross-section is a first-pass helper. It does four cash-flow steps and nothing else:

1. $$\mu=\mathrm{mean}(\Delta d)$$ (divide by 12 if the series is annual)
2. $$\phi$$ from (19) — here the annual slope is the starting loading
3. $$\alpha$$ from corr((19) residual, AR(1) consumption innovation)
4. $$\varphi_\sigma$$ from residual vol / consumption-innovation vol (fallback 7.5)

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

## 4.3 Tables III–V: cash-flow moments under the model

I draw 1000 samples of $$74\times 12$$ months, aggregate to annual, and report the mean and cross-simulation standard deviation of each statistic. If simulated consumption and dividends do not look like 1930–2003, the return predictions of Section 5 are not to be trusted.

Consumption:

|  | Data | Model |
|:---|---:|---:|
| E[Δc] % | 1.96 (0.32) | 1.86 (0.64) |
| σ(Δc) % | 2.20 (0.45) | 2.16 (0.48) |
| AC(1) | 0.44 (0.12) | 0.43 (0.12) |
| AC(2) | 0.16 (0.15) | 0.20 (0.15) |

Table IV: value dividend growth is higher on average and more volatile; the market’s $$\Delta d$$ correlates more with $$\Delta c$$ (0.57) than value (0.38) or growth (0.33). Table V model Δd correlations: GV 0.31, GM 0.80, VM 0.50.

{: .package }
`simulate_cashflow_moments` returns `consumption["E[dc]"]` and `dividends[name]["E[dd]"]` (and vols, AC1, corr with $$\Delta c$$). Examples use 20 simulations; the published tables use 1000. Tests require simulated mean consumption growth between 1 and 3 percent per year.

[Section 5]({% link implications.md %}) reads premia and valuations off the solved Euler equation.
