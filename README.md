# Long-run risks

Python package `lrrcs`: a general-equilibrium long-run-risks model (Bansal and Yaron 2004; Kiku 2006).
The objects of the equilibrium are **asset prices and risk premia**.

A DCF takes expected cash flows and a discount rate as two independent inputs you choose by hand.
This model derives both from one measurable source: aggregate consumption.
Consumption growth has a small, slow-moving component; each asset's dividends inherit it with an
estimated leverage (the cash-flow model), and an investor who dreads bad news about the distant
future prices those dividends (the discount-rate model). Value firms' dividends track the slow
component closely and growth firms' barely do — so the same investor prices the aggregate market
and the value premium, in prices and in premia. Average returns never enter the cash-flow step.

**Documentation:** [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)

| Page | What it is |
|---|---|
| [From DCF to general equilibrium](https://tlorans.github.io/kiku-value-premium-replication/getting-started.html) | Install, Table II by hand, a first solve |
| [Financial data](https://tlorans.github.io/kiku-value-premium-replication/financial-data.html) | Consumption, Campbell–Shiller dividends, the annual panel |
| [The long-run risks model](https://tlorans.github.io/kiku-value-premium-replication/long-run-risks-model.html) | General equilibrium: prices and risk premia |
| [The Time Series](https://tlorans.github.io/kiku-value-premium-replication/time-series.html) | One claim, year after year |
| [The Cross Section](https://tlorans.github.io/kiku-value-premium-replication/cross-section.html) | Two legs, same investor |

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

WRDS reconstruction: `uv pip install -e ".[data]"` then `tf.set_wrds_credentials()` (from the `tidyfinance` package).

## License

MIT
