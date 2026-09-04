# geap

General-equilibrium asset pricing models in Python.

Families share one protocol: specify, solve, compare. Average returns
never enter the cash-flow step.

Docs: [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)

```python
import geap

model = geap.LongRunRisksModel()      # Table II calibration
res = model.solve()                  # quadrature solution
print(res.summary())                 # expected returns, Sharpe, log P/D

res.compare("value", "growth", market="market").premium
```

The model prices a set of named claims. Which two of them make a spread
is a question you ask afterwards.

```python
geap.LongRunRisksModel(gamma=7.5).solve().compare("value", "growth").premium
geap.LongRunRisksModel(claims={"value": {"phi": 2.6}}).solve().compare("value", "growth").premium
```

Table VII, the paper's own model column, is one call:

```python
print(model.simulate(n_samples=1000, years=74, seed=0).summary())
```

## Install

Python 3.11+.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

WRDS reconstruction: `uv pip install -e ".[data]"` then
`tf.set_wrds_credentials()` (from `tidyfinance`). Details live on the
[installation](https://tlorans.github.io/kiku-value-premium-replication/installation.html)
page.

## Families

**Long-run risks** (`LongRunRisksModel`): Bansal and Yaron (2004)
endowment, Epstein–Zin preferences, Kiku (2006) cash-flow leverage.
`geap.lrr.estimation` estimates the same model by GMM with time
aggregation (Bansal, Kiku, and Yaron 2016).

**Power utility** (`PowerUtilityModel`): Mehra and Prescott (1985)
two-state consumption chain. The documented result is the equity
premium puzzle.

**Habit** (`CampbellCochraneModel`): Campbell and Cochrane (1999)
external surplus. Time-varying risk aversion at $\gamma = 2$.

**GMM** (`geap.gmm`): Hansen GMM on moment conditions. Linear factor
GMM is OLS of average excess returns on betas. SDF GMM sets
$E[m(\theta) R^e] = 0$. This is not the cash-flow calibration: returns
never enter `calibrate_claim`.

## Examples

| Script | What it prints |
| --- | --- |
| `examples/run_paper.py` | The paper in Kiku's order |
| `examples/calibrate_any_portfolio.py` | Loadings from cash-flows you supply |
| `examples/two_firms.py` | Two firms that differ only in phi |
| `examples/dcf_counterfactual.py` | The same cash-flows in a DCF and in the model |
| `examples/robustness.py` | The premium as one parameter varies |
| `examples/mehra_prescott.py` | Power-utility CCAPM, Mehra and Prescott (1985) |
| `examples/campbell_cochrane.py` | External habit, Campbell and Cochrane (1999) |
| `examples/gmm_linear_factor.py` | Linear-factor GMM on means and betas |
| `examples/gmm_power_utility.py` | Power-utility SDF GMM on a three-moment toy |
| `examples/bky_jme.py` | Bansal, Kiku, Yaron (2016): sample, cold-start Table 2 GMM, Tables 3–8 |

## License

MIT
