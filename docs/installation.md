---
title: Installation
parent: Package
nav_order: 1
---

# Installation

The core install solves the model at the Table II calibration. Reconstructing Section 2 from the CRSP and Compustat tapes is optional and requires WRDS. The pricing argument does not depend on a data vendor. Only the reconstruction of Table I does.

## Package

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
uv pip install -e ".[fast]"   # Numba on the Euler loops
uv pip install -e ".[data]"   # WRDS + figures
```

Core dependencies are numpy, scipy, and pandas. The decision interval in the model is one month. The published grid is $$n_x=30$$ points on $$x$$ and $$n_s=4$$ points on $$\sigma^2$$, with a 7-point Gauss–Hermite rule on the short-run innovation $$\eta$$.

## WRDS credentials (Section 2 only)

Repo-root `.env` (gitignored; see `.env.example`):

```
WRDS_USERNAME=...
WRDS_PASSWORD=...
```

`connect_wrds()` raises `EmpiricalDataError` if the `[data]` extra is missing or the keys are empty. `model`, `calibration`, and `implications` do not import `wrds`.

## Walk the paper in order

```bash
uv run python examples/run_paper.py
```

If `[data]` or `.env` is missing, the script skips Section 2, prints the reason, and continues from Table II. The example uses $$n_x=15$$ so a laptop finishes; the paper grid is $$n_x=30$$.

Demos that never touch WRDS:

- [`examples/demo.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/demo.py) — Section 3.4 premia and simulated cash-flow moments
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

Value’s long-run leverage is $$\phi=6.2$$ against growth’s $$2.6$$. The analytical solution ranks the long-run risk premium on value above that on growth. Numerical expected returns rank value above market above growth.

[Section 2]({% link empirical.md %}) builds Table I from the committed annual panel, or from WRDS if `refresh=True`.
