# Follow-along Financial data and The market

Date: 2026-08-27
Status: draft (pending user review)
Version: 0.5.0 docs + two calibration helpers

## Goal

Make two book pages work like [Tidy Finance chapters](https://www.tidy-finance.org/chapters/): the reader follows along in polars and plotnine, then sees the same computation as an `lrr.` call.

1. A **Financial data** page that retrieves the series later chapters need, without repeating Tidy Finance’s WRDS/CRSP/Compustat material.
2. A rewritten **The market** page that shows what long-run risk \(x_t\) is, how to estimate it, how to calibrate dividend parameters, how to simulate cash flows, and how to check **return and price** moments.

This spec supersedes, for those two pages and for nav order:

- `docs/superpowers/specs/2026-08-27-lrrcs-book-docs-design.md` — The market’s four H2s (`Data` / `Calibrate cash flows` / `Solve` / `Compare pricing moments`), The market as a compact recipe pass, and the nav_order table that puts The market at 4.

It does **not** reopen the tidyfinance companion package design, Table II numbers, solvers, or Value versus growth.

## Non-goals

- Restyling Value versus growth, Getting started, or Cash flows, then prices beyond nav, “next” links, and a Financial data pointer
- Quarto, notebooks, or leaving Just the Docs
- Plotnine helpers in the library (`lrr.figure_*` for tutorial charts)
- A public price-path simulator (`simulate_asset_pricing_moments` or similar)
- Wrapping `load_consumption` / `campbell_shiller_annual` for `tf.get_backend()`
- Changing Table II defaults, preference parameters, or numerical solvers
- Live WRDS or live FRED as a requirement to finish either page
- PyPI, hatchling, Ruff-only pass
- An R sibling

## Relationship to the existing book

Keep:

- Site title `Long-run risks`; Just the Docs; `superpowers/` excluded from the site
- Thesis: cash flows in, prices out. Average returns never enter calibration
- Documented imports `import tidyfinance as tf` and `import lrrcs as lrr` on every page that already has them
- Value versus growth: title, URL, four H2s, printed 7.81 / 13.88 / 5.3
- Cash flows, then prices: map of the four steps, IMRS/Euler, skeleton
- Getting started: install + five-line solve; still no WRDS dump
- Printed market numbers: data \(E[R]=8.56\), model \(7.53\); \(E[\mathrm{pd}]\) 3.34 vs 3.24
- Replica sample 1930–2003 and shipped `data/*.csv`

Add the follow-along contract only on Financial data and The market.

## Spine and nav

| `nav_order` | Page | File | URL |
|---|---|---|---|
| 1 | Home | `docs/index.md` | `/` |
| 2 | Getting started | `docs/getting-started.md` | `/getting-started.html` |
| 3 | Financial data | `docs/financial-data.md` (new) | `/financial-data.html` |
| 4 | Cash flows, then prices | `docs/cash-flows-then-prices.md` | `/cash-flows-then-prices.html` |
| 5 | The market | `docs/time-series.md` | `/time-series.html` |
| 6 | Value versus growth | `docs/cross-section.md` | `/cross-section.html` |
| 7 | Package | `docs/package.md` | `/package.html` |

No parent on the book chapters. Installation and API stay children of Package (`nav_order` 1 and 2 under that parent).

Home and Getting started link Financial data. Getting started’s “Next” becomes Financial data (not Cash flows, then prices). Package’s book list includes Financial data. README docs table includes Financial data.

## Pedagogy (Financial data and The market only)

Documented imports, in this order when all four appear:

```python
import polars as pl
import plotnine as p9
import tidyfinance as tf
import lrrcs as lrr
```

Fenced `python`, not doctest `>>>`. Public names at `lrr.`; no `from lrrcs.model import` (or other submodule imports) as the documented form.

On each worked step:

1. Show the computation in polars / numpy / plotnine.
2. Repeat it as `lrr.<name>(...)`.

plotnine is for new tutorial charts. Existing paper SVGs under `docs/figures/` may remain; The market rewrite does not need `lr_premium_decomposition.svg`. Core install still solves Table II with no extras.

## Financial data

New `docs/financial-data.md`. Title and H1: **Financial data**. Tutorial voice.

Purpose: show how to retrieve the series The market (and later Value versus growth) uses. Not a WRDS tutorial and not a calibration chapter.

### Link out, do not redo

- [Accessing and managing financial data](https://www.tidy-finance.org/chapters/accessing-and-managing-financial-data.html)
- [WRDS, CRSP, and Compustat](https://www.tidy-finance.org/chapters/wrds-crsp-and-compustat.html)
- [Installation]({{ '/installation.html' | relative_url }}) for `tf.set_wrds_credentials()`

Show **one** `tf.download_data` call (CRSP monthly or Compustat annual) so the companion pattern is visible, then stop. No TRACE, no FISD, no Fama–French factor recap, no Compustat variable dictionary.

### What this page introduces

| Series | Why it is new here | Raw then package |
|---|---|---|
| Real per-capita nondurables + services growth | NIPA on FRED | Build \(\log((ND+S)/\mathrm{pop})\) growth in polars from the FRED CSV, then `lrr.load_consumption()` |
| PCE deflator | Same family | Short note, then `lrr.load_deflator()` |
| Campbell–Shiller dividends | CRSP is in Tidy Finance; \(D_t=(r_t-r_t^x)V_{t-1}\) is not | Toy identity on `ret` / `retx`, then `lrr.campbell_shiller_annual` |
| Real T-bill | CRSP index / CPI | Mention `mcti`, then the shipped `rf` file |
| Annual claims panel | BM quintiles + CS dividends, 1930–2003 | Point at Tidy Finance sorts; then `lrr.build_annual_panel()` / `lrr.table_i()` |

Davis–Fama–French historical book equity is one sentence inside the panel block, not its own section.

### Runnable path (no WRDS)

After each retrieval sketch, read the replica files:

```python
dc = pl.read_csv("data/consumption_annual.csv")
panel = pl.read_csv("data/annual_panel.csv")  # year, claim, ret, dgrowth, pd
rf = pl.read_csv("data/rf_annual.csv")
```

The book window is 1930–2003 on those files. Live FRED would extend past 2003 and is not the replica sample. `refresh=True` on `build_annual_panel` is documented as optional.

### Charts (three, plotnine, from the CSVs)

1. Annual \(\Delta c\), 1930–2003
2. Market \(\Delta d\) against \(\Delta c\)
3. Market \(\log(P/D)\)

No model lines. No \(x_t\) overlay (that belongs on The market).

### Close

The market reads these three files. Next: Cash flows, then prices, or skip to The market.

## The market

Rewrite `docs/time-series.md`. Title and H1 stay **The market**. URL unchanged. Opening question stays: can this household price the value-weighted market?

No `## Data` H2. Open by reading the three shipped files in polars. Then these H2s, in this order, with these exact strings:

1. `## What long-run risk is`
2. `## Estimate x_t`
3. `## Calibrate dividends`
4. `## Simulate cash flows`
5. `## Solve and check returns and prices`

### What long-run risk is

Consumption growth is not white noise. State the Bansal–Yaron process:

\[
\Delta c_{t+1}=\mu+x_t+\sigma_t\eta_{t+1},\qquad x_{t+1}=\rho x_t+\varphi_x\sigma_t e_{t+1}.
\]

\(x_t\) is a small persistent expected-growth piece. News about it is long-run risk. Epstein–Zin with \(\psi\neq 1/\gamma\) prices that news; a claim’s \(\phi\) is its loading on \(x_t\).

**Chart.** Raw annual \(\Delta c\) against the two-year MA of lagged \(\Delta c\). The smooth line is the annual picture of \(x_t\). This first plot may be written before the package call (definition, not API). One sentence: Table II’s monthly \(\rho=0.98\) is the same object on a finer clock.

### Estimate x_t

**Proxy (the estimator we keep).** Polars `shift` + rolling mean of \(\Delta c\), window 2. Then `lrr.expected_growth_proxy(dc, window=2)`. Overlay the proxy.

**Filter (the link to the solver).** Univariate Kalman / AR(1) on annual \(\Delta c\):

\[
y_t=\mu+x_t+v_t,\qquad x_{t+1}=\rho x_t+w_t.
\]

Raw numpy/scipy, then `lrr.filter_expected_growth(dc)`. Overlay \(\hat x_t\). Report the filtered **annual** \(\rho\). The solver iterates the monthly counterpart \(0.98\). Do **not** take \(\phi\) or Table II numbers from this filter.

### Calibrate dividends

Kiku (2006) equation (19): \(\Delta d_t=d_0+\tilde\phi\,\mathrm{MA}(\Delta c,2)+\varepsilon_t\).

OLS of market `dgrowth` on the proxy (polars/numpy). Then `lrr.estimate_long_run_leverage` and `lrr.calibrate_from_data(..., market=dd, frequency="annual", window=2)`. Show \(\mu\), \(\varphi_\sigma\), \(\alpha\) from that helper.

**Annual vs monthly, said once.** The slope \(\tilde\phi\) (printed market about \(0.66\)) is the ranking check. The solver wants monthly \(\phi\). Table II locks market \(\mu=0.0012\), \(\phi=2.8\), \(\varphi_\sigma=7.5\), \(\alpha=0.55\). Simulation and pricing below use `lrr.get_table_ii_params()`, not the annual slope as a monthly loading. Average returns never enter.

### Simulate cash flows

Write the \(\Delta c\) / \(\Delta d\) recursion once. Then `lrr.simulate_cashflow_moments(...)`. Compare to the sample from the CSVs. Consumption target in the prose: mean / vol / AC1 about 1.96, 2.20, 0.44 in the data vs 1.86, 2.16, 0.43 from the model (1000 samples of 74 years). The fenced demo may use a small `n_sims` (for example 20) so the snippet is runnable. If cash-flow moments fail, stop.

### Solve and check returns and prices

`get_table_ii_params` → `solve_analytical` and/or `ModelSolver` → `compute_asset_pricing_moments` / `print_asset_pricing_moments`.

Keep the table: market \(E[R]\) 8.56 vs 7.53, \(E[\mathrm{pd}]\) 3.34 vs 3.24, return vol 20.1 both, risk-free 0.91 vs 1.58. Success is **both** return and price columns close. A match on returns with a wrong \(P/D\) is a fail.

**Path plot (chapter code, not a new public function).** One simulated monthly path via `Dynamics` (`lrr.Dynamics` is already at the root). Log price–dividend from the analytical map, written out in the chapter:

\[
z_t=\bar z+A_1 x_t+A_2(\sigma_t^2-\bar\sigma^2)
\]

with \(\bar z\), \(A_1\), \(A_2\) from `lrr.solve_analytical(...)`. plotnine: \(x_t\), market \(\Delta d\), model \(\log(P/D)\). Do not add `simulate_asset_pricing_moments`.

Next: Value versus growth (unchanged).

## Package API

Two new root names. Auto-discovery from `src/lrrcs/calibration/` exports them. They do not import tidyfinance. They accept array-like input (`list`, numpy, pandas, polars) via `np.asarray(...).ravel()`. Return numpy (and Python floats in the dict).

New module: `src/lrrcs/calibration/expected_growth.py`.

Refactor `estimate_long_run_leverage` to build its MA by calling `expected_growth_proxy`. OLS and the returned scalar must not change.

### `expected_growth_proxy(dc, window=2) -> np.ndarray`

Same length as `dc`. Entry \(t\) is `mean(dc[t-window:t])` for \(t \ge\) `window`, `nan` before that. `window < 1` or `len(dc) <= window` → `ValueError`.

### `filter_expected_growth(dc) -> dict`

Univariate Kalman on (typically annual) consumption growth:

\[
y_t=\mu+x_t+v_t,\qquad x_{t+1}=\rho x_t+w_t,
\]

\(v_t\sim N(0,r)\), \(w_t\sim N(0,q)\), \(x_0=0\).

- \(\mu=\overline{y}\)
- \(\rho, q, r\) by MLE (`scipy.optimize`), bounds \(\rho\in(0, 0.999)\), \(q,r>0\)
- Starting values: \(\rho_0=\mathrm{AC1}(y)\), \(q_0=r_0=\mathrm{Var}(y)/2\)
- Filtered means \(E[x_t\mid y_{1:t}]\), not the smoother
- If MLE does not converge, raise `ValueError`
- If `len(dc) < 8`, raise `ValueError`

Return keys, exactly:

```python
{
    "x": np.ndarray,  # length n
    "mu": float,
    "rho": float,     # annual (or sample-frequency) persistence, not monthly 0.98
    "q": float,
    "r": float,
    "loglik": float,
}
```

This dict is not an input to `calibrate_from_data` or `get_table_ii_params`.

NumPy-style docstrings. Examples use fenced `python` with `import lrrcs as lrr`.

## Extras and install

`pyproject.toml` `[project.optional-dependencies] data` becomes:

```toml
data = ["matplotlib", "pyarrow", "polars", "plotnine"]
```

Core required deps unchanged. `docs/installation.md` lists polars and plotnine under `[data]`. Getting started still does not mention them.

## Tests

### Docs (`tests/test_docs.py`)

- Required pages include `financial-data.md`
- `docs/financial-data.md`: title/H1 Financial data; no parent; `nav_order: 3`
- Nav: Cash flows then prices 4, The market 5, Value versus growth 6, Package 7
- Home and Getting started contain `financial-data`
- Financial data contains both Tidy Finance URLs (the `accessing-and-managing-financial-data` and `wrds-crsp-and-compustat` paths), `data/consumption_annual.csv`, `data/annual_panel.csv`, `data/rf_annual.csv`, `import polars as pl`, `import plotnine as p9`, and `import lrrcs as lrr`
- The market: five H2s in the order listed above (assert by `text.index`); **do not** require `## Data`; keep `8.56` and `7.53`; require `expected_growth_proxy`, `filter_expected_growth`, `simulate_cashflow_moments`, `compute_asset_pricing_moments`; require `import polars as pl` and `import plotnine as p9`; still ban `kiku_value_premium` and `from lrrcs.model import`
- Value versus growth: four H2s and 7.81 / 13.88 / 5.3 unchanged
- Package pages still show `import tidyfinance as tf`
- README lists Financial data

### Unit tests (`tests/test_calibration.py` or a new `tests/test_expected_growth.py`)

- Proxy: `dc = [1, 2, 3, 4]`, `window=2` → `[nan, nan, 1.5, 2.5]` (compare with `np.testing.assert_allclose` and `equal_nan=True`)
- Proxy: `window=0` or series of length 2 with `window=2` → `ValueError`
- Proxy: polars Series in, `numpy.ndarray` out
- After refactor, `estimate_long_run_leverage` on a fixture series matches its current value
- Filter: synthetic `y_t = μ + x_t + v_t` with known annual \(\rho\approx 0.6\); recovered `rho` in a loose band (e.g. 0.3–0.9); `len(x)==len(y)`; `std(x) < std(y)`
- Filter: series shorter than 8 → `ValueError`
- No live FRED or WRDS

API layout: `lrr.expected_growth_proxy` and `lrr.filter_expected_growth` exist at the root (`tests/test_api_layout.py`).

## Files

**Create**

- `docs/financial-data.md`
- `src/lrrcs/calibration/expected_growth.py`
- `tests/test_expected_growth.py` (or fold into `tests/test_calibration.py`)

**Modify**

- `docs/time-series.md` — full rewrite of body; title/URL unchanged; `nav_order: 5`
- `docs/index.md` — link Financial data; do not turn Home into an essay
- `docs/getting-started.md` — Next → Financial data; `nav_order` stays 2
- `docs/cash-flows-then-prices.md` — `nav_order: 4`; optional one-line pointer to Financial data for retrieval
- `docs/cross-section.md` — `nav_order: 6` only (content unchanged)
- `docs/package.md` — `nav_order: 7`; list Financial data
- `docs/installation.md` — `[data]` extras
- `docs/api.md` — two new names on the root-function map
- `README.md` — docs table
- `pyproject.toml` — `[data]` extras
- `src/lrrcs/calibration/leverage.py` — MA via `expected_growth_proxy`
- `tests/test_docs.py` — book contract above
- `tests/test_api_layout.py` — root names
- `tests/test_calibration.py` — leverage still matches if the MA is refactored

**Do not change**

- Solvers, Table II parameter values, `examples/*.py` (unless a docs URL is cited there)
- `docs/cross-section.md` body
- Paper SVGs (unused ones may stay)

## Out of scope this round

- Value versus growth follow-along restyle
- Other sorts, climate, Melin–Zhang
- Backend wrapping of consumption/deflator loaders
- Changing goldens for Table I / Table VI
- Redirects, Quarto, PyPI
