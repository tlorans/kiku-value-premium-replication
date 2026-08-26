---
title: API
parent: Package
nav_order: 2
---

# API

The import name is `lrrcs`. `kiku_value_premium` is the same package.

`market` is the time-series claim. `long` and `short` are the two legs of a sort. `value` / `growth` remain aliases. `print_long_short_premium` prints the spread; `print_value_premium` is the old name.

| Object | Import |
|:---|:---|
| Book-to-market panel, 1930–2003 | `lrrcs.empirical` |
| IMRS, dynamics, solver | `lrrcs.model` |
| Cash-flow loadings | `lrrcs.calibration` |
| Prices and returns | `lrrcs.implications` |

`calibrate_from_data(dc, long=..., short=..., market=..., frequency="annual", window=2)` takes consumption growth and the two legs. No argument for returns.

```python
from lrrcs.model import get_table_ii_params, solve_analytical, print_long_short_premium

print_long_short_premium(solve_analytical(get_table_ii_params()))
```

`connect_wrds()` raises if `[data]` or `.env` is missing. `model`, `calibration`, and `implications` do not import `wrds`.
