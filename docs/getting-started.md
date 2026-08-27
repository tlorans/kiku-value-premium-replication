---
title: Getting started
nav_order: 2
---

# Getting started
{: .no_toc }

1. TOC
{:toc}

This book is a companion to [Tidy Finance](https://www.tidy-finance.org/). tidyfinance gets CRSP, Compustat, and sorts. `lrrcs` calibrates cash-flow loadings on long-run consumption risk and prices the claims. Average returns never enter the cash-flow step. Run the chunks **in order**.

## Install

Python 3.11+. Clone the repository and install in editable mode with `uv`.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

```python
import numpy as np
import tidyfinance as tf
import lrrcs as lrr

lrr.__version__, tf.__name__
```

You now have both packages. This first run uses only `lrrcs`. You will need tidyfinance in [Financial data]({{ '/financial-data.html' | relative_url }}) for CRSP and Compustat.

## Table II, by hand

Kiku (2006, Table II) is the default household: Epstein–Zin preferences, a persistent expected-growth state $$x_t$$, and three dividend claims (growth, value, market). The numbers are monthly.

```python
delta, gamma, psi = 0.999, 10.0, 1.5
theta = (1.0 - gamma) / (1.0 - 1.0 / psi)
mu_c, rho, phi_x, sigma = 0.0015, 0.98, 0.032, 0.0064
phi = {"growth": 2.6, "value": 6.2, "market": 2.8}
theta, rho, phi
```

```text
(-27.0, 0.98, {'growth': 2.6, 'value': 6.2, 'market': 2.8})
```

$$\theta\neq 1$$ because $$\gamma\neq 1/\psi$$. Under power utility that gap is zero and news about $$x_t$$ is not priced. Value’s monthly loading on $$x_t$$ is 6.2; growth’s is 2.6. That ranking — not the six-percent return gap — is what the model will turn into a premium.

`lrr.get_table_ii_params()` is those numbers as a `ModelParams` object. `lrr.solve_analytical` linearizes log price–dividend in $$x_t$$ and returns the long-run premium of each claim.

```python
params = lrr.get_table_ii_params()
params.prefs.gamma, params.cons.rho
params.dividends["value"].phi, params.dividends["growth"].phi
sol = lrr.solve_analytical(params)
lrr.print_long_short_premium(sol)
```

```text
Approximate annualized long-run risk premia:
  growth  :   0.39%
  value   :   0.80%
  market  :   0.34%
Value-growth spread from long-run risks: 0.40%
A1 (PD elasticity to x): growth=43.1, value=88.9
Price of long-run risk Lambda_eps = 5.95
```

**What that did.** It loaded Table II, solved the linearized model, and printed the long–short premium the Euler equation assigns. You did not estimate anything.

**What that did not do.** It did not match that premium. Average returns never entered. It did not touch WRDS.

The 0.40 percent here is only the *long-run piece* of the value premium (the part that comes from $$A_1\times x$$-news). The full Euler-equation gap is about 5.3 percent against about 6 percent in the data — that comparison is [Value versus growth]({{ '/cross-section.html' | relative_url }}).

## Extras

Numba (`[fast]`), matplotlib / polars / plotnine / parquet (`[data]`), and WRDS credentials live on [Installation]({{ '/installation.html' | relative_url }}). You do not need them for the five lines above.

## Key takeaways

- Two imports: `tidyfinance as tf` and `lrrcs as lrr`.
- Table II is a cash-flow calibration. Returns are not in it.
- `solve_analytical` is a first look at prices, not an estimation.

Next: [Financial data]({{ '/financial-data.html' | relative_url }}), where we actually download NIPA and construct Campbell–Shiller dividends.
