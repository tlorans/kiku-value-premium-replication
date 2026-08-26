---
title: Installation
parent: Package
nav_order: 1
---

# Installation

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
uv pip install -e ".[fast]"
uv pip install -e ".[data]"
```

The distribution name is `lrrcs`. Import it that way.

```python
from lrrcs.model import get_table_ii_params, solve_analytical, print_long_short_premium
print_long_short_premium(solve_analytical(get_table_ii_params()))
```

`kiku_value_premium` still imports. Use `lrrcs`.

Core install (numpy, scipy, pandas) solves Table II with no secrets. Reconstructing the 1930–2003 book-to-market panel needs `[data]` and a repo-root `.env`:

```
WRDS_USERNAME=...
WRDS_PASSWORD=...
```

See `.env.example`. `connect_wrds()` raises if the extra or the keys are missing.
