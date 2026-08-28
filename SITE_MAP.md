# SITE_MAP.md — file → URL → nav (updated by Issue 2; baseline of record in docs/_baseline)

Sidebar order below matches `tests/test_docs.py::test_argument_nav_order` (the hard contract).

| # | File | URL | Title | nav_order | parent | Status |
|---|---|---|---|---|---|---|
| 1 | `docs/index.md` | `/` | Home | 1 | — | rewritten (Issue 1) |
| 2 | `docs/getting-started.md` | `/getting-started.html` | The result | 2 | — | keep |
| 3 | `docs/long-run-risks-model.md` | `/long-run-risks-model.html` | The long-run risks model | 3 | — | keep |
| 4 | `docs/measuring-leverage.md` | `/measuring-leverage.html` | Measuring leverage | 4 | — | keep + firewall (Issue 3) |
| 5 | `docs/time-series.md` | `/time-series.html` | Does the market still fit? | 5 | — | keep + framing sentence (Issue 2) |
| 6 | `docs/two-free-numbers.md` | `/two-free-numbers.html` | Two free numbers | 6 | — | **new stub** (Issue 4) |
| 7 | `docs/cross-section.md` | `/cross-section.html` | Value versus growth | 7 | — | keep |
| 8 | `docs/price-your-own-claim.md` | `/price-your-own-claim.html` | Price your own claim | 8 | — | **new stub** (Issue 5) |
| 9 | `docs/package.md` | `/package.html` | Package | 9 (has_children) | — | keep |
| 9.1 | `docs/installation.md` | `/installation.html` | Installation | 1 | Package | fill (Issue 6) |
| 9.2 | `docs/api.md` | `/api.html` | API | 2 | Package | fill (Issue 6) |
| 9.3 | `docs/financial-data.md` | `/financial-data.html` | Financial data | 3 | Package | fill (Issue 6) |
| 10 | `docs/objections.md` | `/objections.html` | Objections | 10 | — | **new stub** (Issue 8) |
| 11 | `docs/background.md` | `/background.html` | Background & glossary | 11 | — | **new stub** (Issue 9) |
| 12 | `docs/references.md` | `/references.html` | References | 12 | — | **new stub** (Issue 10) |

## Conventions (from Issue 0, still binding)

- URLs are `.html`-style; no `permalink` except Home (`/`). Internal links: `{{ '/page.html' | relative_url }}`. Directory-style URLs 404.
- `tests/test_docs.py` pins this map (`test_argument_nav_order`, `BOOK_PAGES`, `DELETED`, `TUTORIAL_FIGURES`); update in the same PR as any structure change.
- Jekyll excludes `docs/_baseline/` and `docs/superpowers/` from the published site.
- Theme: Just the Docs v0.10.1 (`remote_theme`); callouts `paper` / `package` / `caution` defined but unused; MathJax via `docs/_includes/`; search + back-to-top on.
