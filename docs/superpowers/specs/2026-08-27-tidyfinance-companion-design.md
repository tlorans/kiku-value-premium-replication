# lrrcs as a tidyfinance companion

Date: 2026-08-27
Status: approved design (pending spec review)
Version: 0.5.0

## Goal

Make `lrrcs` feel like an extension of [py-tidyfinance](https://github.com/tidy-finance/py-tidyfinance): a required dependency, a flat public API, empirical plumbing through tidyfinance, and docs that show the two packages used together. `lrrcs` stays the long-run-risks / Kiku-style claims layer. It does not re-export tidyfinance and does not fork it.

## Non-goals

- Re-exporting `tidyfinance` symbols from `lrrcs`
- Migrating the paper site to Great Docs
- Switching the build backend to hatchling
- Adopting Ruff 80-column as a blocking constraint
- Importing tidyfinance private names (`_use_backend`, `_download_*`, …)
- Adding `lrr.set_backend`
- Keeping `kiku_value_premium`, `connect_wrds`, or Python 3.9–3.10

## Relationship

Users import both packages:

```python
import tidyfinance as tf
import lrrcs as lrr
```

```
user code
  ├── import tidyfinance as tf    # data, WRDS, sorts, backend
  └── import lrrcs as lrr         # long-run risks + Kiku-style claims
         └── depends on tidyfinance (public API only)
```

## Package layout

`src/lrrcs/` is the only installable package. Move the current implementation out of `src/kiku_value_premium/` into `src/lrrcs/` (real modules, not re-export shims). Delete `src/kiku_value_premium/`.

```
src/lrrcs/
  __init__.py          # auto-discover public functions/classes
  _backend.py          # local pandas/polars conversion at the empirical boundary
  empirical/
  model/
  calibration/
  implications/
```

Submodules remain importable (`import lrrcs.model`) for organization. The documented path is the package root.

## Dependencies

`pyproject.toml`:

- `requires-python = ">=3.11"` (tidyfinance requires 3.11)
- required: `tidyfinance>=0.5.0`, `numpy>=1.26`, `scipy>=1.7`, `pandas>=2.2` (direct pandas/numpy pins must not sit below tidyfinance 0.5.0)
- `[fast]`: `numba>=0.56`
- `[data]`: `matplotlib`, `pyarrow` only. Drop the `wrds` package and `python-dotenv`; tidyfinance owns credentials and SQL.
- version `0.5.0`

Empirical modules may import `tidyfinance` and call only public names: `download_data`, `assign_portfolio`, `breakpoint_options`, `compute_breakpoints`, `set_wrds_credentials`, `get_wrds_connection`, `get_backend`, `set_backend`. Model, calibration, and implications do not import tidyfinance.

## Public API

`import lrrcs as lrr` then `lrr.<name>(...)`.

Root `__init__.py` auto-discovers functions and classes from public (non-`_`) submodules, following tidyfinance:

- skip dunders
- skip `_`-prefixed names
- skip constants
- skip objects not defined in `lrrcs`
- skip third-party re-exports

Then wrap the data-bearing empirical functions listed below so they honor `tf.get_backend()`.

### Root names that stay

Model: `ModelParams`, `PreferencesParams`, `ConsumptionParams`, `DividendParams`, `get_table_ii_params`, `get_default_params`, `EpsteinZinPreferences`, `Dynamics`, `StateGrid`, `ModelSolver`, `AnalyticalSolution`, `solve_analytical`, `print_long_short_premium`, `resolve_legs`.

Calibration: `estimate_long_run_leverage`, `calibrate_from_data`, `get_table_ii_dividends`, `simulate_cashflow_moments`.

Implications: `compute_asset_pricing_moments`, `print_asset_pricing_moments`, `figure_lr_premium`, `figure_mean_pd`, `figure5`.

Empirical: `build_annual_panel`, `table_i`, `table_vi_data`, `figure1`, `figure2`, `figure3`, `figure4`, `EmpiricalDataError`.

### Root names that go away in 0.5.0

- the `kiku_value_premium` package
- `connect_wrds`
- `print_value_premium` (use `print_long_short_premium`)
- exported constants `START`, `END`, `FIGURE2_START`, `ROLE_ALIASES`

Sample years become default arguments: `build_annual_panel`, `table_i`, and `table_vi_data` default to 1930–2003; `figure2` defaults to 1952–2003.

### Not re-exported

Anything from tidyfinance. Users call `tf.download_data` and `tf.set_wrds_credentials` themselves when they need those helpers directly.

### Style

NumPy-style docstrings on public functions. Examples use fenced `python` blocks, not doctest `>>>` prompts.

## Typical use

```python
import tidyfinance as tf
import lrrcs as lrr

tf.set_wrds_credentials()
panel = lrr.build_annual_panel()
sol = lrr.solve_analytical(lrr.get_table_ii_params())
lrr.print_long_short_premium(sol)
```

## Empirical rewrite

`lrr.build_annual_panel()` remains the one-shot 1930–2003 reconstruction. It no longer uses the `wrds` Python package or ad-hoc SQL against `connect_wrds()`.

### Through tidyfinance

| Need | Call |
|---|---|
| Credentials | User calls `tf.set_wrds_credentials()` once |
| CRSP monthly 1925–2003 | `tf.download_data("WRDS", "crsp_monthly", start_date, end_date, version="v1", additional_columns=["retx"])` so Campbell–Shiller still has capital-gain returns |
| Compustat / CCM | `tf.download_data("WRDS", "compustat_annual", ...)` and `"ccm_links"` |
| BM quintiles | June book-to-market on the merged file; `tf.assign_portfolio(..., breakpoint_options=tf.breakpoint_options(n_portfolios=5, breakpoints_exchanges="NYSE"))` |

`version="v1"` is required for the historical CRSP monthly file used in the replica sample. If `retx` is named differently on that extract, pass the v1 column name via `additional_columns` and normalize to `retx` inside `lrrcs`.

### Stay in lrrcs

- Campbell–Shiller dividends from `ret` / `retx`
- Davis–Fama–French historical book equity (Ken French zip)
- Delisting on `retx` (tidyfinance already adjusts `ret`; we still apply the Fama–French −30% rule to performance delists 400–599 on the capital-gain side)
- CRSP index files `msi` (`vwretd` / `vwretx`) and `mcti` (T-bill / CPI) if tidyfinance has no public dataset covering 1925–2003
- NIPA consumption (existing annual loader)
- Annual compounding, deflators, Table I / Table VI / figures

Index-file leftovers that still need SQL use `tf.get_wrds_connection()`. No second credential scheme and no direct `wrds.Connection`.

Parquet cache under `data/raw/` stays. `refresh=True` still means “hit WRDS again.”

### Replica contract

The function still targets the printed 1930–2003 moments. Goldens are rematched after the swap. If v1 + `retx` or delisting differs from today’s extracts, fix our side (extra columns, post-processing) until the replica sits inside the printed bands. Do not change the paper numbers to follow tidyfinance.

## Backend

Data-bearing empirical functions honor `tf.get_backend()` / `tf.set_backend(...)`. Default is pandas, matching tidyfinance today.

Wrap at the `lrrcs` package boundary only. Accept pandas or polars in; return the active backend’s frame type. Implement conversion in `lrrcs._backend` (private). Do not import `tidyfinance.backend._use_backend`.

Empirical internals may stay pandas. A convert on the `tf.download_data` path is acceptable. There is no `lrr.set_backend`.

Do not wrap: model, calibration, implications (numpy / dataclasses), or matplotlib figure helpers (`figure1`–`figure5`, `figure_lr_premium`, `figure_mean_pd`).

Data-bearing wrap list: `build_annual_panel`, `table_i`, `table_vi_data`. Extend the list if another public empirical function starts returning a frame.

## Errors

- Missing WRDS credentials: `EmpiricalDataError` whose message tells the user to call `tf.set_wrds_credentials()`.
- Failed Ken French download or empty historical book-equity parse: `EmpiricalDataError` with a specific message.
- Missing `[data]` extras when a figure or parquet cache needs matplotlib/pyarrow: message to install `lrrcs[data]`.
- No silent fallback to the old `wrds` package.
- Model/calibration keep current `ValueError` behaviour (length mismatch, empty series, …).

## Tests

Default CI stays `pytest -m "not wrds"`.

- Patch `tidyfinance.download_data` (and assignment helpers) with fixtures so the new panel path runs without credentials.
- Keep model, calibration, implications, and construction-fixture tests; import from `lrrcs`, not `kiku_value_premium`.
- API layout tests: version `0.5.0`; `lrr.solve_analytical` and `lrr.build_annual_panel` exist at the root; `kiku_value_premium` and `connect_wrds` are absent; no `print_value_premium` at the root.
- Rematch Table I / Table VI / figure goldens after the tidyfinance swap. Printed-paper bands remain the target.
- One backend test: a data-bearing function returns pandas or polars according to `tf.set_backend`.
- Docs tests that grep for import names require `import lrrcs as lrr` and `import tidyfinance as tf` on the package pages, and `lrr.` calls (not `from lrrcs.model import` as the documented form).
- Live WRDS tests remain `@pytest.mark.wrds`.

## Documentation

Keep Just the Docs and the replica narrative. `_config.yml` already excludes `superpowers/`, so this spec stays off the site.

### Package pages (rewrite)

`docs/installation.md`, `docs/api.md`, `docs/package.md`, `README.md`:

- Companion framing: tidyfinance gets data and sorts; `lrrcs` calibrates cash flows and prices claims.
- Python ≥ 3.11, required `tidyfinance`, editable install via `uv`.
- Side-by-side `import tidyfinance as tf` and `import lrrcs as lrr`.
- WRDS setup is `tf.set_wrds_credentials()`.
- API page is a root-function map, not four submodule tables.
- `[fast]` and `[data]` as above.

### Replica pages (restyle code, keep prose)

Update every page that currently shows `kiku_value_premium` or `from lrrcs.<subpackage> import` so the working examples are `tf` + `lrr` side by side. Paper prose, printed tables, and figures stay.

| Page | Code restyle |
|---|---|
| `empirical.md` | Show `tf.set_wrds_credentials()`, tidyfinance downloads/sorts as plumbing, then `lrr.build_annual_panel()`, `lrr.table_i()`, figures. State that Campbell–Shiller and historical BE stay in `lrrcs`. |
| `model.md` | `import lrrcs as lrr` then `lrr.get_table_ii_params()`, `lrr.EpsteinZinPreferences`, `lrr.Dynamics`, `lrr.ModelSolver`, `lrr.solve_analytical`, `lrr.print_long_short_premium`. |
| `calibration.md` | `lrr.get_table_ii_dividends()`, `lrr.calibrate_from_data(...)`, `lrr.estimate_long_run_leverage(...)`. |
| `implications.md` | `lrr.ModelSolver`, `lrr.compute_asset_pricing_moments`, `lrr.figure_lr_premium`. |
| `time-series.md`, `cross-section.md` | Same flat `lrr.` calls; cross-section may show `tf` only where the panel is built. |
| `further.md`, `climate.md`, `other-risk-premia.md`, `generalization.md` | `lrr.calibrate_from_data(dc, long=..., short=..., market=...)` then solve. |
| `index.md` | Short companion example at the top. |

Do not rewrite the economic argument on those pages. The change is the working language of the package, not the paper.

### Examples

`examples/*.py` switch to `import lrrcs as lrr`. Drop `print_value_premium` and `kiku_value_premium`.

## Out of scope this round

- Publishing to PyPI (install remains git/editable unless already published)
- Changing numerical solvers, Table II defaults, or preference parameters
- Climate/other-premia data construction beyond import/docs restyle
- Great Docs, hatchling, Ruff-only formatting pass
)
