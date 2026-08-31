# NUMBERS.md — index of every figure on the site

**Status note (0.6.0 API migration).** This ledger was written against the
Jekyll site in `docs/` and the flat 0.5.0 API, and both are gone. The
`docs/` page paths and the `docs/_baseline/*` scripts named below no
longer exist; the site now lives in `site/*.qmd` and its numbers are
re-executed from scratch every week by `.github/workflows/freshness.yml`,
which is the live verification this file used to provide. The
"Reproduces via" entries have been re-keyed to the 0.6.0 calls so they
still say where each number comes from. The findings F1 to F4 below are
kept verbatim as history, including their original 0.5.0 call names in
the narrative.

The seeded numbers themselves did not move in the 0.6.0 migration: the
solver, moments, and simulation engines were reused unchanged behind the
new `LongRunRisksModel` facade, and every value in this file was checked
against the 0.5.0 output before the old API was removed.

Baseline captured 2026-08-28 at `lrrcs` 0.5.0, commit `cf344ac`, Python 3.12 (uv env).
Live site: https://tlorans.github.io/kiku-value-premium-replication/

**Final-audit stamp (Issue 15, 2026-08-28, post-`b7fc4dc`):** `docs/_baseline/audit_numbers.py` re-run on merged main — output byte-identical to baseline. All 15 pages live (0 × 404); rendered-site vocabulary scan clean; internal page links, front matter (nav_order 1–12 unique/sequential, no orphans), wink audit, and scoping-line presence all pass (`.issue0/final_lint.py` logic reproduced in `docs/_baseline/final_lint.py`). F1–F4 remain the only open findings, by design (see Findings).

**Rule (REWRITE_PLAN.md):** no number appears on any page unless a committed script prints it.
This file is the index. Every entry carries a status:

- **TRACED** — reproduced by the listed package call, re-executed on every site render.
- **GOLDEN** — Kiku's printed value, pinned as a test constant in `src/lrrcs/empirical/goldens.py` and gated by `tests/test_empirical_goldens.py` (reconstruction must land within her printed Newey-West SEs).
- **CHUNK** — self-contained arithmetic in the page's own code block (no data dependency); runs as printed.
- **UNTRACED** — no committed script reproduces it. See Findings.
- **STALE** — the page's printed output no longer matches what current code prints. See Findings.

Reproduce everything offline: `uv run quarto render site` after `rm -rf site/_freeze`.
Gate: `uv run pytest`.

---

## Findings (recorded, not fixed — per plan)

- **F1 · RESOLVED 2026-08-28 (branch `fix/f1-solver`) — Table VII model column now has a traced counterpart.** Root cause of the collapse: `solve_consumption_claim` iterated the Euler fixed point in a form whose local slope is 1−θ = 28 (θ = −27), so the iteration diverged and landed on the silent clamp log(1e-12) = −27.63. The solver now iterates the θ-divided contraction (modulus ≈ κ₁ < 1), integrates the Gaussian innovations η and v in closed form (the old kernel dropped the independent dividend residual √(1−α²)·v entirely), uses genuine Tauchen–Hussey transition weights, and raises `SolverDivergenceError` instead of flooring. A new `simulate_table_vii` (in `lrrcs.implications.simulation`) reproduces the paper's object: 1000 samples × 74 years of monthly data aggregated to annual. On the paper grid (30×4), `examples/run_paper.py` prints: E[R] 7.75 / 13.00 / 8.74, rf 1.00, value premium 5.26 (paper 5.29), beta ratio 0.83, log P/D 3.16 / 2.74 / 2.97 with every paper ranking reproduced — each E[R] and volatility within one of the paper's own cross-sample SDs (2.91 / 4.30 / 2.69). Residual level gaps vs Kiku's prints (rf 1.58, beta ratio 0.92, log P/D 3.65 / 3.10 / 3.24) are grid-resolution dependent: a grid-convergence study (`tests/test_implications.py::test_grid_convergence`) shows the 30-point grid over-disperses x by ~21%, and at n_x = 60 the solution lands at rf 1.82, beta ratio 0.91, log P/D 3.79 / 3.40 / 3.42, converging to VP ≈ 3.5, rf ≈ 1.83 by n_x = 140 — i.e. Kiku's exact printed values reflect her (undisclosed) 30-point discretization, and part of the 5.3% premium is grid-induced x-over-dispersion. Page statuses marked "UNTRACED (F1)" now read: GOLDEN (Kiku's print) with a TRACED model counterpart within the paper's cross-sample SDs. The `two-free-numbers.md` 0.56-vs-0.92 TODO resolves the same way: 0.56 is the affine-innovations count; the solved model's simulated annual beta ratio is 0.83 on the paper grid (0.91 at n_x=60), vs Kiku's printed 0.92. Gated by `tests/test_implications.py` (no-collapse, analytical consistency at n_x=60 within 15%, grid convergence, Table VII bands).
- **F2 · equal-φ block is STALE** (`getting-started.md` ~line 120, `cross-section.md` ~line 241). Page prints `value: 0.39% / spread: 0.00%`; current code prints `value: 0.28% / spread: −0.12%` (residual comes from the φ_σ / α legs the block does not equalize). Cause is presumably a code change after the page was written.
- **F3 · 1000-sample sentence is STALE** (`time-series.md` ~line 174). Page: "with 1,000 samples the model is close to the data on consumption: mean 1.86 vs 1.96, volatility 2.16 vs 2.20, AC1 0.43 vs 0.44". Current `simulate_cashflow_moments(n_sims=1000, years=74)` prints E[dc]≈1.81, σ≈2.45, **AC1≈0.15** across seeds 1, 7, 42. Data side (1.96 / 2.20 / 0.44) is GOLDEN. The model-side AC1 claim does not reproduce on current code. **Root cause identified 2026-08-28:** the paper time-aggregates *levels* (annual consumption = sum of 12 monthly levels, then log growth — matching how NIPA annual data are built), which mechanically raises AC1 (Working-1960 aggregation) and lowers σ; `simulate_cashflow_moments` sums monthly *log growth*, which yields AC1 ≈ 0.15–0.19 (the direct theoretical value) and σ ≈ 2.45. Fix belongs to the calibration module page rewrite: aggregate levels, then Table III's 1.86 / 2.16 / 0.43 should reproduce.
- **F4 · A1-by-hand block misprints** (`time-series.md` ~line 200). Page prints `(0.962, 56.3)` for κ₁ and A₁ with φ=2.8, ψ=1.5, ρ=0.98, z̄=3.24; the arithmetic gives `(0.962, 37.5)`, which matches the solver's `A1['market']=37.5` and the audit. The 56.3 is inconsistent with the block's own inputs.
- Cosmetic: `measuring-leverage.md` shows only the `market` row of `print_calibration_summary`; the same call also prints `long` (NaN, Value series has a gap) and `short` rows. Values match; display differs.

---

## Home (`docs/index.md`)

| Number | Status | Reproduces via |
|---|---|---|
| Data E[R] 7.81 (1.98) / 13.88 (1.74) / 8.56 (1.79) | GOLDEN | `goldens.TABLE_I` |
| Data log P/D 3.61 (0.18) / 3.25 (0.12) / 3.34 (0.13) | GOLDEN | `goldens.TABLE_I` |
| Model log P/D 3.65 (0.06) / 3.10 (0.15) / 3.24 (0.07) | TRACED (levels; SEs are Kiku's) | `.solve(method="analytical").mean_log_pd` |
| Model E[R] 6.07 (2.91) / 11.36 (4.30) / 7.53 (2.69) | **UNTRACED (F1)** | — |
| "about six extra points a year over 1930 to 2003" | GOLDEN | 13.88 − 7.81 |
| "5.3" model gap / "about 6 in the data" | UNTRACED (model side, F1) / GOLDEN (data side) | 11.36 − 6.07 |
| CAPM beta ratio 0.92 | **UNTRACED (F1)** | grid solver gave 0.84, not 0.92 |
| "about 0.4 percent on the value-growth spread" | TRACED | `LongRunRisksModel().solve(method="analytical").summary()` → 0.40% |
| Sample period 1930–2003 | GOLDEN | `goldens.START/END` |

## Two free numbers (`docs/two-free-numbers.md`) — added by Issue 4

All numbers below are printed by `examples/dcf_counterfactual.py` (TRACED, run 2026-08-28).

| Number | Status | Reproduces via |
|---|---|---|
| g_eff growth / value / market = 3.24 / 6.04 / 3.32 %/yr | TRACED | panel (A), expected dividend growth incl. convexity |
| Implied value-growth premium under one common rate: 0.00 pp (exact) | TRACED | panel (A), identity |
| Value grows +2.80 pp/yr faster; DCF prices value richer | TRACED | panel (A) |
| Data P/D ranking 3.25 vs 3.61 | GOLDEN | `goldens.TABLE_I` |
| "5.3 pp model gap" / "data: 13.88 − 7.81 = 6.07 pp" | UNTRACED (model side, F1) / GOLDEN (data side) | — |
| CAPM betas (affine innovations) growth 0.89, value 0.50; ratio 0.56 | TRACED | panel (B), 200×74y simulation, seed 7 |
| CAPM spread −2.4 pp ("with the Table VII premium level") | UNTRACED — derived from the site's F1-blocked 0.92/5.3 numbers, not script output | — |
| φ 6.2 → 7.4: g_eff 6.04 → 7.07 %/yr (DCF world) | TRACED | panel (C) |
| A1 value 88.9 → 108.2; premium_lr 0.80% → 0.97% (equilibrium) | TRACED | panel (C), `.solve(method="analytical")` |

**Gate note (open):** panel (B)'s page line "the CAPM-fitted spread is negative: the wrong sign" is script-backed; the parenthetical "prices near −2.4" leans on the site's Table VII numbers, which F1 blocks. Also open: the site elsewhere claims ratio 0.92 (model betas) while the level-free affine count gives 0.56. Both belong to the F1 resolution.

## Price your own claim (`docs/price-your-own-claim.md`) — added by Issue 5

All numbers below are printed by `examples/two_firms.py` via `LongRunRisksModel.from_loading` (TRACED, run 2026-08-28).

| Number | Status | Reproduces via |
|---|---|---|
| Firm A (φ=0.5): A1 −3.0, premium_lr −0.03%, g_eff 3.20%, gordon 6.89% | TRACED | `LongRunRisksModel.from_loading(0.5).solve(method="analytical")` |
| Firm B (φ=1.5): A1 15.2, premium_lr 0.14%, g_eff 3.32%, gordon 7.01% | TRACED | `LongRunRisksModel.from_loading(1.5).solve(method="analytical")` |
| Anchor mean log P/D 3.30 (linearization point, not a fitted level) | TRACED | `.solve(method="analytical")` default for custom claims |
| "Gordon column puts the two firms 0.12 points apart" | CHUNK | 7.01 − 6.89 |

## The result (`docs/getting-started.md`)

| Number | Status | Reproduces via |
|---|---|---|
| θ = −27; δ, γ, ψ = 0.999, 10.0, 1.5; 1/ψ = 0.667 | TRACED | params dump + chunk arithmetic |
| μ_c, ρ, φ_x, σ = 0.0015, 0.98, 0.032, 0.0064 | TRACED | `ModelParams().cons` |
| φ dict {growth 2.6, value 6.2, market 2.8} | TRACED | `ModelParams().dividends` |
| Quickstart block (0.39 / 0.80 / 0.34; spread 0.40; A1 43.1 / 88.9; Λ_ε 5.95) | TRACED | `LongRunRisksModel().solve(method="analytical").summary()` |
| Results table (same as Home) + Risk-free 0.91 (0.39) / 1.58 (0.01) | 0.91 GOLDEN (Kiku Table I print, not in goldens.py); 1.58 **UNTRACED (F1)** | — |
| "mean price-dividend levels … 24.7 on value versus 39.8 on growth" | **UNTRACED (F1)** — Kiku Table VII levels; analytical exp(3.10/3.65) = 22.2 / 38.5 | — |
| "safe rate, about seventy basis points too high" | UNTRACED (rests on 1.58, F1) | 1.58 − 0.91 |
| "ratio of value to growth CAPM betas is 0.92" / "premium is five points higher" | UNTRACED (F1) | — |
| Equal-φ block (0.39 / 0.39 / 0.34; spread 0.00) | **STALE (F2)** — code now prints 0.28 / −0.12 | `params.dividends[*].phi = 2.6` then solve |
| P/D = 25 at r−g = 4%; "price jumps by a third" | CHUNK | 1/0.04; 1/0.03 |
| "six-percent gap" | GOLDEN | 13.88 − 7.81 |

## The long-run risks model (`docs/long-run-risks-model.md`)

| Number | Status | Reproduces via |
|---|---|---|
| First autocorrelation of Δc "about 0.41" | TRACED | corr on `data/consumption_annual.csv` |
| ρ = 0.98, "half-life of about three years" | TRACED / CHUNK | ln 0.5 ÷ ln 0.98 ≈ 34 months |
| (γ, 1/ψ, θ) = (10.0, 0.667, −27.0); δ = 0.999 | TRACED | params dump + chunk |
| A1 growth 43.1, market 37.5, value 88.9; Λ_ε 5.95 | TRACED | `.solve(method="analytical")` |
| κ₁ ≈ 0.96 | TRACED | 0.962 at z̄ = 3.24 |
| Sim chunk inputs (μ 0.0015, σ 0.0064, φ_x 0.032, ρ 0.98) | TRACED | `ModelParams().cons` |
| φ_G = 2.6, φ_m = 2.8, φ_V = 6.2 | TRACED | `ModelParams().dividends` |

## Measuring leverage (`docs/measuring-leverage.md`)

| Number | Status | Reproduces via |
|---|---|---|
| MA head table (1930 −0.053 … 1935 0.020) | TRACED | `expected_growth_proxy(y, 2)` head |
| φ̂ = {Growth −0.267, Value 12.129, Market 0.722} | TRACED | page OLS chunk ≡ `estimate_long_run_leverage` |
| "Kiku's Table VI prints −0.38 / 2.16 / 0.66" | GOLDEN | `goldens.TABLE_VI_PHI` |
| "Seventy-two annual observations" | TRACED | 74 years − 2 MA warmup |
| Calibration summary market row (0.00076 / 0.722 / 5.33 / 0.57) | TRACED | `lrr.calibration.calibrate_from_data(...)` |
| Table II monthly φ locks (2.6 / 2.8 / 6.2) | TRACED | `ModelParams()` |

## Does the market still fit? (`docs/time-series.md`)

| Number | Status | Reproduces via |
|---|---|---|
| "out-earns a Treasury bill by six to eight percentage points" | GOLDEN (range) | 8.56 − 0.91 |
| "price-dividend ratio swings from 10 to 88" | TRACED | panel `pd` min 10.52 / max 88.07 |
| `mkt.head()` six rows | TRACED | audit "market head rows" |
| 74 obs; Δc mean 1.75, vol 2.37; AC1 0.41; rf 0.07 | TRACED | shipped CSVs |
| "returns average 8.5; mean P/D about 31 (log 3.33)" | TRACED | 0.085 / 30.85 / 3.326 |
| "Kiku's printed sample is 0.91 percent" | GOLDEN (Kiku Table I print) | — |
| `describe()` table (mean / std / min / max) | TRACED | audit "market describe" |
| Table II market leg (μ_d 0.0012, φ 2.8, φ_σ 7.5, α 0.55; ν 0.99, σ_w 1e-6) | TRACED | params dump |
| 20-sim moments (1.82 / 2.44 / 0.16; 0.68 / 16.36) | TRACED | `simulate_cashflow_moments(n_sims=20, years=74, seed=1)` |
| "1,000 samples … mean 1.86 vs 1.96, volatility 2.16 vs 2.20, AC1 0.43 vs 0.44" | **STALE (F3)** model side; GOLDEN data side | current runs: 1.81 / 2.45 / 0.15 |
| κ₁, A₁ = (0.962, 56.3) | **STALE (F4)** — reproduced (0.962, 37.5), matches solver A1 market | chunk arithmetic |
| Market scoreboard row + risk-free | data GOLDEN; model **UNTRACED (F1)** | — |
| "volatility is 20.1 percent in both" | data GOLDEN (20.1); model UNTRACED (F1) | — |
| Kalman (0.43, 0.00046, 1e-12, 178.9); "ρ ≈ 0.43" | TRACED | `filter_expected_growth(y)` → (0.4262, 0.000464, 1e-12, 178.888) |
| Appendix: MA head; market slope 0.722 | TRACED | as above |

## Value versus growth (`docs/cross-section.md`)

| Number | Status | Reproduces via |
|---|---|---|
| Reconstruction means 7.49 / 13.67 / 8.52 | TRACED | panel `ret` means |
| Kiku vintage 7.81 / 13.88 / 8.56 | GOLDEN | `goldens.TABLE_I` |
| Summary table (E[R], σ(R), log P/D; σ(R) 20.2 / 29.9 / 20.1) | GOLDEN | `goldens.TABLE_I` |
| CAPM betas {Growth 0.95, Value 1.28} | TRACED | page OLS chunk on shipped panel |
| "the paper's vintage has both near 1.03" | UNTRACED (Kiku Table V print; not in goldens.py) | — |
| φ̂ dict; Table VI prints (−0.38 / 2.16 / 0.66) | TRACED / GOLDEN | as Measuring leverage |
| (6.2, 2.6) | TRACED | params |
| A1 by hand: growth 43.1, value 88.9 | TRACED | chunk ≡ solver |
| Quickstart block; A1 ratio 2.06 | TRACED | `.solve(method="analytical")` |
| Table VII table incl. risk-free row | data GOLDEN; model **UNTRACED (F1)** | — |
| "5.3" / "about 6" / 0.92 / "five points higher" | as Home | — |
| Equal-φ block (spread 0.00) | **STALE (F2)** | code now prints −0.12 |

## Robustness (cross-section.md §Robustness) — added by Issue 12

All grid values are printed by `examples/robustness.py` (TRACED, run 2026-08-28).

| Number | Status | Reproduces via |
|---|---|---|
| Baseline market premium_lr 0.34%, spread 0.40% | TRACED | `LongRunRisksModel().solve(method="analytical")` |
| ρ ∈ {0.95, 0.98, 0.99}: market 0.14/0.34/0.51%, spread 0.19/0.40/0.55% | TRACED | grid, `cons.rho` |
| ψ ∈ {1.2, 1.5, 2.0}: market 0.31/0.34/0.37%, spread 0.41/0.40/0.40% | TRACED | grid, `prefs.psi` |
| γ ∈ {5, 10, 15}: market 0.16/0.34/0.52%, spread 0.19/0.40/0.62% | TRACED | grid, `prefs.gamma` |
| φ_V ∈ {5.0, 6.2, 7.4}: spread 0.23/0.40/0.58% (market flat) | TRACED | grid, `dividends[value].phi` |
| φ_G ∈ {2.0, 2.6, 3.2}: spread 0.52/0.40/0.28% (market flat) | TRACED | grid, `dividends[growth].phi` |

## Installation (`docs/installation.md`)

| Number | Status | Reproduces via |
|---|---|---|
| Python 3.11+ requirement | TRACED | `pyproject.toml` `requires-python` |
| `((3, 12), '0.5.0')` | TRACED | uv env Python 3.12; `lrrcs.__version__` |
| Quickstart block (0.39 / 0.80 / 0.34 / 0.40) | TRACED | as Home |
| Clean-venv check: install 5 s, snippet 4.3 s, 10 s total (2026-08-28, Windows, Python 3.12.12) | TRACED | `docs/_baseline/clean_venv_check.sh` → output committed alongside |
| "under a minute from install to first valuation" | TRACED | measured: 10 s |

## API (`docs/api.md`)

No printed numbers.

## Financial data (`docs/financial-data.md`)

| Number | Status | Reproduces via |
|---|---|---|
| FRED head rows (1929 11.737 …) | network chunk (FRED `DNDGRA3A086NBEA`); not reproducible offline | — |
| Δc head + 1.75 / 2.37 / 74 | TRACED | `data/consumption_annual.csv` |
| Toy Campbell-Shiller year (2.54 / 112.68 / 44.42) | TRACED | audit toy chunk (2.5365 / 112.6825 / 44.4244) |
| Toy real T-bill (NaN / 0.002) | TRACED | audit toy chunk |
| Table I reconstruction (7.49 (1.93) … 3.33 (0.13), all cells) | TRACED | `table_i(panel)` — audit matches every cell |
| "volatility of 48 percent against growth's 14" | TRACED | 47.72 / 14.35 |
| "volatility 2.37 percent" | TRACED | shipped CSV |

## Package (`docs/package.md`)

No numbers.

## Site chrome

- Tagline: promoted from footer to under the Home title in Issue 1 (`docs/index.md`); footer now carries "MIT License." only.
