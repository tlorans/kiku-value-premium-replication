# Long-run risks

Python package `lrrcs`. Kiku (2006) in code: cash-flow leverage on long-run consumption risk prices the value premium. Average returns never enter the cash-flow step.

A DCF takes expected cash flows and a discount rate as two independent inputs. This model derives both from one process — consumption growth. Dividends load on a small, highly persistent component of consumption growth; an Epstein–Zin household prices those loadings. Value firms are more exposed to that component than growth firms, so the same household returns value's high premium and low price–dividend ratio together.

**Documentation:** [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)

| Page | What it is |
| --- | --- |
| [The result](https://tlorans.github.io/kiku-value-premium-replication/getting-started.html) | Install, Table II, the scoreboard |
| [The long-run risks model](https://tlorans.github.io/kiku-value-premium-replication/long-run-risks-model.html) | Where growth and the discount rate come from |
| [Measuring leverage](https://tlorans.github.io/kiku-value-premium-replication/measuring-leverage.html) | Equation (19), no returns |
| [Does the market still fit?](https://tlorans.github.io/kiku-value-premium-replication/time-series.html) | Same household, the market pair |
| [Value versus growth](https://tlorans.github.io/kiku-value-premium-replication/cross-section.html) | Two legs, nothing re-tuned |
| [Financial data](https://tlorans.github.io/kiku-value-premium-replication/financial-data.html) | Rebuild 1930–2003 from the raw records |

## Install

Python 3.11+.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

```python
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

WRDS reconstruction: `uv pip install -e ".[data]"` then `tf.set_wrds_credentials()` (from the `tidyfinance` package). Details live on the [installation](https://tlorans.github.io/kiku-value-premium-replication/installation.html) page.

## License

MIT
