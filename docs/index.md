---
title: Home
nav_order: 1
permalink: /
---

# Long-run risks

A general-equilibrium model of **asset prices and risk premia**.

Long-run risks are a small but highly persistent component that governs consumption growth. Firms differ in how their dividends are exposed to low-frequency consumption shocks. Time-non-separable Epstein–Zin preferences break the link between smoothing consumption over time and across states, so the marginal rate of substitution depends on the forward-looking return on aggregate wealth. Shocks to the persistent growth-rate component therefore produce large reactions in valuations and sizable risk compensations.

Companion to [tidyfinance](https://www.tidy-finance.org/): tidyfinance gets data and sorts; `lrrcs` maps cash-flow exposures into prices and premia. Average returns never enter the cash-flow step. The chapters are follow-alongs: run every snippet top to bottom, full code first, then the `lrr.` shortcut.

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

[Start here]({{ '/getting-started.html' | relative_url }})

## The book

1. [Financial data]({{ '/financial-data.html' | relative_url }}) — consumption and the cash flows that carry low-frequency risk.
2. [The long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}) — the general-equilibrium objects: valuations and risk premia.
3. [The market]({{ '/time-series.html' | relative_url }}) — the aggregate claim.
4. [Value versus growth]({{ '/cross-section.html' | relative_url }}) — dispersion in long-run risk across firms.

[Package]({{ '/package.html' | relative_url }}) · [Installation]({{ '/installation.html' | relative_url }}) · [API]({{ '/api.html' | relative_url }}) · [GitHub](https://github.com/tlorans/kiku-value-premium-replication)
