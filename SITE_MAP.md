# SITE_MAP.md — file → URL → nav (baseline 2026-08-28, commit cf344ac)

Sidebar order below is verified against the **live rendered HTML** (`docs/_baseline/html/index.html`, `nav-list` extraction).

| # | File | Live URL | Title | nav_order | parent | Status in rewrite plan |
|---|---|---|---|---|---|---|
| 1 | `docs/index.md` | `/` (permalink: `/`) | Home | 1 | — | rewrite (Issue 1) |
| 2 | `docs/getting-started.md` | `/getting-started.html` | The result | 2 | — | keep |
| 3 | `docs/long-run-risks-model.md` | `/long-run-risks-model.html` | The long-run risks model | 3 | — | keep |
| 4 | `docs/measuring-leverage.md` | `/measuring-leverage.html` | Measuring leverage | 4 | — | keep + firewall (Issue 3) |
| 5 | `docs/time-series.md` | `/time-series.html` | Does the market still fit? | 5 | — | keep |
| 6 | `docs/cross-section.md` | `/cross-section.html` | Value versus growth | 6 | — | keep |
| 7 | `docs/package.md` | `/package.html` | Package | 7 (has_children) | — | keep |
| 7.1 | `docs/installation.md` | `/installation.html` | Installation | 1 | Package | fill (Issue 6) — already substantial |
| 7.2 | `docs/api.md` | `/api.html` | API | 2 | Package | fill (Issue 6) — already substantial |
| 7.3 | `docs/financial-data.md` | `/financial-data.html` | Financial data | 3 | Package | fill (Issue 6) — already substantial |

## Facts the plan must accommodate

- **URL style is `.html`, not directory-style.** No page sets a `permalink` except Home (`/`). Internal links use `{{ '/page.html' | relative_url }}`. New pages (Issue 2) should follow the same convention to keep links stable; directory-style URLs 404 (verified 2026-08-28).
- **Target nav (plan Issue 2) implies new top-level `nav_order` 1–12** with Package's children unchanged. Current: 6 pages + Package parent at 7. The plan's table inserts Two free numbers (6), shifts Value versus growth to 7, Price your own claim to 8, Package to 9, Objections 10, Background 11, References 12.
- **`tests/test_docs.py` is a hard contract on this map** (`test_argument_nav_order` pins the exact current orders; `BOOK_PAGES`, `DELETED`, `TUTORIAL_FIGURES` pin file inventories). Every nav/structure change must update that test in the same PR, or `uv run pytest` fails. This is the machine's substitute for a local Jekyll build (see REWRITE_PLAN.md, Machine amendments).
- Jekyll excludes `docs/_baseline/` and `docs/superpowers/` from the published site (underscore dirs; `_config.yml` exclude).
- Theme: Just the Docs v0.10.1 via `remote_theme`; custom callouts `paper` / `package` / `caution` already defined in `_config.yml` (Issue 3 can add a `firewall` callout without new dependencies); MathJax wired through `docs/_includes/`; search + back-to-top enabled.
