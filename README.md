# geap

General-equilibrium asset pricing models in Python.

The first family is long-run risks: cash-flow leverage on persistent
consumption growth, priced by an Epstein–Zin household. Average
returns never enter the cash-flow step.

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

## Examples

| Script | What it prints |
| --- | --- |
| `examples/run_paper.py` | The paper in Kiku's order |
| `examples/calibrate_any_portfolio.py` | Loadings from cash-flows you supply |
| `examples/two_firms.py` | Two firms that differ only in phi |
| `examples/dcf_counterfactual.py` | The same cash-flows in a DCF and in the model |
| `examples/robustness.py` | The premium as one parameter varies |

## License

MIT
