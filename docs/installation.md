---
layout: default
title: Installation & Quick Start
---

# Installation & Quick Start

## Install the package

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
pip install -e .

# Optional: Numba acceleration for the 30×4 numerical solver (highly recommended)
pip install -e ".[fast]"
```

## Minimal quick-start (original value/growth replication)

```python
from kiku_value_premium.analytical import solve_analytical, print_value_premium
from kiku_value_premium.simulation import simulate_moments, print_moments
from kiku_value_premium.solver import ModelSolver
from kiku_value_premium.moments import compute_asset_pricing_moments, print_asset_pricing_moments

# 1. Analytical mechanism – isolates the long-run risk channel
sol = solve_analytical()
print_value_premium(sol)

# 2. Cash-flow moments (compare to paper Tables III–V)
mom = simulate_moments(n_sims=100, years=74)
print_moments(mom)

# 3. Full numerical solution (paper resolution: 30 × 4 grid)
solver = ModelSolver(n_x=30, n_s=4, n_quad=7)
solver.solve()

# 4. Asset-pricing moments (Tables VII–X)
moments = compute_asset_pricing_moments(solver)
print_asset_pricing_moments(moments)
```

## What you should see

- Analytical value–growth long-run risk premium spread driven by φ_V = 6.2 vs φ_G = 2.6
- Numerical mean log(P/D) ranking: Value < Market < Growth
- Value premium ≈ 5.3 % and CAPM failure (model betas do not explain the premium)

For the full economic interpretation of each step, see the **[Recipe page](KIKU_RECIPE.html)**.
