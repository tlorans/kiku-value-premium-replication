---
layout: default
title: Model
---

# Section 3 – Model

## What she does

Preferences are Epstein–Zin. The intertemporal marginal rate of substitution is her equation (3). Agents care about long-run growth prospects because risk aversion \(\gamma\) differs from the inverse EIS.

Aggregate consumption is the Bansal–Yaron (2004) long-run risks process — her (6)–(9) / Table II: a small persistent expected-growth factor \(x_t\) (\(\rho=0.98\)), short-run shocks, and stochastic volatility.

Equities are claims to heterogeneous dividend streams. Value and growth differ in their loadings on the three risks. The decisive parameter is long-run leverage \(\phi\): value 6.2, growth 2.6, market 2.8.

She solves the model on a Tauchen–Hussey product grid over \((x,\sigma^2)\). Paper default is \(30\times 4\) plus a 7-point Gauss–Hermite quadrature for the short-run innovation inside every Euler evaluation. Section 3.4 is the log-linear solution that isolates the long-run risk prices.

## What you call

```python
from kiku_value_premium.model import (
    ModelParams,
    PreferencesParams,
    ConsumptionParams,
    DividendParams,
    get_table_ii_params,
    EpsteinZinPreferences,
    Dynamics,
    StateGrid,
    ModelSolver,
    solve_analytical,
    print_value_premium,
)

params = get_table_ii_params()
print(params.prefs)            # δ=0.999, γ=10, ψ=1.5
print(params.cons.rho)         # 0.98
print(params.dividends["value"].phi)   # 6.2
print(params.dividends["growth"].phi)  # 2.6

ez = EpsteinZinPreferences(params.prefs)
print(ez.theta)

dyn = Dynamics(params, seed=42)
path = dyn.simulate_cashflows(T=12 * 74)

print_value_premium(solve_analytical(params))

# Paper default is n_x=30; examples/run_paper.py uses 15 so it finishes.
solver = ModelSolver(params, n_x=30, n_s=4, n_quad=7)
solver.solve()
# solver.z_c, solver.z["value"], solver.z["growth"], solver.stationary
```

Install the `[fast]` extra to enable Numba kernels on the Euler loops.

## What you should see

Table II defaults:

| Block | Values |
|-------|--------|
| Preferences | \(\delta=0.999\), \(\gamma=10\), \(\psi=1.5\) |
| Consumption | \(\mu=0.0015\), \(\rho=0.98\), \(\varphi_x=0.032\), \(\sigma=0.0064\), \(\nu=0.99\), \(\sigma_w=0.0000017\) |
| Growth | \(\mu=0.0009\), \(\phi=2.6\), \(\varphi_\sigma=8.4\), \(\alpha=0.27\) |
| Value | \(\mu=0.0019\), \(\phi=6.2\), \(\varphi_\sigma=7.4\), \(\alpha=0.15\) |
| Market | \(\mu=0.0012\), \(\phi=2.8\), \(\varphi_\sigma=7.5\), \(\alpha=0.55\) |
| Residual correlations | GV 0.20, GM 0.80, VM 0.45 |

`solve_analytical` ranks the long-run risk premium value > growth and uses Campbell–Shiller linearization points \(\log(P/D)\) growth 3.65, value 3.10, market 3.24. The paper’s model column is a value premium around 5.3%, expected returns 6.1 / 11.4 / 7.5% (growth / value / market), and CAPM \(\beta_V/\beta_G<1\).
