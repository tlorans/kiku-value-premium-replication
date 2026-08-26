---
layout: default
title: Calibration
---

# Section 4 – Calibration

## What she does

Calibration uses **cash-flow moments only**. Return premia never enter. Table II is the default used to price claims.

Equation (19) estimates long-run leverage \(\tilde\phi\) by OLS of dividend growth on a two-year moving average of lagged consumption growth. Residual correlation with the consumption innovation identifies \(\alpha\). `calibrate_from_data` sets \(\varphi_\sigma\) to the ratio of that residual's volatility to consumption-innovation volatility (same frequency as the input series; falls back to 7.5 if the consumption innovation is degenerate).

She then simulates the joint consumption–dividend process: 1000 monthly samples of \(74\times 12\) observations, time-averaged to annual, and reports means and cross-simulation SDs as in Tables III–V.

## What you call

```python
from kiku_value_premium.calibration import (
    estimate_long_run_leverage,
    calibrate_from_data,
    get_table_ii_dividends,
    simulate_cashflow_moments,
)
from kiku_value_premium.model import get_table_ii_params, ModelParams

# Exact paper dividends (Table II bottom panel)
dividends = get_table_ii_dividends()
assert dividends["value"].phi == 6.2
assert dividends["growth"].phi == 2.6

# Same recipe on any cash-flow series — no returns argument
dividends = calibrate_from_data(
    dc,
    {"growth": dd_growth, "value": dd_value},
    frequency="annual",
    window=2,
)
phi = estimate_long_run_leverage(dc, dd_value, window=2)

params = get_table_ii_params()
print(simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=params))
```

`calibrate_from_data(dc, dd_by_name, frequency="annual", window=2)` has no argument for returns or premia. Plug the resulting `DividendParams` into `ModelParams` and keep Table II preferences and consumption if you want her pricing kernel.

The paper’s Monte Carlo is `n_sims=1000`. `examples/run_paper.py` uses 20 so it finishes.

## What you should see

`simulate_cashflow_moments` returns nested keys `consumption["E[dc]"]`, `consumption["sigma(dc)"]`, `consumption["AC1"]`, and `dividends[name]["E[dd]"]` / `"sigma(dd)"` / `"AC1"` / `"corr(dc,dd)"` for `growth`, `value`, and `market`.

Simulated E[Δc] sits in a 1–3% annual range. Value dividend growth is more volatile than growth’s; market tracks consumption more closely than value does. Those are the model-column rankings of Tables III–V, not the empirical SE gate.

Table II \(\phi\) ranking is value 6.2 > market 2.8 > growth 2.6 — the same ranking that produces the value premium in Section 5.
