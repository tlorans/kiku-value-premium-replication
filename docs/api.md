---
title: API
parent: Package
nav_order: 2
---

# API

Public names live at the package root. Submodules (`lrrcs.model`, `lrrcs.empirical`, `lrrcs.calibration`, `lrrcs.implications`) exist for organization but are not the documented path. The division of labor mirrors the model's two halves: `calibrate_from_data` measures cash-flow exposures (the cash-flow side), `solve_analytical` and `compute_asset_pricing_moments` let the household price them (the discount-rate side), and the outputs are valuations and risk premia together.

```python
import numpy as np
import polars as pl
import tidyfinance as tf
import lrrcs as lrr
```

`market` is the time-series claim. `long` and `short` are the two legs of a sort. `value` / `growth` remain aliases. `print_long_short_premium` prints the spread.

| Object | Call |
|:---|:---|
| Book-to-market panel, 1930–2003 | `lrr.build_annual_panel` |
| Consumption, deflator, T-bill | `lrr.load_consumption`, `lrr.load_deflator`, `lrr.real_rf_from_monthly` |
| Campbell–Shiller dividends | `lrr.campbell_shiller_annual` |
| Table I / Table VI | `lrr.table_i`, `lrr.table_vi_data` |
| IMRS, dynamics, solver | `lrr.get_table_ii_params`, `lrr.ModelSolver`, `lrr.solve_analytical` |
| Expected growth \(x_t\) | `lrr.expected_growth_proxy`, `lrr.filter_expected_growth` |
| Cash-flow loadings | `lrr.calibrate_from_data` |
| Valuations and risk premia | `lrr.compute_asset_pricing_moments` |

`lrr.build_annual_panel` downloads CRSP/Compustat/CCM through the `tidyfinance` WRDS client, forms NYSE-breakpoint quintiles, builds Campbell–Shiller dividends, and splices historical book equity.

A new sort is the same loop as [Measuring leverage]({{ '/measuring-leverage.html' | relative_url }}): consumption and two dividend legs in, no returns.

```python
dc = pl.read_csv("data/consumption_annual.csv").sort("year")["dc"].to_numpy()
panel = pl.read_csv("data/annual_panel.csv")

def dd(claim):
    return (
        panel.filter(pl.col("claim") == claim)
        .sort("year")["dgrowth"]
        .to_numpy()
    )

div = lrr.calibrate_from_data(
    dc,
    frequency="annual",
    window=2,
    long=dd("Value"),
    short=dd("Growth"),
    market=dd("Market"),
)
lrr.print_calibration_summary(div)
```

`lrr.calibrate_from_data(..., long=..., short=..., market=...)` takes consumption growth and the two legs. There is no argument for returns — by design, so the Euler equation stays a test.

```python
lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

Missing WRDS credentials raise `EmpiricalDataError` with a message to call `tf.set_wrds_credentials()`.
