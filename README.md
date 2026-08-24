# Kiku (2006) – Is the Value Premium a Puzzle? – Replication Package

Python package that replicates the core of Dana Kiku’s 2006 Job Market Paper *Is the Value Premium a Puzzle?* using the Bansal–Yaron long-run risks model with Epstein–Zin preferences.

The paper shows that the value premium is compensation for long-run consumption risk: value firms’ cash flows load more heavily on the persistent expected-growth factor. With Epstein–Zin preferences this exposure commands a large risk premium.

## Installation

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
pip install -e .
```

## Quick start

```python
from kiku_value_premium.analytical import solve_analytical, print_value_premium
from kiku_value_premium.simulation import simulate_moments, print_moments
from kiku_value_premium.solver import ModelSolver

# 1. Analytical demonstration of the mechanism (Section 3.4)
sol = solve_analytical()
print_value_premium(sol)

# 2. Cash-flow moments (Tables III–V)
mom = simulate_moments(n_sims=100, years=74)
print_moments(mom)

# 3. Numerical Tauchen–Hussey + Euler solution (Appendix)
solver = ModelSolver(n_x=15, n_s=4)   # paper uses 30 × 4; start smaller for speed
solver.solve()
print(solver.mean_pd())
```

## Package contents

| Module | Content |
|--------|---------|
| `params.py` | Exact Table II calibration |
| `preferences.py` | Epstein–Zin IMRS |
| `analytical.py` | Log-linear A-coefficients, risk prices, long-run premia |
| `dynamics.py` | Continuous-state simulation of (x, σ², Δc, Δd) |
| `simulation.py` | Monte-Carlo annual moments |
| `discretization.py` | Product grid (x × σ²) + transition matrix |
| `solver.py` | Successive-approximation Euler solver for z_c and the three equity claims |

## Key quantitative targets (paper)

- Model value premium ≈ 5.3 % (data ≈ 6.1 %)
- E[R] Growth / Value / Market ≈ 6.1 / 11.4 / 7.5 %
- log(P/D) ≈ 3.65 / 3.10 / 3.24
- CAPM β_Value / β_Growth ≈ 0.92 (model reproduces the failure of the CAPM)

The analytical module already recovers a large value-growth spread driven by the difference in long-run leverage φ. The numerical solver provides the grid-based valuation functions from which returns, the risk-free rate and further moments can be computed.

## References

Kiku, D. (2006). Is the Value Premium a Puzzle? Job Market Paper, Duke University.

Bansal, R. & Yaron, A. (2004). Risks for the Long Run. Journal of Finance.

Tauchen, G. & Hussey, R. (1991). Quadrature-based methods for obtaining approximate solutions to nonlinear asset pricing models. Econometrica.

## License

MIT
