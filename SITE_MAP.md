# SITE_MAP.md — page, sidebar position, and legacy URL

The site is a Quarto website under `site/`, published to `site/_site`.
The sidebar order below is set by `site/_quarto.yml` and checked by
`tests/test_site.py`, which is the contract. Update this file in the
same pull request as any structural change.

An earlier version of the site was a 12-chapter course, and before that
a Jekyll site under `docs/`. Every one of those URLs still has to
resolve, so each page carries the old URL in the `aliases` field of its
front matter, and `test_legacy_urls_covered_by_aliases` fails if one
goes missing.

| # | File | Title | Sidebar section | Legacy URL |
|---|---|---|---|---|
| 1 | `site/index.qmd` | geap | top level | `/`, `/getting-started.html` |
| 2 | `site/installation.qmd` | Installation | top level | `/installation.html`, `/package.html` |
| 3 | `site/lrr/index.qmd` | Long-run risks | Long-run risks | `/two-free-numbers.html`, `/long-run-risks-model.html`, `/objections.html` |
| 4 | `site/lrr/user-guide.qmd` | User guide | Long-run risks | `/measuring-leverage.html` |
| 5 | `site/lrr/examples.qmd` | Examples | Long-run risks | `/financial-data.html`, `/time-series.html`, `/cross-section.html`, `/price-your-own-claim.html` |
| 6 | `site/lrr/math.qmd` | Mathematical detail | Long-run risks | — |
| 7 | `site/lrr/api.qmd` | Module reference | Long-run risks | `/api.html` |
| 8 | `site/reference/glossary.qmd` | Glossary | Reference | `/background.html` |
| 9 | `site/reference/references.qmd` | References | Reference | `/references.html` |

## Conventions

Every page must appear in the sidebar, and every sidebar entry must
exist on disk. Both directions are checked, so a new page that is not
listed in `site/_quarto.yml` fails the suite.

The site is a library. Course furniture (Parts, exercises, takeaways,
"how to read this course") is banned by `tests/test_site.py`.

Pages run their Python at build time, so a render is what checks the
code. Quarto is configured with `freeze: auto`, and the cached output
lives in `site/_freeze`. Continuous integration renders from the
committed freeze, so after you change a page you run `make site` and
commit the regenerated freeze along with it. A page that runs Python
without a freeze entry fails `test_freeze_covers_every_executed_page`.
Note that the freeze keys its figure files by cell number, so moving or
removing a cell can leave an orphaned file behind, and you should
delete it.

No number appears on a page unless one of the page's own cells prints
it, or the page attributes it to the paper. See `NUMBERS.md`.

Names removed from the public API must not survive anywhere a reader
can see them, prose included. The list is `REMOVED_API_NAMES` in
`tests/test_site.py`, and it covers the site, `README.md`, and the
scripts in `examples/`.

## Build commands

Run `make site` to render, `make preview` to serve the site locally
with live reload, and `make freeze` to delete `site/_freeze` and render
everything from scratch. Run `uv run pytest tests/test_site.py` for the
structural checks alone.
