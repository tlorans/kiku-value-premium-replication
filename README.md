# Long-run risks and the cross section

Python package `lrrcs`. The model is Bansal and Yaron (2004) long-run risks with Epstein–Zin preferences. Kiku (2006) is the first cross-sectional column.

Once cash flows are calibrated to consumption and dividends, the model is asked to account for both **time-series and cross-sectional properties of assets’ prices and returns**. The time-series object is the market claim. The cross-sectional object is a pair of claims that differ only in cash-flow loadings. Value is the first pair. Size, profitability, investment, industries, and climate sorts are later pairs. Average returns never enter the cash-flow step.

**Documentation:** [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)

| Page | What is priced |
|---|---|
| [Time series](https://tlorans.github.io/kiku-value-premium-replication/time-series.html) | Market claim |
| [Cross section](https://tlorans.github.io/kiku-value-premium-replication/cross-section.html) | Value versus growth |
| [Other risk premia](https://tlorans.github.io/kiku-value-premium-replication/other-risk-premia.html) | Size, profitability, investment, industries |
| [Climate](https://tlorans.github.io/kiku-value-premium-replication/climate.html) | Transition and physical sorts |

## Install

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

```python
from lrrcs.model import get_table_ii_params, solve_analytical, print_long_short_premium

print_long_short_premium(solve_analytical(get_table_ii_params()))
```

`kiku_value_premium` still imports. Use `lrrcs`.

## License

MIT
