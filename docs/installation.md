---
title: Installation
parent: Package
nav_order: 1
---

# Installation

Python 3.11+. `tidyfinance` is a required dependency.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
uv pip install -e ".[fast]"
uv pip install -e ".[data]"
```

`[fast]` is Numba. `[data]` is matplotlib, pyarrow, polars, and plotnine.

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

Core install solves Table II with no secrets. Reconstructing the 1930–2003 book-to-market panel needs `[data]` and WRDS credentials via `tf.set_wrds_credentials()`.
