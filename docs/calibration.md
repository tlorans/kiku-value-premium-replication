---
title: Calibration
nav_order: 5
---

# Calibration of the Model
{: .no_toc }

{: .here }
The machine is written. Now we pick numbers. Only consumption and dividend *dynamics* are allowed as targets. Average returns are not.

**In a nutshell.** We choose preference and cash-flow numbers so that *consumption and dividends* look like the 1930–2003 sample. We do not choose them so that the value premium equals 6 percent. The premium is supposed to fall out later.

{: .idea }
A weather model is useful only if you fit it to temperature and humidity, then *ask* it whether it will rain. If you also fit it to rainfall, you have not tested the rain forecast. Here, temperature is consumption growth, humidity is dividend growth, and rain is the value premium. Matching rain by hand would assume the puzzle away.

{: .why }
If you fit $$\phi$$ to match average returns, you have assumed the puzzle away. Kiku’s discipline is the opposite: match how cash flows move with consumption, then *ask* the Euler equation what returns must be.

1. TOC
{:toc}

## What is being chosen (and what is not)

The investor’s decision interval is one month. Table II is the default used throughout the replica.

What we **are** matching: mean and persistence of consumption growth, how long a shift in $$x_t$$ lasts, how volatile dividends are, and how much each portfolio’s dividends load on slow consumption.

What we **are not** matching: mean returns, the 6 percent value premium, Sharpe ratios, or CAPM betas. Those are the exam, on the next page.

|  |  | Meaning |
|:---|---:|:---|
| $$\delta$$ | 0.999 | patience (how much next month counts) |
| $$\gamma$$ | 10 | risk aversion (the “bumpy ride” knob) |
| $$\psi$$ | 1.5 | IES (the “willing to wait” knob) |
| $$\mu_c$$ | 0.0015 | mean monthly consumption growth |
| $$\rho$$ | 0.98 | how long a shift in $$x_t$$ lasts |
| $$\varphi_x$$ | 0.032 | size of shocks to $$x$$ |
| $$\sigma$$ | 0.0064 | typical consumption vol |
| $$\nu$$ | 0.99 | persistence of variance |
| $$\sigma_w$$ | 0.0000017 | shocks to variance |

Dividends (bottom panel of Table II):

|  | $$\mu$$ | $$\phi$$ | $$\varphi_\sigma$$ | $$\alpha$$ |
|:---|---:|---:|---:|---:|
| Growth | 0.0009 | 2.6 | 8.4 | 0.27 |
| Value | 0.0019 | 6.2 | 7.4 | 0.15 |
| Market | 0.0012 | 2.8 | 7.5 | 0.55 |

Residual correlations of orthogonalized dividend shocks: GV 0.20, GM 0.80, VM 0.45. Those help match Table V (how dividend growth comoves across portfolios), not Table VII (mean returns).

```python
from kiku_value_premium.calibration import get_table_ii_dividends
from kiku_value_premium.model import get_table_ii_params
get_table_ii_dividends()["value"].phi  # 6.2
get_table_ii_params().cons.rho         # 0.98
```

## Equation (19): from annual evidence to monthly $$\phi$$

This is the worked example for the one number that does the cross-sectional work.

**Problem.** The solver wants a monthly loading $$\phi$$ of dividend growth on $$x_t$$. The data give annual dividends and annual consumption. We never observe $$x_t$$ directly.

**What we know.** Section 2 estimated an *annual* regression of dividend growth on a two-year average of past consumption:

$$
\Delta d_t=d_0+\tilde\phi\sum_{k=1}^{2}\Delta c_{t-k}+\varepsilon_t.
$$

Printed $$\tilde\phi$$: growth $$-0.38$$ (1.34), value $$2.16$$ (1.44), market $$0.66$$ (1.20). Value’s slope is larger. That coefficient is a check, not the monthly input.

**Approach.** She picks monthly $$\phi$$ so that, when the model is simulated monthly and time-averaged the same way as the data, the *simulated* (19) matches the data check. Table II’s 6.2 / 2.6 / 2.8 are those monthly numbers. The paper replica never puts OLS $$\tilde\phi$$ into `ModelSolver`; it puts her Table II values.

**What would change.** If we set $$\phi_{\text{value}}$$ so that the model’s mean value return equalled 13.88 percent, the next page would no longer be a test. It would be a restatement of the target.

`calibrate_from_data` on a *new* cross-section is a first-pass helper. It does the same four cash-flow steps and nothing else:

1. $$\mu=\mathrm{mean}(\Delta d)$$ (divide by 12 if the series is annual)
2. $$\phi$$ from (19) — here the annual slope is used as the starting loading
3. $$\alpha$$ from corr((19) residual, AR(1) consumption innovation)
4. $$\varphi_\sigma$$ from residual vol / consumption-innovation vol (fallback 7.5)

There is no returns argument. That is the discipline, not an omission.

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

## Tables III–V: did the “weather” look right?

She draws 1000 samples of $$74\times 12$$ months, aggregates to annual, and reports the mean and cross-simulation SD of each statistic. This is the humidity-and-temperature check: if simulated consumption and dividends do not look like 1930–2003, we should not trust the rain forecast on the next page.

Consumption:

|  | Data | Model |
|:---|---:|---:|
| E[Δc] % | 1.96 (0.32) | 1.86 (0.64) |
| σ(Δc) % | 2.20 (0.45) | 2.16 (0.48) |
| AC(1) | 0.44 (0.12) | 0.43 (0.12) |
| AC(2) | 0.16 (0.15) | 0.20 (0.15) |

Table IV: value dividend growth is higher on average and more volatile; the market’s $$\Delta d$$ correlates more with $$\Delta c$$ (0.57) than value (0.38) or growth (0.33). Table V model Δd correlations: GV 0.31, GM 0.80, VM 0.50.

{: .package }
`simulate_cashflow_moments` returns `consumption["E[dc]"]` and `dividends[name]["E[dd]"]` (and vols, AC1, corr with $$\Delta c$$). Examples use 20 simulations; her tables use 1000. Tests only require simulated mean consumption growth between 1 and 3 percent per year.

> **Check.** What would go wrong if we chose $$\phi_{\text{value}}$$ so that the model’s mean value return equalled 13.88 percent? What *is* allowed as a target?

[Asset pricing implications]({% link implications.md %}) are the out-of-sample part: premia and P/D after cash flows are locked.
