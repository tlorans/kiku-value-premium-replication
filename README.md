# Long-run risks

Python package `lrrcs`: a general-equilibrium long-run-risks model (Bansal and Yaron 2004; Kiku 2006).
The objects of the equilibrium are **asset prices and risk premia**.

A DCF takes expected cash flows and a discount rate as two independent inputs.
This model derives both from one primitive — the consumption process.
Consumption growth carries a small but highly persistent component, plus time-varying volatility;
dividends load on that component with estimated leverage (the cash-flow model), and an Epstein–Zin
household whose marginal utility responds to news about the entire future prices them (the discount-rate model).
Value firms' cash flows are highly exposed to long-run consumption shocks; growth firms' are driven more
by short-lived fluctuations — so the same household prices the aggregate market and the value premium.
Average returns never enter the cash-flow step.

**Documentation:** [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)

| Page | What it is |
|---|---|
| [From DCF to general equilibrium](https://tlorans.github.io/kiku-value-premium-replication/getting-started.html) | Install, Table II by hand, a first solve |
| [Financial data](https://tlorans.github.io/kiku-value-premium-replication/financial-data.html) | Consumption, Campbell–Shiller dividends, the annual panel |
| [The long-run risks model](https://tlorans.github.io/kiku-value-premium-replication/long-run-risks-model.html) | General equilibrium: valuations and risk premia |
| [The Time Series](https://tlorans.github.io/kiku-value-premium-replication/time-series.html) | One claim, year after year |
| [The Cross Section](https://tlorans.github.io/kiku-value-premium-replication/cross-section.html) | Two legs, same household |

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
