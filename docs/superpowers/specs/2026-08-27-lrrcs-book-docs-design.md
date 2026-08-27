# lrrcs GitHub Pages as a GE asset-pricing book

Date: 2026-08-27
Status: draft (pending user review)
Version: 0.5.0 docs

## Goal

Turn the Just the Docs GitHub Pages site into a short *book* whose spine is one recipe:

1. Form the claim(s) from data.
2. Calibrate cash-flow dynamics.
3. Solve the long-run risks model.
4. Compare model asset-pricing moments to the data.

The site is a companion book to [tidy-finance.org](https://www.tidy-finance.org/) for general-equilibrium asset pricing, not a pkgdown API site and not a walkthrough of Kiku (2006). Kiku (2006) supplies the default 1930–2003 sample and Table II numbers used as the worked example. It is not the table of contents.

This spec supersedes the **Documentation** section of `docs/superpowers/specs/2026-08-27-tidyfinance-companion-design.md` (“keep Just the Docs and the replica narrative”). The package design in that spec is unchanged.

## Non-goals

- Quarto, Great Docs, or a custom marketing landing
- An R sibling or bilingual chapters
- Other risk premia, climate, or “further applications” in this version
- Changing solvers, Table II defaults, or preference parameters
- Publishing to PyPI
- Rewriting the Python API or examples except where a docs URL/title is cited
- Redirect stubs for deleted pages (those URLs 404)

## Thesis (cash flows in, prices out)

Calibration matches consumption and dividend dynamics only. Average returns, Sharpe ratios, and CAPM betas never enter the cash-flow step.

The Euler equation is then a test: does the solved model reproduce asset-pricing moments (equity premium, risk-free rate, return volatility, mean log price–dividend, long–short premia, price–dividend ranking)?

If cash-flow moments fail, stop. A later match on returns would be a free parameter in disguise.

## Shape

A one-page map, then two full passes of the same four steps.

| Part | Page | File | URL |
|---|---|---|---|
| Landing | Home | `docs/index.md` | `/` |
| Start | Getting started | `docs/getting-started.md` (new) | `/getting-started.html` |
| Map | Cash flows, then prices | `docs/cash-flows-then-prices.md` (new) | `/cash-flows-then-prices.html` |
| Pass 1 | The market | `docs/time-series.md` (rewrite) | `/time-series.html` |
| Pass 2 | Value versus growth | `docs/cross-section.md` (rewrite) | `/cross-section.html` |
| Reference | Package | `docs/package.md` | `/package.html` |
| Reference | Installation | `docs/installation.md` | `/installation.html` |
| Reference | API | `docs/api.md` | `/api.html` |

Sidebar order (Just the Docs `nav_order`, no parent unless noted):

| Page | `nav_order` | parent |
|---|---|---|
| Home | 1 | — |
| Getting started | 2 | — |
| Cash flows, then prices | 3 | — |
| The market | 4 | — |
| Value versus growth | 5 | — |
| Package | 6 | — (`has_children: true`, `has_toc: false`) |
| Installation | 1 | Package |
| API | 2 | Package |

`time-series.html` and `cross-section.html` keep their URLs. Titles become **The market** and **Value versus growth**.

## Chapter contract

Tutorial voice (“you” / “we”). Not the paper’s “I construct…”.

Both claim chapters use these H2s, in this order, with these names:

1. Data
2. Calibrate cash flows
3. Solve
4. Compare pricing moments

The Cash flows, then prices page names the same four steps but is a map, not a third pass.

Code rules (unchanged from the companion spec):

- Documented imports: `import tidyfinance as tf` and `import lrrcs as lrr`
- Fenced `python` blocks, not doctest `>>>`
- Public names at the `lrr.` root; no `from lrrcs.model import` as the documented form
- No `kiku_value_premium`, `connect_wrds`, or `print_value_premium`

Each claim chapter opens with a one-paragraph question (what this pass asks the household). Printed 1930–2003 numbers stay (market 8.56 / 7.53; value 13.88 vs growth 7.81; model value premium about 5.3 vs about 6 in the data; Table II \(\phi\) 6.2 / 2.6 / 2.8). Existing SVGs that those two chapters still need stay under `docs/figures/`.

Cash flows, then prices states the IMRS and Euler equation once, compactly. Claim chapters do not re-derive the model; the Solve section shows the code plus a short reminder.

## Homepage

`docs/index.md` is a landing, not an essay.

- H1: **Long-run risks**
- One-sentence pitch: calibrate cash flows, then ask whether the model matches asset-pricing moments
- Companion line: tidyfinance gets data and sorts; `lrrcs` calibrates cash-flow loadings and prices claims
- Hero code: the five-line Table II solve (`tf` + `lrr` + `print_long_short_premium(solve_analytical(get_table_ii_params()))`)
- CTA: Start here → Getting started
- Four-step preview (names only, link to Cash flows, then prices)
- Two claim links: The market, Value versus growth
- Package / Installation / API / GitHub

No Cochrane/Mehra lede, no “I show”, no “overlooked column” essay. Those arguments live in the two claim chapters where they earn their keep.

## Getting started

New `docs/getting-started.md`. The first book chapter.

- Python 3.11+, clone, `uv pip install -e .`
- `import tidyfinance as tf` / `import lrrcs as lrr`
- Five-line solve and printed output
- What that did: used Table II defaults, solved, printed the model long–short premium
- What that did not do: did not match that premium; did not touch WRDS
- Package split (one short paragraph)
- Link to Installation for `[fast]`, `[data]`, and `tf.set_wrds_credentials()`
- Next: Cash flows, then prices

Do not dump extras and WRDS into this chapter. `docs/installation.md` remains the reference.

## Cash flows, then prices

New `docs/cash-flows-then-prices.md`. One screen, almost no original results.

- The four steps, each one short block
- Target vs test (cash-flow moments vs asset-pricing moments)
- Compact IMRS / Euler
- Skeleton code in the shape both passes copy (`calibrate_from_data` or Table II params → `ModelSolver` / `solve_analytical` → `compute_asset_pricing_moments`)
- Next: The market, then Value versus growth

## The market

Rewrite `docs/time-series.md`. One claim. Bansal and Yaron (2004) is the test this pass is for.

| H2 | Content |
|---|---|
| Data | Consumption and market dividends, 1930–2003. `tf` plumbing where the panel is built; `lrr.build_annual_panel` / `lrr.table_i`. Campbell–Shiller dividends stay in `lrrcs`. |
| Calibrate cash flows | Table II consumption + market \(\phi=2.8\). `simulate_cashflow_moments` as the stop-or-go check. Mean market return is not a target. |
| Solve | `get_table_ii_params`, `solve_analytical` or `ModelSolver`. |
| Compare pricing moments | Equity premium, risk-free rate, return vol, mean log \(P/D\). `compute_asset_pricing_moments`. |

## Value versus growth

Rewrite `docs/cross-section.md`. Two legs, same household. Kiku (2006) is the worked example, not the page title.

| H2 | Content |
|---|---|
| Data | June BM quintiles, NYSE breaks. Growth 7.81, value 13.88, betas near one. |
| Calibrate cash flows | \(\phi_V=6.2\), \(\phi_G=2.6\). The six-percent premium is not a target. |
| Solve | Same preferences as the market pass. |
| Compare pricing moments | Long–short about 5.3 vs about 6; value’s \(P/D\) below growth’s; CAPM betas still fail. `print_long_short_premium`. The market row on the same calibration remains the time-series check. |

## Package pages

Keep companion framing. Light edits only: links point at Getting started / Cash flows, then prices / the two claims, not at deleted paper sections. `docs/generalization.md` is deleted; the “other portfolios” idea is out of this version.

Installation and API content stay as they are except for title/description consistency with the new site title.

## Config and README

`docs/_config.yml`:

- `title: Long-run risks`
- `description` states the recipe (calibrate cash flows, then ask whether asset-pricing moments match)
- Footer matches
- Still Just the Docs, `color_scheme: kiku`, MathJax, `superpowers/` excluded

`README.md`:

- Title **Long-run risks**
- Companion one-liner and the five-line solve
- Docs table: Getting started, Cash flows, then prices, The market, Value versus growth
- Install unchanged (`uv`, Python 3.11+)

## Files to delete

These URLs 404. No redirect stubs.

- `docs/empirical.md`
- `docs/model.md`
- `docs/calibration.md`
- `docs/implications.md`
- `docs/other-risk-premia.md`
- `docs/climate.md`
- `docs/further.md`
- `docs/generalization.md`
- `docs/replica.md`
- `docs/value.md`

Unused figures may remain under `docs/figures/`. Do not delete SVGs still referenced by the two claim chapters.

## Tests

Rewrite `tests/test_docs.py` so it encodes this book. Drop assertions that the site is “the paper, not a tutorial.”

Must pass:

- `_config.yml` still uses Just the Docs; title is `Long-run risks` (not “and the cross section”)
- Required pages exist: `index.md`, `getting-started.md`, `cash-flows-then-prices.md`, `time-series.md`, `cross-section.md`, `package.md`, `installation.md`, `api.md`
- Deleted files listed above do not exist
- Home does not link the deleted stems (`empirical`, `model`, `calibration`, `implications`, `climate`, `further`, `other-risk-premia`, `generalization`, `replica`)
- Home H1 is `# Long-run risks`; no `## Introduction`; Start here links to Getting started
- `time-series.md` title/H1 is The market; `cross-section.md` title/H1 is Value versus growth; both have the four H2s in order (`## Data`, `## Calibrate cash flows`, `## Solve`, `## Compare pricing moments`)
- Printed numbers remain: market page has `8.56` and `7.53`; value page has `7.81`, `13.88`, and `5.3`
- Every book and package page with a python fence uses `import lrrcs as lrr`, no `kiku_value_premium`, no `from lrrcs.model import` (and the other submodule imports already banned)
- Package pages still show `import tidyfinance as tf`
- README title and links match the landing
- MathJax and `kiku.scss` still present
- `getting-started.md`, `cash-flows-then-prices.md`, `time-series.md`, and `cross-section.md` have no parent; `installation.md` and `api.md` parent Package
- `cash-flows-then-prices.md` title/H1 is Cash flows, then prices; `docs/recipe.md` does not exist
- README does not contain “six-step” / “6-step”

Keep `test_mathjax_and_sidebar_theme`. Keep companion import checks on package pages.

## Relationship to the companion spec

Do not reopen:

- `import lrrcs as lrr` / `import tidyfinance as tf`
- tidyfinance as required dependency; empirical plumbing through public tidyfinance names
- Campbell–Shiller, historical book equity, consumption loaders in `lrrcs`
- Backend wrapping, `EmpiricalDataError`, goldens, WRDS tests

Do replace: the replica-narrative docs plan in that spec’s Documentation section.

## Out of scope this round

- Other sorts, climate, Melin–Zhang
- Quarto / custom HTML landing
- Solver or Table II number changes
- PyPI, hatchling, Ruff-only pass
- Executable notebooks
- Redirect pages for deleted URLs
