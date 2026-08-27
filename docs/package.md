---
title: Package
nav_order: 7
has_children: true
has_toc: false
---

# Package

`lrrcs` is a companion to tidyfinance. tidyfinance gets data and sorts; `lrrcs` calibrates cash-flow loadings and prices claims. Average returns never enter the cash-flow step.

```python
import numpy as np
import polars as pl
import tidyfinance as tf
import lrrcs as lrr
```

Start with the book: [Getting started]({{ '/getting-started.html' | relative_url }}), [Financial data]({{ '/financial-data.html' | relative_url }}), [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}), [The market]({{ '/time-series.html' | relative_url }}), [Value versus growth]({{ '/cross-section.html' | relative_url }}).

A typical session after the data chapter: load the 1930–2003 sample, slope of market $$\Delta d$$ on the two-year MA of lagged $$\Delta c$$, then Table II prices.

```python
dc = pl.read_csv("data/consumption_annual.csv").sort("year")
mkt = (
    pl.read_csv("data/annual_panel.csv")
    .filter(pl.col("claim") == "Market")
    .join(dc, on="year")
    .sort("year")
)
y = dc["dc"].to_numpy()
dd = mkt["dgrowth"].to_numpy()
ma = np.full(len(y), np.nan)
for t in range(2, len(y)):
    ma[t] = float(np.mean(y[t - 2 : t]))
mask = np.isfinite(ma) & np.isfinite(dd)
x = ma[mask] - ma[mask].mean()
e = dd[mask] - dd[mask].mean()
phi_tilde = float(np.dot(x, e) / np.dot(x, x))
phi_tilde
```

```text
0.722
```

The same slope from the package, then the linearized prices:

```python
lrr.estimate_long_run_leverage(y, dd, window=2)
lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

- [Installation]({{ '/installation.html' | relative_url }})
- [API]({{ '/api.html' | relative_url }})
