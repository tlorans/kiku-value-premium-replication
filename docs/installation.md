---
title: Installation
nav_order: 2
---

# Installation

{: .fs-6 .fw-300 }

Core install solves Table II with no secrets. Section 2 needs WRDS.

## Package

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
uv pip install -e ".[fast]"   # Numba on the Euler loops
uv pip install -e ".[data]"   # WRDS + figures
```

Core dependencies are numpy, scipy, and pandas.

## WRDS credentials (Section 2 only)

Repo-root `.env` (gitignored; see `.env.example`):

```
WRDS_USERNAME=...
WRDS_PASSWORD=...
```

`connect_wrds()` raises `EmpiricalDataError` if the `[data]` extra is missing or the keys are empty. `model`, `calibration`, and `implications` do not import `wrds`.

## Run her paper in order

```bash
uv run python examples/run_paper.py
```

If `[data]` or `.env` is missing, the script skips Section 2, prints why, and continues from Table II. The example uses $$n_x=15$$ so it finishes; her grid is $$n_x=30$$.

Shorter demos that never touch WRDS:

- [`examples/demo.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/demo.py) — analytical long-run premia and simulated cash-flow moments
- [`examples/calibrate_any_portfolio.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_any_portfolio.py) — `calibrate_from_data` on a synthetic cross-section

## First run without WRDS

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

solver = ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))
```

Value’s long-run leverage is $$\phi=6.2$$ against growth’s $$2.6$$. The analytical solution ranks the long-run risk premium value above growth; numerical expected returns rank value above market above growth.

Next: [Empirical evidence]({% link empirical.md %}).
