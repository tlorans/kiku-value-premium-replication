# Kiku (2006) – Is the Value Premium a Puzzle? – Replication Package

Python package that replicates the core quantitative results of Dana Kiku’s 2006 Job Market Paper.

The paper shows that the value premium is compensation for long-run consumption risk: value firms’ cash flows load more heavily on the persistent expected-growth factor of the Bansal–Yaron long-run risks model. With Epstein–Zin preferences this exposure commands a large risk premium, while growth firms are driven mainly by short-run and volatility risks.

## Installation

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
pip install -e .
```

## Quick demonstration of the mechanism

```python
from kiku_value_premium.params import get_default_params
from kiku_value_premium.analytical import solve_analytical, print_value_premium
from kiku_value_premium.simulation import simulate_moments, print_moments

# 1. Analytical long-run risk premia (Section 3.4)
sol = solve_analytical()
print_value_premium(sol)

# 2. Cash-flow moments from Monte-Carlo (Tables III–IV)
mom = simulate_moments(n_sims=100, years=74)
print_moments(mom)
```

The analytical module recovers a sizable value-growth spread driven almost entirely by the difference in the long-run leverage parameters φ (6.2 vs 2.6) amplified by ρ = 0.98. The simulation module matches the first and second moments of consumption and dividend growth reported in the paper.

## Package contents

| Module | Content |
|--------|---------|
| `params.py` | Exact Table II calibration (preferences, consumption, three dividend streams, residual correlations) |
| `preferences.py` | Epstein–Zin recursive utility and IMRS |
| `analytical.py` | Log-linear solutions for A-coefficients, risk prices Λ, betas and long-run premia |
| `dynamics.py` | State evolution (x, σ²) + joint cash-flow simulation with correct shock correlations |
| `simulation.py` | Monte-Carlo, annual aggregation, moment tables |

## Next steps for a full numerical replication

- Tauchen–Hussey discretization of the joint (x, σ²) process (Appendix of the paper: 30-point GH for x, 4-point grid for volatility).
- Fixed-point solution of the Euler equation on the product grid for the consumption claim and the three equity claims.
- Computation of returns, risk-free rate, CAPM / C-CAPM betas, predictability regressions and the counter-cyclical value premium (Tables VII–X).

These pieces follow the paper’s equations one-for-one and can be added modularly.

## Key quantitative targets (paper)

- Model value premium ≈ 5.3 % (data ≈ 6.1 %)
- E[R] Growth / Value / Market ≈ 6.1 / 11.4 / 7.5 %
- log(P/D) ≈ 3.65 / 3.10 / 3.24
- CAPM β_Value / β_Growth ≈ 0.92 (model reproduces the failure of the CAPM)

## References

Kiku, D. (2006). Is the Value Premium a Puzzle? Job Market Paper, Duke University.

Bansal, R. & Yaron, A. (2004). Risks for the Long Run. Journal of Finance.

Tauchen, G. & Hussey, R. (1991). Quadrature-based methods … Econometrica.

## License

MIT
