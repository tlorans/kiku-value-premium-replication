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

## Who this is for

Finance-first readers who already run a DCF and want the two free numbers — expected cash flows and the discount rate — to come from one measurable primitive. You should be comfortable with log returns, a regression, and a small Python session (`numpy` / `polars`). You do not need to write a solver.

Not for a first course in Python, and not a trading notebook. The capstone is a scored pair: the premium *and* the price–dividend level, from cash flows that never saw a return.

## What you can do when you finish

- F — name why pairing any growth rate with any discount rate is not a model of risk.
- F — separate cash-flow exposure (leverage of dividends on expected consumption growth) from a return beta.
- Q — write the Bansal–Yaron growth process and the Epstein–Zin pricing kernel with units on every symbol.
- P — load the 1930–2003 files, estimate one leverage, solve Table II, and interpret the printed premia in one sentence.
- X — reject a calibration that matches returns but misses the valuation.

## How to read a chapter

Each page is one notion. Predict the naive answer before you run a cell. Reproduce the tiny example by hand when there is one (Gordon growth; Campbell–Shiller on twelve toy months). Then run the same arithmetic as `lrr.<name>(...)`. A plot title is a claim, not a variable name. After the scoreboard, write one sentence that would *invalidate* the result (wrong frequency, look-ahead in the expected-growth proxy, leverage estimated from returns).

| Page | Notion | Decision it changes |
|---|---|---|
| [From DCF to general equilibrium](https://tlorans.github.io/kiku-value-premium-replication/getting-started.html) | Two free numbers become one primitive | Whether your discount rate is an input or an output |
| [Financial data](https://tlorans.github.io/kiku-value-premium-replication/financial-data.html) | Consumption, Campbell–Shiller dividends, the annual panel | What is allowed to enter calibration |
| [The long-run risks model](https://tlorans.github.io/kiku-value-premium-replication/long-run-risks-model.html) | Expected growth, Epstein–Zin, the cash-flow SML | What risk the premium pays for |
| [The Time Series](https://tlorans.github.io/kiku-value-premium-replication/time-series.html) | One claim, year after year | Whether the market pair (premium *and* P/D) is a pass |
| [The Cross Section](https://tlorans.github.io/kiku-value-premium-replication/cross-section.html) | Two legs, same household | Whether value's extra return is cash-flow risk or a new discount rate |

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

WRDS reconstruction: `uv pip install -e ".[data]"` then `tf.set_wrds_credentials()`.

## License

MIT
