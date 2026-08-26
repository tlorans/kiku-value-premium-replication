---
layout: default
title: Generalizing the Recipe
---

# Generalizing the Recipe beyond Value / Growth

Kiku’s methodology is deliberately modular. The same six steps work for **any** cross-section once you supply the cash-flow series.

## Typical use cases

- Industry portfolios
- Climate-exposure sorts (temperature, transition, physical risk)
- Quality, profitability, investment, or any characteristic-sorted portfolios
- Country or regional equity portfolios

## Exact workflow

1. **Obtain data**  
   Aggregate consumption growth `dc` and a dictionary of portfolio cash-flow growth series `{name: dd}`.

2. **Calibrate long-run leverages only** (never use return premia)
   ```python
   from kiku_value_premium.calibration import calibrate_from_data
   dividends = calibrate_from_data(dc, dd_dict, frequency="annual", window=2)
   ```
   This implements Kiku’s equation (19) – the OLS of dividend growth on a moving average of lagged consumption growth. The resulting `phi` is the long-run leverage of each portfolio.

3. **Keep the aggregate consumption process and Epstein–Zin preferences**
   ```python
   from kiku_value_premium.params import get_default_params
   params = get_default_params()
   params.dividends = dividends
   ```

4. **Solve**
   ```python
   from kiku_value_premium.solver import ModelSolver
   solver = ModelSolver(params)
   solver.solve()
   ```

5. **Read the cross-sectional risk premia and valuations**
   ```python
   from kiku_value_premium.moments import compute_asset_pricing_moments
   moments = compute_asset_pricing_moments(solver)
   ```

The ranking of the estimated `phi`s becomes the ranking of long-run risk premia. Portfolios with higher long-run leverage command higher expected returns and lower price–dividend ratios – exactly as value stocks do in the original paper.

## Climate / industry application notes

When the underlying model is extended with additional state variables (e.g. temperature anomaly, policy intensity), the same cash-flow projection / long-run leverage logic can be applied to those extra states. The package already isolates the pure consumption long-run risk channel; the extra climate states can be added later by extending the state grid and the Euler equations while re-using the calibrated `DividendParams`.

See `examples/calibrate_any_portfolio.py` and `examples/calibrate_from_real_data.py` for concrete starting points.
