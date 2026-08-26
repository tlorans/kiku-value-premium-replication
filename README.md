# Long-run risks and the cross section

Companion package to Dana Kiku (2006). The model is Bansal and Yaron (2004) long-run risks with Epstein–Zin preferences.

Once cash flows are calibrated to consumption and dividends, the model is asked to account for both **time-series and cross-sectional properties of assets’ prices and returns** (Kiku 2006, p. 2). The time-series object is the market claim. The cross-sectional object is a pair of claims that differ only in cash-flow loadings. Value is the first pair. Size, profitability, investment, and climate sorts are later pairs. Average returns never enter the cash-flow step.

**Documentation:** [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)

| Page | What is priced |
|---|---|
| [Time series](https://tlorans.github.io/kiku-value-premium-replication/time-series.html) | Market claim: equity premium, risk-free rate, $$\log(P/D)$$ |
| [Cross section](https://tlorans.github.io/kiku-value-premium-replication/cross-section.html) | Value versus growth |
| [Other risk premia](https://tlorans.github.io/kiku-value-premium-replication/other-risk-premia.html) | Size, profitability, investment |
| [Climate](https://tlorans.github.io/kiku-value-premium-replication/climate.html) | Transition and physical sorts |

[Installation](https://tlorans.github.io/kiku-value-premium-replication/installation.html) · [API](https://tlorans.github.io/kiku-value-premium-replication/api.html) · [Other portfolios](https://tlorans.github.io/kiku-value-premium-replication/generalization.html)

## Install

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
uv pip install -e ".[fast]"   # Numba on the Euler loops
uv pip install -e ".[data]"   # WRDS + figures
```

Core install (numpy, scipy, pandas) solves the Table II calibration with no secrets.

Reconstructing the 1930–2003 book-to-market panel needs `[data]` and a repo-root `.env`:

```
WRDS_USERNAME=...
WRDS_PASSWORD=...
```

See `.env.example`. The file is gitignored. `connect_wrds()` raises if the extra or the keys are missing. `model`, `calibration`, and `implications` never import `wrds`.

## Run

```bash
uv run python examples/run_paper.py
```

```python
from kiku_value_premium.model import get_table_ii_params, solve_analytical, print_value_premium

print_value_premium(solve_analytical(get_table_ii_params()))
```

Value’s long-run leverage is $$\phi = 6.2$$ against growth’s $$2.6$$. Calibration uses cash-flow moments only; return premia never enter.

## Citation

Kiku, D. (2006). *Is the Value Premium a Puzzle?* Job Market Paper, Duke University / Wharton.

Bansal, R., and A. Yaron. (2004). “Risks for the Long Run.” *Journal of Finance*.

Fama, E., and K. French. (2015). “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics*.

Melin, L., and F. Zhang. (2026). “Quantifying Climate Risk Premia.” EDHEC Climate Institute.

## License

MIT
