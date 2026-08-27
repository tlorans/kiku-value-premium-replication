---
title: Home
nav_order: 1
permalink: /
---

# Long-run risks

A general-equilibrium model of **asset prices and risk premia**.

Long-run risks are a small but highly persistent component that governs consumption growth. The model also allows for time-variation in the conditional volatility of consumption — news about future economic uncertainty. Firms are distinguished by the exposure of their dividends to low- versus high-frequency consumption shocks. Time-non-separable Epstein–Zin preferences break the link between smoothing consumption over time and across states, so the marginal rate of substitution depends on the forward-looking return on the aggregate wealth portfolio. Shocks to the persistent growth-rate component significantly alter expectations about consumption far into the future, leading to large reactions in stock prices and sizable risk compensations.

Valuations and risk premia therefore depend on the amount of low-frequency risks embodied in cash flows. Value firms are highly exposed to long-run consumption shocks and exhibit higher elasticity of their price–dividend ratios to that news, with high ex-ante compensation; growth firms are driven more by short-lived fluctuations.

Companion to [tidyfinance](https://www.tidy-finance.org/): tidyfinance gets data and sorts; `lrrcs` maps cash-flow exposures into prices and premia. Average returns never enter the cash-flow step. The chapters are follow-alongs: run every snippet top to bottom, full code first, then the `lrr.` shortcut.

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

[Start here]({{ '/getting-started.html' | relative_url }})

## The book

1. [Financial data]({{ '/financial-data.html' | relative_url }}) — the consumption process that governs growth, and the cash flows in which low- versus high-frequency risk is embodied.
2. [The long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}) — Epstein–Zin, the forward-looking return on wealth, and why shocks to the growth-rate component move valuations and premia.
3. [The Time Series]({{ '/time-series.html' | relative_url }}) — one claim’s exposure to low-frequency consumption shocks, year after year.
4. [The Cross Section]({{ '/cross-section.html' | relative_url }}) — value highly exposed to long-run news; growth driven more by short-lived fluctuations.

[Package]({{ '/package.html' | relative_url }}) · [Installation]({{ '/installation.html' | relative_url }}) · [API]({{ '/api.html' | relative_url }}) · [GitHub](https://github.com/tlorans/kiku-value-premium-replication)
