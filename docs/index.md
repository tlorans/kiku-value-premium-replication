---
title: Home
nav_order: 1
permalink: /
---

# Long-run risks

Calibrate cash flows, then ask whether the model matches asset-pricing moments.

Companion to [tidyfinance](https://www.tidy-finance.org/): tidyfinance gets data and sorts; `lrrcs` calibrates cash-flow loadings and prices claims. Average returns never enter the cash-flow step.

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

[Start here]({{ '/getting-started.html' | relative_url }})

## The four steps

1. Form the claim(s) from data.
2. Calibrate cash-flow dynamics.
3. Solve the long-run risks model.
4. Compare model asset-pricing moments to the data.

That loop is [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}). Then we run it twice: [The market]({{ '/time-series.html' | relative_url }}) and [Value versus growth]({{ '/cross-section.html' | relative_url }}).

[Package]({{ '/package.html' | relative_url }}) · [Installation]({{ '/installation.html' | relative_url }}) · [API]({{ '/api.html' | relative_url }}) · [GitHub](https://github.com/tlorans/kiku-value-premium-replication)
