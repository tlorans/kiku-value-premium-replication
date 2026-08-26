---
layout: default
title: Installation & Quick Start
---

# Installation & Quick Start

## Install the package

Use `uv` from the repository root:

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .

# Optional: Numba acceleration for the numerical solver
uv pip install -e ".[fast]"

# Optional: WRDS empirical pipeline (Table I, Figures 1–4)
uv pip install -e ".[data]"
```

Core install is numpy, scipy, and pandas. It solves the model from Table II with no secrets.

## WRDS credentials (Section 2 only)

Replication of Table I needs a repo-root `.env`:

```
WRDS_USERNAME=...
WRDS_PASSWORD=...
```

See `.env.example`. The file is gitignored. Importing `empirical` without the `[data]` extra, or with empty keys, raises `EmpiricalDataError` that names the extra and the two keys.

**Without WRDS you can still solve Table II.** `model`, `calibration`, and `implications` do not import `wrds`.

## Run the paper in order

```bash
uv run python examples/run_paper.py
```

If `[data]` or `.env` is missing, the script skips Section 2, prints why, and continues from Table II. The example uses `n_x=15` so it finishes; the paper default is `n_x=30`.

Shorter demos that never touch WRDS:

- [`examples/demo.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/demo.py) — analytical long-run premia and simulated cash-flow moments
- [`examples/calibrate_any_portfolio.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_any_portfolio.py) — `calibrate_from_data` on a synthetic cross-section

## What you should see without WRDS

```python
from kiku_value_premium.model import (
    get_table_ii_params,
    solve_analytical,
    ModelSolver,
    print_value_premium,
)
from kiku_value_premium.calibration import simulate_cashflow_moments
from kiku_value_premium.implications import (
    compute_asset_pricing_moments,
    print_asset_pricing_moments,
)

params = get_table_ii_params()
print_value_premium(solve_analytical(params))
print(simulate_cashflow_moments(n_sims=20, years=74, seed=1))

# Paper default is n_x=30; 15 is faster for a first run.
solver = ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))
```

Value’s long-run leverage is 6.2 against growth’s 2.6. The analytical solution ranks the long-run risk premium value > growth, and the numerical ranking of expected returns is value > market > growth.

## Paper-order recipe

- [Empirical Evidence](empirical.html) — Section 2, Table I, Figures 1–4
- [Model](model.html) — Section 3, IMRS, solver, analytical §3.4
- [Calibration](calibration.html) — Section 4, eq. (19), Tables II–V
- [Asset Pricing Implications](implications.html) — Section 5, Tables VII–X, Figure 5
- [API](api.html) — public names by subpackage
