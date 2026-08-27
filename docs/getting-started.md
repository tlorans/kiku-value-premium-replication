---
title: Getting started
nav_order: 2
---

# Getting started
{: .no_toc }

1. TOC
{:toc}

Python 3.11+. Clone the repository and install in editable mode with `uv`.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

**What that did.** It loaded Table II of Kiku (2006) — the default consumption process, preferences, and dividend loadings — solved the model, and printed the long–short premium the Euler equation assigns. You did not estimate anything.

**What that did not do.** It did not match that premium. Average returns never entered. It did not touch WRDS.

tidyfinance gets data and sorts. `lrrcs` calibrates cash-flow loadings and prices claims. This first run used only `lrrcs`. You will need both when you form claims from CRSP and Compustat.

For Numba, matplotlib, parquet, and WRDS credentials, see [Installation]({{ '/installation.html' | relative_url }}).

Next: [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}).
