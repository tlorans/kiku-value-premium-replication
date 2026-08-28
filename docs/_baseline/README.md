# docs/_baseline — Issue 0 snapshot (2026-08-28, commit cf344ac, lrrcs 0.5.0)

Baseline for the documentation rewrite (see `REWRITE_PLAN.md`). Jekyll excludes
this directory (underscore) from the published site.

Contents:

- `audit_numbers.py` — reproduces every offline-computable numeric claim on the
  site through package calls. Run from repo root:
  `uv run python docs/_baseline/audit_numbers.py`
- `audit_output.txt` — its captured output; the per-number statuses in
  `NUMBERS.md` (repo root) reference these sections.
- `quickstart.log` — the Home-page quickstart run verbatim.
- `fetch_baseline.sh` + `live_fetch_log.txt` — fetches the rendered HTML of all
  ten live pages (screenshots pending; see REWRITE_PLAN machine amendments).
- `html/*.html` — the rendered live pages at baseline (nav order extracted from
  `html/index.html`; see `SITE_MAP.md`).

Findings recorded during the audit (details in `NUMBERS.md`):

- F1: the Table VII "model" E[R] column (6.07 / 11.36 / 7.53, rf 1.58, beta
  ratio 0.92) is not reproducible from committed code — the numerical solver
  path (`ModelSolver` + `compute_asset_pricing_moments`) collapses to the
  price floor at every grid tried. Escalated to the human at the Issue-0 gate.
- F2: the equal-φ block on The result / Value versus growth is stale
  (code prints spread −0.12, page prints 0.00).
- F3: the 1000-sample sentence on Does the market still fit? is stale on the
  model side (AC1 0.15 on current code vs 0.43 claimed).
- F4: the κ₁/A₁ block on that page misprints A₁ (56.3; arithmetic gives 37.5).
