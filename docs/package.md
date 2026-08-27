---
title: Package
nav_order: 7
has_children: true
has_toc: false
---

# Package

`lrrcs` maps the low-frequency risks embodied in cash flows into **asset prices and risk premia**. The inputs are consumption growth and dividend growth; the outputs are valuations and ex-ante compensations, for the aggregate market and for the legs of a sort. Average returns never enter the cash-flow step — they are what the model gets graded on.

```python
import numpy as np
import polars as pl
import lrrcs as lrr
```

Start with the book: [From DCF to general equilibrium]({{ '/getting-started.html' | relative_url }}), [Financial data]({{ '/financial-data.html' | relative_url }}), [The long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}), [The Time Series]({{ '/time-series.html' | relative_url }}), [The Cross Section]({{ '/cross-section.html' | relative_url }}).

A typical session after the data chapter: load the 1930–2003 sample, measure the market's exposure to long-run consumption shocks, then read off Table II valuations and premia.

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

The same slope from the package, then the linearized valuations and risk premia:

```python
lrr.estimate_long_run_leverage(y, dd, window=2)
lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

- [Installation]({{ '/installation.html' | relative_url }})
- [API]({{ '/api.html' | relative_url }})
