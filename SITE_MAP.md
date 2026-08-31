# SITE_MAP.md — page, sidebar position, and legacy URL

The site is a Quarto website under `site/`, published to `site/_site`. The
sidebar order below is set by `site/_quarto.yml` and checked by
`tests/test_site.py`, which is the contract. Update this file in the same pull
request as any structural change.

An earlier version of the site was built with Jekyll under a `docs/` directory,
and the pages there had `.html` URLs. That directory is gone. Every one of its
URLs still has to resolve, so each page carries the old URL in the `aliases`
field of its front matter, and `test_legacy_urls_covered_by_aliases` fails if
one goes missing.

| # | File | Title | Sidebar section | Legacy URL |
|---|---|---|---|---|
| 1 | `site/index.qmd` | Valuing Asset Claims in General Equilibrium | top level | `/`, `/getting-started.html` |
| 2 | `site/how-to-read.qmd` | How to read this course | top level | — |
| 3 | `site/chapters/01-two-free-numbers.qmd` | 1. Two free numbers | Part I, The Puzzle | `/two-free-numbers.html` |
| 4 | `site/chapters/02-value-premium-in-the-data.qmd` | 2. The value premium in the data | Part I, The Puzzle | `/financial-data.html` |
| 5 | `site/chapters/03-pricing-by-euler-equation.qmd` | 3. Pricing by Euler equation | Part II, The Toolkit | — |
| 6 | `site/chapters/04-epstein-zin-preferences.qmd` | 4. Epstein-Zin preferences | Part II, The Toolkit | — |
| 7 | `site/chapters/05-long-run-risks.qmd` | 5. Long-run risks: the endowment | Part II, The Toolkit | `/long-run-risks-model.html` |
| 8 | `site/chapters/06-log-linear-solution.qmd` | 6. The log-linear solution | Part III, Solving the Model | — |
| 9 | `site/chapters/07-quadrature-solution.qmd` | 7. The quadrature solution | Part III, Solving the Model | — |
| 10 | `site/chapters/08-calibrating-cash-flows.qmd` | 8. Calibrating cash flows from data | Part IV, Confronting the Data | `/measuring-leverage.html` |
| 11 | `site/chapters/09-the-market-test.qmd` | 9. The market test | Part IV, Confronting the Data | `/time-series.html` |
| 12 | `site/chapters/10-value-premium-resolved.qmd` | 10. The value premium, resolved | Part IV, Confronting the Data | `/cross-section.html` |
| 13 | `site/chapters/11-price-your-own-claim.qmd` | 11. Price your own claim | Part V, Your Turn | `/price-your-own-claim.html` |
| 14 | `site/chapters/12-objections-and-limits.qmd` | 12. Objections and limits | Part V, Your Turn | `/objections.html` |
| 15 | `site/reference/installation.qmd` | Installation | Reference | `/installation.html`, `/package.html` |
| 16 | `site/reference/api.qmd` | API | Reference | `/api.html` |
| 17 | `site/reference/glossary.qmd` | Glossary | Reference | `/background.html` |
| 18 | `site/reference/references.qmd` | References | Reference | `/references.html` |

## Conventions

Every page must appear in the sidebar, and every sidebar entry must exist on
disk. Both directions are checked, so a new page that is not listed in
`site/_quarto.yml` fails the suite.

Each chapter carries a fixed set of parts. First comes a collapsed callout
titled "Recall", which must appear before the exercises. Second come the
exercises, and any chapter with an `## Exercises` heading must also ship a
collapsed callout titled "Check your answer". Third comes a link to
`reference/references.qmd`. All three are enforced by `tests/test_site.py`.

Pages run their Python at build time, so a render is what checks the code.
Quarto is configured with `freeze: auto`, and the cached output lives in
`site/_freeze`. Continuous integration renders from the committed freeze, so
after you change a page you run `make site` and commit the regenerated freeze
along with it. A page that runs Python without a freeze entry fails
`test_freeze_covers_every_executed_page`. Note that the freeze keys its figure
files by cell number, so moving or removing a cell can leave an orphaned file
behind, and you should delete it.

No number appears on a page unless one of the page's own cells prints it, or
the page attributes it to the paper. See `NUMBERS.md` for the rule and for the
figures that are quoted from the paper rather than computed.

Names removed from the public API must not survive anywhere a reader can see
them, prose included. The list is `REMOVED_API_NAMES` in `tests/test_site.py`,
and it covers the site, `README.md`, and the scripts in `examples/`.

## Build commands

Run `make site` to render, `make preview` to serve the site locally with live
reload, and `make freeze` to delete `site/_freeze` and render everything from
scratch. Run `uv run pytest tests/test_site.py` for the structural checks alone.
