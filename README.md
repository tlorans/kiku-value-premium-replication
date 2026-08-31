# Long-run risks

Python package `lrrcs`. Kiku (2006) in code: cash-flow leverage on long-run consumption risk prices the value premium. Average returns never enter the cash-flow step.

A DCF takes expected cash flows and a discount rate as two independent inputs. This model derives both from one process, consumption growth. Dividends load on a small, highly persistent component of consumption growth; an Epstein-Zin household prices those loadings. Value firms are more exposed to that component than growth firms, so the same household returns value's high premium and low price-dividend ratio together.

**The course:** [Valuing Asset Claims in General Equilibrium](https://tlorans.github.io/kiku-value-premium-replication/) — twelve chapters from the puzzle to pricing your own claim. Every model number on the site is printed at build time by the code cell above it, and each chapter downloads as a runnable notebook.

| Part | Chapters |
| --- | --- |
| I — The Puzzle | [Two free numbers](https://tlorans.github.io/kiku-value-premium-replication/chapters/01-two-free-numbers.html) · [The value premium in the data](https://tlorans.github.io/kiku-value-premium-replication/chapters/02-value-premium-in-the-data.html) |
| II — The Toolkit | [Pricing by Euler equation](https://tlorans.github.io/kiku-value-premium-replication/chapters/03-pricing-by-euler-equation.html) · [Epstein–Zin preferences](https://tlorans.github.io/kiku-value-premium-replication/chapters/04-epstein-zin-preferences.html) · [Long-run risks](https://tlorans.github.io/kiku-value-premium-replication/chapters/05-long-run-risks.html) |
| III — Solving | [Log-linear](https://tlorans.github.io/kiku-value-premium-replication/chapters/06-log-linear-solution.html) · [Quadrature](https://tlorans.github.io/kiku-value-premium-replication/chapters/07-quadrature-solution.html) |
| IV — Confronting the Data | [Calibrating cash flows](https://tlorans.github.io/kiku-value-premium-replication/chapters/08-calibrating-cash-flows.html) · [The market test](https://tlorans.github.io/kiku-value-premium-replication/chapters/09-the-market-test.html) · [The value premium, resolved](https://tlorans.github.io/kiku-value-premium-replication/chapters/10-value-premium-resolved.html) |
| V — Your Turn | [Price your own claim](https://tlorans.github.io/kiku-value-premium-replication/chapters/11-price-your-own-claim.html) · [Objections and limits](https://tlorans.github.io/kiku-value-premium-replication/chapters/12-objections-and-limits.html) |

## Install

Python 3.11+.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

```python
import lrrcs as lrr

model = lrr.LongRunRisksModel()      # the Table II calibration
res = model.solve()                  # solve on the paper's state grid
print(res.summary())                 # expected returns, betas, log P/D
res.value_premium                    # 5.18
```

Change one number and solve again. Nothing else needs re-tuning:

```python
lrr.LongRunRisksModel(gamma=7.5).solve().value_premium
lrr.LongRunRisksModel(claims={"value": {"phi": 2.6}}).solve().value_premium
```

Table VII, the paper's own model column, is one call:

```python
print(model.simulate(n_samples=1000, years=74, seed=0).summary())
```

WRDS reconstruction: `uv pip install -e ".[data]"` then `tf.set_wrds_credentials()` (from the `tidyfinance` package). Details live on the [installation](https://tlorans.github.io/kiku-value-premium-replication/reference/installation.html) page.

## Site

The site is a Quarto project in `site/`, rendered and deployed by `.github/workflows/publish.yml` (GitHub Pages, source: GitHub Actions). Chapters execute the package at render time; the committed `site/_freeze/` carries the executed outputs, and `.github/workflows/freshness.yml` re-executes everything weekly from scratch. Locally: `make preview` / `make site`.

## License

MIT
