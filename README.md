# Long-run risks

Python package `lrrcs`, a companion to [tidyfinance](https://github.com/tidy-finance/py-tidyfinance).
The model is Bansal and Yaron (2004) long-run risks with Epstein–Zin preferences.
Kiku (2006) is the first cross-sectional column.

tidyfinance gets data and sorts. `lrrcs` calibrates cash-flow loadings and prices claims.
Average returns never enter the cash-flow step.

**Documentation:** [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)

| Page | What it is |
|---|---|
| [Getting started](https://tlorans.github.io/kiku-value-premium-replication/getting-started.html) | Install and a five-line solve |
| [Financial data](https://tlorans.github.io/kiku-value-premium-replication/financial-data.html) | Consumption, Campbell–Shiller dividends, the annual panel |
| [Cash flows, then prices](https://tlorans.github.io/kiku-value-premium-replication/cash-flows-then-prices.html) | The four-step loop |
| [The market](https://tlorans.github.io/kiku-value-premium-replication/time-series.html) | One claim, time series |
| [Value versus growth](https://tlorans.github.io/kiku-value-premium-replication/cross-section.html) | Two legs, same household |

## Install

Python 3.11+.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

WRDS reconstruction: `uv pip install -e ".[data]"` then `tf.set_wrds_credentials()`.

## License

MIT
