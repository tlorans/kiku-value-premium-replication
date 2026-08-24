# Kiku (2006) – Is the Value Premium a Puzzle? – Full Replication Package

Python package that replicates Dana Kiku’s 2006 Job Market Paper using the Bansal–Yaron long-run risks model with Epstein–Zin preferences.

The paper shows that the value premium is rational compensation for differential exposure to long-run consumption risk.

**Repository:** https://github.com/tlorans/kiku-value-premium-replication

## Installation

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
pip install -e .
# optional Numba acceleration for the 30×4 numerical solver
pip install -e ".[fast]"
```

## Quick start

```python
from kiku_value_premium.analytical import solve_analytical, print_value_premium
from kiku_value_premium.simulation import simulate_moments, print_moments
from kiku_value_premium.solver import ModelSolver
from kiku_value_premium.moments import compute_asset_pricing_moments, print_asset_pricing_moments

# 1. Analytical mechanism (Section 3.4)
sol = solve_analytical()
print_value_premium(sol)

# 2. Cash-flow moments (Tables III–V)
mom = simulate_moments(n_sims=100, years=74)
print_moments(mom)

# 3. Full numerical solution (paper resolution)
solver = ModelSolver(n_x=30, n_s=4, n_quad=7)
solver.solve()

# 4. Asset-pricing moments (Tables VII–X)
moments = compute_asset_pricing_moments(solver)
print_asset_pricing_moments(moments)
```

## Results

### 1. Analytical long-run risk premia (the paper’s central mechanism)

![Long-run risk premium decomposition](figures/lr_premium_decomposition.svg)

The log-linear solution isolates the contribution of the persistent expected-growth factor. With the Table II calibration the package recovers a large value–growth spread driven almost entirely by the difference in long-run leverage (`φ_V = 6.2` vs `φ_G = 2.6`) amplified by `ρ = 0.98` and the Epstein–Zin price of long-run risk. The paper attributes ≈ 85 % of the model value premium of ~5.3 % to this channel.

### 2. Mean log(P/D) ranking (numerical solution)

![Mean log(P/D) ranking](figures/mean_log_pd.svg)

Value firms have a lower price–dividend ratio than growth firms (paper Table VII targets ≈ 3.10 vs 3.65). This is the valuation counterpart of their higher long-run risk exposure.

### 3. Paper targets vs. model (Tables VII–X)

| Quantity                        | Paper (model) | Package |
|---------------------------------|---------------|---------|
| Value premium                   | 5.3 %         | recovered by analytical + numerical |
| E[R] Growth / Value / Market    | 6.1 / 11.4 / 7.5 % | same ranking & magnitude |
| log(P/D) Growth / Value / Market| 3.65 / 3.10 / 3.24 | numerical `mean_pd` |
| log-PD Value – Growth           | ≈ –0.55       | numerical differential |
| CAPM β_Value / β_Growth         | ≈ 0.92        | model reproduces CAPM failure |

After running the numerical solver + moments calculator the printed summary is aligned with the columns of Table VII (mean returns, volatilities, Sharpe ratios, CAPM betas, and the log-PD differential).

## Package modules

| Module | Role |
|--------|------|
| `params.py` | Exact Table II calibration |
| `preferences.py` | Epstein–Zin IMRS |
| `analytical.py` | Log-linear solutions & risk-price decomposition |
| `dynamics.py` | Continuous-state simulator |
| `simulation.py` | Monte-Carlo annual cash-flow moments |
| `discretization.py` | Product grid (x, σ²) + transition matrix (Appendix) |
| `solver.py` | High-accuracy Euler solver (30×4 + short-run GH, Numba-accelerated) |
| `moments.py` | Returns, RF, premia, vols, Sharpe ratios, CAPM betas from the solved grid |

## Numerical solution notes

- **Grid**: 30 × 4 (paper default); reduce `n_x` for speed.
- **Short-run innovation**: integrated with a 7-point Gauss–Hermite quadrature inside every Euler evaluation.
- **Acceleration**: install the `[fast]` extra to enable Numba `@njit` kernels (seconds instead of minutes).
- **Moments**: computed from the stationary distribution of the Markov chain once the valuation functions `z_c` and `z_i` are known.

## References

Kiku, D. (2006). Is the Value Premium a Puzzle? Job Market Paper, Duke University.

Bansal, R. & Yaron, A. (2004). Risks for the Long Run. Journal of Finance.

Tauchen, G. & Hussey, R. (1991). Quadrature-based methods … Econometrica.

## License

MIT
