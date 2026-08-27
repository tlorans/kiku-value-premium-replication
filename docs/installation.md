---
title: Installation
parent: Package
nav_order: 1
---

# Installation

Python 3.11+. `tidyfinance` is a required dependency. Run the chunks **in order**.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

```python
import sys
import tidyfinance as tf
import lrrcs as lrr

sys.version_info[:2], lrr.__version__
```

```text
((3, 12), '0.5.0')
```

Core install solves the Table II general equilibrium — valuations and long-run risk premia — with no secrets:

```python
params = lrr.get_table_ii_params()
lrr.print_long_short_premium(lrr.solve_analytical(params))
```

```text
Approximate annualized long-run risk premia:
  growth  :   0.39%
  value   :   0.80%
  market  :   0.34%
Value-growth spread from long-run risks: 0.40%
```

## Extras

```bash
uv pip install -e ".[fast]"
uv pip install -e ".[data]"
```

`[fast]` is Numba (the Euler grid). `[data]` is matplotlib, pyarrow, polars, and plotnine — needed to reconstruct the 1930–2003 panel and to run the tutorial plots.

```python
import polars as pl
import plotnine as p9

pl.__version__, p9.__version__
```

## WRDS

Rebuilding CRSP / Compustat from scratch needs credentials. Once per machine:

```python
tf.set_wrds_credentials()
```

That writes a `.env` tidyfinance already knows how to read. `lrr.build_annual_panel(refresh=True)` then hits WRDS. `refresh=False` reuses `data/raw/*.parquet` or the shipped CSVs.

Missing credentials raise `EmpiricalDataError` with a message to call `tf.set_wrds_credentials()`.

## Key takeaways

- Editable install with `uv` is enough to price Table II.
- `[data]` is for the follow-along plots and the panel.
- WRDS is optional if you use the shipped 1930–2003 files.
