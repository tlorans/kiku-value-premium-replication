# Contributing

The rules below govern the prose on the site and in the package. For the
site's page map and structural checks see `SITE_MAP.md`, and for where
the numbers come from see `NUMBERS.md`.

## Voice

Write short declarative sentences with one idea in each. Do not hedge,
and do not use marketing language. The register to match is a sentence
like "Average returns never enter." Do not ask rhetorical questions.

## Words not to use

The following words do not belong anywhere in the package or on the
site. Grep before you open a pull request.

The first group would misrepresent what the model is about: `climate`,
`carbon`, `transition`, `physical risk`, `stranded`, `sustainability`,
`ESG`, `net zero`, `policy`, `regulation`, `decarbonization`. Note that
`tests/test_api_layout.py::test_no_climate_imports` guards the related
case of importing a climate module into the package.

The second group is one word, `scenario`. Write `shock`, `path`, or
`state` instead, because those are what the model actually has.

The third group is marketing adjectives: `powerful`, `revolutionary`,
`game-changing`, `cutting-edge`, `seamless`.

## Truth discipline

No number appears on a page unless one of the page's own cells prints
it, or the page attributes it to Kiku (2006). See `NUMBERS.md`.

Every claim is scoped. The narrow claim is that when the forecast and
the discount rate come from one process, the cross-section is priced,
and when they come from two, nothing bounds the error. The claim is not
that the model is true, and no page may contradict that scoping.

Citations are limited to the works listed in
`site/reference/references.qmd`. A few further references are named on
the page that uses them, such as Fama and French on the portfolio sort.
Any other empirical claim needs a source added to the references page
before it ships.

Do not add applications, use cases, or industry examples. The worked
examples stay synthetic or stay on the paper's portfolios.

The site is a library, not a syllabus. Do not write "this course",
"this chapter", Parts, exercises, or takeaways.

## When a script disagrees with the prose

Stop and raise it rather than adjusting the prose to match what you
expected. If a script's output contradicts a claim a page makes, the
page may be wrong, the code may be wrong, or the claim may never have
been true, and the three need different fixes. The same applies when
the package turns out to lack a capability that a planned page
requires.

## Working on the repo

Use `uv` for everything, so `uv pip install -e .` to install,
`uv run pytest` for the gate, and `uv run python examples/<name>.py`
to run a script.

For the site, `make preview` serves it locally with live reload and
`make site` renders it. Pages run their Python at render time, so a
render is what checks the code on a page. Continuous integration
renders from the committed `site/_freeze`, which means a page change is
not finished until you have rendered and committed the regenerated
freeze alongside it.
