---
title: Home
nav_order: 1
permalink: /
---

# Long-run risks

Calibrate cash flows, then ask whether the model matches asset-pricing moments.

Companion to [tidyfinance](https://www.tidy-finance.org/): tidyfinance gets data and sorts; `lrrcs` calibrates cash-flow loadings and prices claims. Average returns never enter the cash-flow step. The chapters are follow-alongs: run every snippet top to bottom, full code first, then the `lrr.` shortcut.

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

[Start here]({{ '/getting-started.html' | relative_url }})

## The book

1. [Financial data]({{ '/financial-data.html' | relative_url }}) — consumption, Campbell–Shiller dividends, the panel.
2. [The long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}) — what $$x_t$$ is, and why it is priced.
3. [The market]({{ '/time-series.html' | relative_url }}) — one claim, time series.
4. [Value versus growth]({{ '/cross-section.html' | relative_url }}) — two legs, same household.

[Package]({{ '/package.html' | relative_url }}) · [Installation]({{ '/installation.html' | relative_url }}) · [API]({{ '/api.html' | relative_url }}) · [GitHub](https://github.com/tlorans/kiku-value-premium-replication)
