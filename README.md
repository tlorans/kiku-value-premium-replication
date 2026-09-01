# lrrcs

Python package for general-equilibrium long-run risks. Prices and risk
premia come from one consumption process and one investor.

A discounted cash flow takes expected cash-flows from one model and a
risk premium from another. This package prices every claim inside one
economy. The default calibration is Kiku (2006), Table II. Average
returns never enter the cash-flow step.

Docs: [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)

## Install

Python 3.11+.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

```python
import lrrcs as lrr

model = lrr.LongRunRisksModel()
res = model.solve()
print(res.summary())

res.compare("value", "growth", market="market").premium
```

Change one number and solve again.

```python
lrr.LongRunRisksModel(gamma=7.5).solve().compare("value", "growth").premium
lrr.LongRunRisksModel(claims={"value": {"phi": 2.6}}).solve().compare("value", "growth").premium
```

Table VII, the paper's model column, is one call.

```python
print(model.simulate(n_samples=1000, years=74, seed=0).summary())
```

WRDS reconstruction: `uv pip install -e ".[data]"` then
`tf.set_wrds_credentials()` from `tidyfinance`. See
[installation](https://tlorans.github.io/kiku-value-premium-replication/reference/installation.html).

## Examples

| Script | What it prints |
| --- | --- |
| `examples/run_paper.py` | The paper in Kiku's order |
| `examples/calibrate_any_portfolio.py` | Loadings from cash-flows you supply |
| `examples/two_firms.py` | Two firms that differ only in phi |
| `examples/dcf_counterfactual.py` | The same cash-flows in a DCF and in the model |
| `examples/robustness.py` | The premium as one parameter varies |

## Site

The site is a Quarto project in `site/`, rendered by
`.github/workflows/publish.yml`. User-guide pages are static.
Chapters that still execute the package at render time keep their
outputs in `site/_freeze/`. Locally: `make preview` / `make site`.

## License

MIT
