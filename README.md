# Long-run risks

Python package `lrrcs`, a companion to [tidyfinance](https://github.com/tidy-finance/py-tidyfinance).
A general-equilibrium long-run-risks model (Bansal and Yaron 2004; Kiku 2006).
The objects of the equilibrium are **asset prices and risk premia**.

Long-run risks are a small but highly persistent component of consumption growth.
Value firms are highly exposed to those low-frequency shocks; growth firms are driven more by short-lived consumption news.
Epstein–Zin preferences make the marginal rate of substitution depend on the return on aggregate wealth, so that dispersion in cash-flow exposure shows up in valuations and in ex-ante premia.

tidyfinance gets data and sorts. `lrrcs` maps cash-flow exposures into prices and premia.
Average returns never enter the cash-flow step.

**Documentation:** [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)

| Page | What it is |
|---|---|
| [Getting started](https://tlorans.github.io/kiku-value-premium-replication/getting-started.html) | Install, Table II by hand, a first solve |
| [Financial data](https://tlorans.github.io/kiku-value-premium-replication/financial-data.html) | Consumption, Campbell–Shiller dividends, the annual panel |
| [The long-run risks model](https://tlorans.github.io/kiku-value-premium-replication/long-run-risks-model.html) | General equilibrium: valuations and risk premia |
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
