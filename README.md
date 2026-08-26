# Is the Value Premium a Puzzle?

Python replica of Dana Kiku (2006). The model is Bansal and Yaron (2004) long-run risks with Epstein–Zin preferences. The claim is hers: the value premium is rational compensation for differential exposure to long-run consumption risk.

In the 1930–2003 sample, as in the model, value cash flows load more on the persistent component of consumption growth than growth cash flows do. That leverage gap, amplified by $\rho = 0.98$, produces a model value premium of about 5.3 percent against about 6 percent in the data. CAPM betas do not explain the spread.

**Documentation:** [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)  
The site follows her paper (sidebar, equations, Printed vs Package tables). This README is the GitHub landing page.

| Her section | Site | Package |
|---|---|---|
| 2. Empirical evidence | [Empirical](https://tlorans.github.io/kiku-value-premium-replication/empirical.html) | `kiku_value_premium.empirical` |
| 3. The long-run risks model | [Model](https://tlorans.github.io/kiku-value-premium-replication/model.html) | `kiku_value_premium.model` |
| 4. Calibration | [Calibration](https://tlorans.github.io/kiku-value-premium-replication/calibration.html) | `kiku_value_premium.calibration` |
| 5. Asset pricing implications | [Implications](https://tlorans.github.io/kiku-value-premium-replication/implications.html) | `kiku_value_premium.implications` |

[Installation](https://tlorans.github.io/kiku-value-premium-replication/installation.html) · [API](https://tlorans.github.io/kiku-value-premium-replication/api.html) · [Other portfolios](https://tlorans.github.io/kiku-value-premium-replication/generalization.html)

## Install

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
uv pip install -e ".[fast]"   # Numba on the Euler loops
uv pip install -e ".[data]"   # WRDS + figures
```

Core install (numpy, scipy, pandas) solves her Table II calibration with no secrets.

Section 2 (Table I, Figures 1–4) needs `[data]` and a repo-root `.env`:

```
WRDS_USERNAME=...
WRDS_PASSWORD=...
```

See `.env.example`. The file is gitignored. `connect_wrds()` raises if the extra or the keys are missing. `model`, `calibration`, and `implications` never import `wrds`.

## Run

```bash
uv run python examples/run_paper.py
```

Walks her order. Without WRDS it skips Section 2, prints why, and continues from Table II. The example uses `n_x=15` so it finishes; her grid is `n_x=30`.

```python
from kiku_value_premium.model import get_table_ii_params, solve_analytical, print_value_premium

print_value_premium(solve_analytical(get_table_ii_params()))
```

Value’s long-run leverage is $\phi = 6.2$ against growth’s $2.6$. Calibration uses cash-flow moments only; return premia never enter.

## Citation

Kiku, D. (2006). *Is the Value Premium a Puzzle?* Job Market Paper, Duke University / Wharton.

Bansal, R., and A. Yaron. (2004). “Risks for the Long Run.” *Journal of Finance*.

## License

MIT
