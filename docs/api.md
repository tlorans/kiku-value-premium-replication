---
title: API
parent: Package
nav_order: 2
---

# API

```python
import tidyfinance as tf
import lrrcs as lrr
```

Public names live at the package root. Submodules (`lrrcs.model`, `lrrcs.empirical`, `lrrcs.calibration`, `lrrcs.implications`) exist for organization but are not the documented path.

`market` is the time-series claim. `long` and `short` are the two legs of a sort. `value` / `growth` remain aliases. `print_long_short_premium` prints the spread.

| Object | Call |
|:---|:---|
| Book-to-market panel, 1930–2003 | `lrr.build_annual_panel` |
| Table I / Table VI | `lrr.table_i`, `lrr.table_vi_data` |
| IMRS, dynamics, solver | `lrr.get_table_ii_params`, `lrr.ModelSolver`, `lrr.solve_analytical` |
| Cash-flow loadings | `lrr.calibrate_from_data` |
| Prices and returns | `lrr.compute_asset_pricing_moments` |

tidyfinance downloads CRSP/Compustat/CCM and supplies NYSE breakpoints. `lrr.build_annual_panel` still builds Campbell–Shiller dividends and historical book equity.

`lrr.calibrate_from_data(dc, long=..., short=..., market=..., frequency="annual", window=2)` takes consumption growth and the two legs. No argument for returns.

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

Missing WRDS credentials raise `EmpiricalDataError` with a message to call `tf.set_wrds_credentials()`.
