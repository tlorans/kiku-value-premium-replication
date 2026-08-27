---
title: Getting started
nav_order: 2
---

# Getting started
{: .no_toc }

1. TOC
{:toc}

This book is a companion to [Tidy Finance](https://www.tidy-finance.org/). It implements a **general-equilibrium** long-run-risks economy whose objects are **asset prices and risk premia** — valuations (price–dividend ratios) and ex-ante compensations, not only average returns.

tidyfinance gets CRSP, Compustat, and sorts. `lrrcs` maps the low-frequency risks embodied in cash flows into those prices and premia. Average returns never enter the cash-flow step. Run the chunks **in order**.

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

Kiku (2006, Table II) is the default economy: time-non-separable Epstein–Zin preferences, a small but highly persistent component that governs consumption growth ($$x_t$$), time-variation in the conditional volatility of consumption (news about future economic uncertainty), and three claims (growth, value, market) distinguished by the exposure of their dividends to low- versus high-frequency consumption shocks. The numbers are monthly.

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

$$\theta\neq 1$$ because Epstein–Zin preferences break the link between smoothing consumption over time ($$\psi$$) and across states ($$\gamma$$). The marginal rate of substitution then depends not only on present and future consumption, as under power utility, but also on the forward-looking return on the aggregate wealth portfolio. Shocks to the persistent growth-rate component significantly alter investors’ expectations about consumption far into the future, leading to large reactions in stock prices and sizable risk compensations.

Value’s monthly loading on $$x_t$$ is 6.2; growth’s is 2.6. Value firms are highly exposed to long-run consumption shocks; growth firms are driven more by short-lived fluctuations. That dispersion in long-run cash-flow exposure — not the six-percent return gap — is what the equilibrium turns into valuations and premia. Value firms exhibit higher elasticity of their price–dividend ratios to long-run consumption news, and have to provide investors with high ex-ante compensation.

`lrr.get_table_ii_params()` is those numbers as a `ModelParams` object. `lrr.solve_analytical` linearizes log price–dividend in $$x_t$$ and returns both the elasticity of valuations and the long-run risk premium of each claim.

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

**What that did.** It loaded Table II, solved the linearized general-equilibrium model, and printed the long-run risk premia and the elasticity of price–dividend ratios to $$x_t$$. You did not estimate anything.

**What that did not do.** It did not match those premia or those valuations to the data. Average returns never entered. It did not touch WRDS.

The 0.40 percent here is only the long-run *piece* of the value premium. The full Euler-equation gap is about 5.3 percent against about 6 percent in the data, and value’s $$P/D$$ sits below growth’s — both prices and premia. That comparison is [Value versus growth]({{ '/cross-section.html' | relative_url }}).

## Extras

Numba (`[fast]`), matplotlib / polars / plotnine / parquet (`[data]`), and WRDS credentials live on [Installation]({{ '/installation.html' | relative_url }}). You do not need them for the five lines above.

## Key takeaways

- Two imports: `tidyfinance as tf` and `lrrcs as lrr`.
- Table II is a cash-flow calibration: a persistent growth-rate component, time-varying uncertainty, and dividend exposures. Returns are not in it.
- Epstein–Zin breaks the link between smoothing over time and across states, so the MRS depends on the forward-looking return on the aggregate wealth portfolio.
- The equilibrium objects are asset prices and risk premia. `solve_analytical` is a first look at both, including value’s higher $$P/D$$ elasticity.

Next: [Financial data]({{ '/financial-data.html' | relative_url }}), where we actually download NIPA and construct Campbell–Shiller dividends.
