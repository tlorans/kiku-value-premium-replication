# Kiku (2006) Package Revamp

Date: 2026-08-26
Status: draft, pending user review
Repo: `kiku-value-premium-replication`
Version after revamp: 0.3.0 (breaking)

This spec is the source of truth for the package and documentation revamp. It records the design approved in conversation. Implementation starts only after the user accepts this file.

## 1. Identity

This package is a transparent replica of Dana Kiku (2006), "Is the Value Premium a Puzzle?" It implements the Bansal–Yaron long-run risks model with Epstein–Zin preferences, her 1930–2003 value/growth/market construction, her cash-flow-only calibration discipline, and her Tauchen–Hussey numerical solution.

The public API and the GitHub Pages site follow her paper order (Empirical Evidence → Model → Calibration → Asset Pricing Implications). Each section is still a recipe: what she does, what you call, what you should see.

This is not the climate paper. Melin and Zhang, `climate_discount`, overlay, NACE, and `papers/02-mz-firm-dcf` stay out of this repository.

## 2. Locked decisions

- Approach A: paper-section public API; WRDS as an optional `[data]` extra; core install solves the model from Table II with no secrets.
- Kernel: Bansal–Yaron (2004) as in her Section 3. Solver: Tauchen–Hussey product grid, paper default 30 × 4 plus 7-point short-run Gauss–Hermite. Analytical Section 3.4 stays in `model`.
- Sample: 1930–2003 only. Figure 2 is sliced 1952–2003, as in her caption.
- Empirical series: full WRDS reconstruction (CRSP/Compustat), not Ken French headline files. Pre-1962 book equity comes from the Davis–Fama–French / Ken French historical book-equity file because Compustat does not go back to 1930.
- Credentials: repo-root `.env` with `WRDS_USERNAME` and `WRDS_PASSWORD`. Never committed.
- Success for data columns: `|package − printed| ≤ printed Newey–West SE`. Goldens are her print, never our output. If a series cannot be brought inside the band after the construction-audit checklist, stop and ask; do not widen the band; do not switch the headline series to Ken French.
- Model/calibration/implications tests recover her model-column ranking and magnitudes (value premium around 5.3%, value > market > growth expected returns, value log(P/D) < growth, CAPM β_value/β_growth < 1). Those model columns are not on the Table I SE gate.
- Breaking change: origin 0.2.0 six-step flat imports go away. No compatibility shim.
- Package manager: `uv`.
- Local `main` is behind `origin/main` by the GitHub Pages / six-step-recipe commits. Implementation fast-forwards that first, then replaces the six-step site with this design.

## 3. Public API and layout

```
src/kiku_value_premium/
  __init__.py                 # version, section re-exports, recipe docstring
  empirical/
    __init__.py
    wrds.py                   # connect_wrds, EmpiricalDataError
    construction.py           # FF 1993 BM portfolios, DFF book equity
    dividends.py              # Campbell–Shiller / BDL per-share dividends
    consumption.py            # NIPA real per-capita ND+S, PCE deflator
    rates.py                  # 90-day T-bill minus 12-month inflation MA
    tables.py                 # table_i, table_vi_data
    figures.py                # figure1–figure4
    goldens.py                # printed cells from Kiku (2006)
    panel.py                  # build_annual_panel
  model/
    __init__.py
    params.py                 # moved from today's top-level
    preferences.py
    dynamics.py
    discretization.py
    solver.py
    analytical.py             # Section 3.4 log-linear solution
  calibration/
    __init__.py
    leverage.py               # estimate_long_run_leverage (eq. 19)
    from_data.py              # calibrate_from_data (cash-flow moments only)
    table_ii.py               # get_table_ii_dividends, get_table_ii_params
    simulation.py             # simulate_cashflow_moments (Tables III–V)
  implications/
    __init__.py
    moments.py                # compute_asset_pricing_moments (VII–X, VIII)
    figures.py                # figure_lr_premium, figure_mean_pd, figure5
```

Headline public names:

| Section | Import from | Objects |
|---------|-------------|---------|
| 2 | `kiku_value_premium.empirical` | `connect_wrds`, `build_annual_panel`, `table_i`, `table_vi_data`, `figure1`, `figure2`, `figure3`, `figure4`, `START`, `END` |
| 3 | `kiku_value_premium.model` | `ModelParams`, `PreferencesParams`, `ConsumptionParams`, `DividendParams`, `get_table_ii_params`, `EpsteinZinPreferences`, `Dynamics`, `StateGrid`, `ModelSolver`, `solve_analytical` |
| 4 | `kiku_value_premium.calibration` | `estimate_long_run_leverage`, `calibrate_from_data`, `get_table_ii_dividends`, `simulate_cashflow_moments` |
| 5 | `kiku_value_premium.implications` | `compute_asset_pricing_moments`, `print_asset_pricing_moments`, `figure_lr_premium`, `figure_mean_pd`, `figure5` |

`START, END = 1930, 2003` live in `empirical` and are the only sample window.

`calibrate_from_data(dc, dd_by_name, frequency="annual", window=2)` takes consumption growth and a dict of dividend-growth series. It has no argument for returns or premia.

Core dependencies: numpy, scipy, pandas. Optional:

- `[fast]`: `numba>=0.56`
- `[data]`: `wrds`, `python-dotenv`, `matplotlib`
- `[dev]`: pytest, matplotlib, numba

Importing `empirical` without `[data]` raises `EmpiricalDataError` that names the extra and the two `.env` keys. `model`, `calibration`, and `implications` must not import `wrds`.

## 4. Data flow

```
.env
  → connect_wrds()
  → data/raw/          (gitignored CRSP/Compustat extracts)
  → construction + dividends + rates + consumption
  → data/annual_panel.csv   (committable; Growth/Value/Market/RF/Δc, 1930–2003)
  → table_i / table_vi_data / figure1–4
  → SE gate vs empirical.goldens

Table II params
  → Dynamics / calibrate_from_data
  → simulate_cashflow_moments          (III–V)
  → ModelSolver(n_x=30, n_s=4, n_quad=7)
  → compute_asset_pricing_moments      (VII–X, VIII)
  → figure_lr_premium, figure_mean_pd, figure5
```

`build_annual_panel(refresh=False)` reuses `data/raw/` when present. `refresh=True` hits WRDS again. CI never calls WRDS.

## 5. WRDS empirical pipeline

### 5.1 Credentials and errors

Repo-root `.env`:

```
WRDS_USERNAME=...
WRDS_PASSWORD=...
```

`.gitignore` includes `.env` and `data/raw/`. Password is never logged.

`EmpiricalDataError` is raised when:

- `[data]` is not installed
- `.env` is missing or the two keys are empty
- WRDS connection fails and no usable `data/raw/` cache exists
- a required extract comes back empty

If WRDS is down and `data/raw/` exists, `refresh=False` proceeds from cache.

### 5.2 Pulls

| Source | Role |
|--------|------|
| `crsp.msf` + names | Monthly `ret`, `retx`, `prc`, `shrout`; ordinary shares `shrcd` in {10, 11}; NYSE/AMEX/NASDAQ |
| `crsp.msi` | Value-weighted market return with dividends (`vwretd`) |
| `crsp.ccmxpf_linktable` | PERMNO–GVKEY, `linktype` in {LU, LC}, `linkprim` in {P, C} |
| `comp.funda` | Book equity = SEQ + TXDITC − preferred (redemption, else liquidation, else par) |
| Ken French historical book equity | Moody’s / Davis–Fama–French file through 1962 |
| CRSP T-bill and inflation | Real RF = 90-day T-bill − 12-month moving average of inflation |
| FRED / NIPA (public) | Real per-capita nondurables + services; PCE deflator |

### 5.3 Construction (her Section 2.1)

1. Form five book-to-market quintiles at the end of June each year, NYSE breakpoints, NYSE/AMEX/NASDAQ ordinary shares. Growth = bottom quintile, value = top quintile. Market = CRSP value-weighted market.
2. Book-to-market = book equity at the last fiscal year-end of the prior calendar year / December market equity of the prior year.
3. Per-share dividends as Campbell–Shiller (1988) / Bansal–Dittmar–Lundblad (2005): extract yield \(y_{t+1}\) from with-dividend versus without-dividend returns, \(D_{t+1}=y_{t+1}V_t\), \(V_{t+1}=h_{t+1}V_t\), \(V_0=100\).
4. Time-aggregate monthly returns and dividends to calendar years. Convert to real with the PCE deflator. Dividend growth = first difference of log dividends. log(P/D) = end-of-year price / that year’s cumulative dividend.
5. Write `data/annual_panel.csv`. No security-level CRSP in git.

### 5.4 Objects from the panel

- `table_i(panel)` — Panel A means and volatilities, Panel B correlations, Newey–West **8** lags.
- `table_vi_data(panel)` — eq. (19) \(\tilde\phi\) and Panel B innovation correlations. Her Table VI data-column SEs use Newey–West **4** lags; match that lag for Table VI only.
- Figure 1: realized value minus growth, 1930–2003.
- Figure 2: expected value premium (spread projected on lagged P/D and dividend growth of the two portfolios) versus 3-year moving average of squared AR(1) consumption residuals, rescaled to the premium’s mean and SD, **1952–2003**.
- Figure 3: spectral density of consumption growth, ARMA(1,1) versus Bartlett kernel, 1930–2003.
- Figure 4: 3-year moving average of dividend growth versus rescaled consumption, two panels (growth, value), 1930–2003.

## 6. Model, calibration, implications

Unchanged economics, new homes.

**Model.** Epstein–Zin IMRS as her (3). Consumption and dividends as her (6)–(9) / Table II. `ModelSolver` default `n_x=30`, `n_s=4`, `n_quad=7`. `solve_analytical` is the Section 3.4 log-linear elasticities and long-run risk prices.

**Calibration.** Table II is the default. `calibrate_from_data` estimates \(\mu\), \(\tilde\phi\) from eq. (19), \(\alpha\) from residual/consumption-innovation correlation, and \(\varphi_\sigma\) so residual volatility matches. It never sees return premia. `simulate_cashflow_moments` is 1000 monthly samples of 74 × 12 observations, time-averaged to annual, mean and cross-simulation SD, as in her Tables III–V.

**Implications.** Stationary distribution of the solved chain plus short-run quadrature yields expected returns, volatilities, mean log(P/D), RF, Sharpe ratios, CAPM and C-CAPM betas (Table VIII is \(\beta_V/\beta_G\)), and return correlations (Table IX). Figure 5 is the model-implied analogue of Figure 2 on a long simulated sample (her 1000 annual observations).

Table II defaults stay exactly as in today’s `params.py`:

- Preferences: \(\delta=0.999\), \(\gamma=10\), \(\psi=1.5\)
- Consumption: \(\mu=0.0015\), \(\rho=0.98\), \(\varphi_x=0.032\), \(\sigma=0.0064\), \(\nu=0.99\), \(\sigma_w=0.0000017\)
- Growth: \(\mu=0.0009\), \(\phi=2.6\), \(\varphi_\sigma=8.4\), \(\alpha=0.27\)
- Value: \(\mu=0.0019\), \(\phi=6.2\), \(\varphi_\sigma=7.4\), \(\alpha=0.15\)
- Market: \(\mu=0.0012\), \(\phi=2.8\), \(\varphi_\sigma=7.5\), \(\alpha=0.55\)
- Residual correlations: GV 0.20, GM 0.80, VM 0.45

## 7. Documentation

Keep GitHub Pages (Cayman theme + MathJax). The site is the recipe.

| Page | Content |
|------|---------|
| `docs/index.md` | Identity, four-section recipe at a glance |
| `docs/installation.md` | `uv` install, `[fast]`, `[data]`, `.env`, what works without WRDS |
| `docs/empirical.md` | Section 2 recipe + Table I + Figures 1–4 |
| `docs/model.md` | Section 3 recipe + IMRS + BY process + solver + analytical 3.4 |
| `docs/calibration.md` | Section 4 recipe + eq. (19) + Tables II–V |
| `docs/implications.md` | Section 5 recipe + Tables VII–X + mechanism figures + Figure 5 |
| `docs/api.md` | Public names by subpackage |
| `docs/generalization.md` | Other portfolios via `calibrate_from_data`. No climate kernel |

Delete `docs/KIKU_RECIPE.md`, `docs/results.md`, and `docs/examples.md` as top-level pages. `README.md` is a short pointer (identity, install, link to Pages), not a second recipe.

Each section page has three blocks: what she does; what you call; what you should see (printed cell + package output / figure).

Figures are written to `figures/` and copied to `docs/figures/` so Pages does not call WRDS.

`examples/run_paper.py` runs Sections 2–5 in order. If `[data]` or `.env` is missing, it skips Section 2, says so, and continues from Table II. Keep `examples/demo.py` and `examples/calibrate_any_portfolio.py` as links from installation and generalization.

## 8. Tests and the SE-matching gate

Goldens in `src/kiku_value_premium/empirical/goldens.py`, typed from her print.

**Gate rule.** For every data-column cell below, `|package − printed| ≤ printed SE`. Failed tests do not edit goldens.

Table I (Newey–West 8 lags), percent except log(P/D):

| Asset | E[R] | σ(R) | E[Δd] | σ(Δd) | E[log P/D] |
|-------|------|------|-------|-------|------------|
| Growth | 7.81 (1.98) | 20.2 (2.00) | 0.68 (1.25) | 13.9 (2.24) | 3.61 (0.18) |
| Value | 13.88 (1.74) | 29.9 (4.34) | 3.63 (3.06) | 18.1 (2.69) | 3.25 (0.12) |
| Market | 8.56 (1.79) | 20.1 (2.23) | 0.85 (0.95) | 10.9 (2.41) | 3.34 (0.13) |

Table I Panel B: return correlations GV 0.75 (0.05), GM 0.95 (0.01), VM 0.87 (0.04); Δd correlations GV 0.32 (0.17), GM 0.80 (0.09), VM 0.53 (0.10).

Table III data: E[Δc] 1.96 (0.32), σ 2.20 (0.45), AC1 0.44 (0.12), AC2 0.16 (0.15).

Table VI data (Newey–West **4** lags): \(\tilde\phi\) growth −0.38 (1.34), value 2.16 (1.44), market 0.66 (1.20). Innovation correlations: growth 0.37 (0.14), value 0.30 (0.07), market 0.58 (0.15).

**Layer 1 — units, no panel.** Tiny fixtures for book-equity formula, Campbell–Shiller dividends, NYSE breakpoints, Newey–West, eq. (19), `calibrate_from_data` signature has no returns, Table II defaults, analytical \(\phi_V>\phi_G\), solver on a 5×2 grid, public imports from the four subpackages. Assert the package does not import `climate_discount` or `corpo_research_papers`.

**Layer 2 — committed `data/annual_panel.csv`.** Default `uv run pytest`. This is the SE gate for Table I, Table III data, and Table VI data. Figure helpers write non-empty PDF and SVG. Window 1930–2003; Figure 2 sliced 1952–2003. Model tests from Table II: simulated III–V recover her model-column ranking; numerical VII–X recover value > market > growth expected returns, value log(P/D) < growth, Table VIII \(\beta_V/\beta_G < 1\).

**Layer 3 — live WRDS.** `pytest -m wrds`, skipped without `.env`. `refresh=True` rebuilds a panel whose Table I cells still pass the gate. Not in default CI.

**Construction-audit checklist** when Layer 2 fails, in order: share-code / exchange filters → NYSE breakpoints → DFF book-equity merge → Campbell–Shiller dividends → PCE deflator → calendar-year aggregation. Then stop and ask.

## 9. Files created or moved

Create:

- `src/kiku_value_premium/empirical/` (all modules in §3)
- `src/kiku_value_premium/model/` (moved current model modules)
- `src/kiku_value_premium/calibration/` (moved + split)
- `src/kiku_value_premium/implications/`
- `tests/test_empirical_construction.py`
- `tests/test_empirical_panel.py`
- `tests/test_empirical_wrds.py`
- `tests/test_model.py`
- `tests/test_calibration.py`
- `tests/test_implications.py`
- `tests/test_api_layout.py`
- `data/annual_panel.csv` (after a local WRDS run that passes the gate)
- `docs/empirical.md`, `docs/model.md`, `docs/calibration.md`, `docs/implications.md`
- `examples/run_paper.py`
- `.gitignore` (`.env`, `data/raw/`, `__pycache__`, `.venv`)
- `.env.example` (`WRDS_USERNAME=`, `WRDS_PASSWORD=`)

Modify:

- `src/kiku_value_premium/__init__.py` — 0.3.0, section re-exports
- `pyproject.toml` — extras `[data]`, `[fast]`, `[dev]`; description
- `README.md` — thin pointer
- `docs/index.md`, `docs/installation.md`, `docs/api.md`, `docs/generalization.md`, `docs/_config.yml`
- existing solver/params/etc. — new package paths only, no kernel change

Delete:

- top-level `src/kiku_value_premium/{params,preferences,analytical,dynamics,moments,calibration,discretization,simulation,solver}.py` after the move
- `docs/KIKU_RECIPE.md`, `docs/results.md`, `docs/examples.md`

Do not add `climate_discount` to dependencies. Do not vendor paper-repo modules.

## 10. Out of scope

- Melin–Zhang climate kernel, scenario P/D paths, Table XI, climate Figure 6
- Any import of `climate_discount` or `corpo_research_papers`
- Ken French 5×5 BM files as the headline empirical series
- Sample years after 2003
- Compatibility shim for the 0.2.0 six-step imports
- Inverting \((\phi,\sigma_u)\) from prices
- Putting OLS \(\tilde\phi\) into the solver
- Spectral Figure 3 is in scope (her paper). Climate-paper omissions are not inherited.

## 11. Key decisions

1. **Paper-section API, not the six-step flat API.** Docs and imports tell the same story as her sections 2–5. Breaking 0.3.0 is acceptable.
2. **WRDS is an extra, not a hard dependency.** Replication of Table I needs credentials; solving the model from Table II does not.
3. **Printed Newey–West bands are the empirical gate.** Construction is iterated; goldens are not.
4. **DFF book equity is part of “full WRDS,” not a cheat.** Her 1930 start is otherwise impossible.
5. **Climate stays out.** This repo remains a Kiku (2006) replica. The climate paper continues to live in `corpo_research_papers`.
6. **Committed annual panel, gitignored raw extracts.** CI and Pages never see CRSP microdata or WRDS passwords.
7. **Figure 2 window is 1952–2003.** Her caption, not the 1930–2003 headline window.

## 12. Open questions

None. Remaining construction mismatches that fail the SE gate after the audit checklist are escalated at implementation time, not designed away here.

## 13. Implementation note for the later plan

1. Fast-forward local `main` to `origin/main` (Pages + current recipe docs).
2. Add `.gitignore` and `.env.example`.
3. Move code into the four subpackages with tests at each step.
4. Implement empirical construction against Layer 1 fixtures.
5. Run a local WRDS `refresh=True`, write `data/annual_panel.csv`, iterate the audit until Layer 2 passes.
6. Rewrite GitHub Pages to the four section recipes.
7. Add `examples/run_paper.py`.
8. Confirm default pytest is green without `.env`, and `pytest -m wrds` is green with `.env`.
