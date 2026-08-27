# lrrcs GE Book Docs Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Turn the Just the Docs GitHub Pages site into a short book: landing, Getting started, Cash flows then prices, then two full passes (the market; value versus growth).

**Architecture:** Keep GitHub Pages + Just the Docs. Tests in `tests/test_docs.py` encode the book (titles, nav, four H2s, imports, deleted replica pages). New chapters are written as markdown; `time-series.md` and `cross-section.md` keep their URLs with new titles. Old paper-section pages are deleted last so their URLs 404.

**Tech Stack:** Just the Docs (`jekyll-remote-theme`), GitHub Pages, pytest, `uv run pytest`.

**Spec:** `docs/superpowers/specs/2026-08-27-lrrcs-book-docs-design.md`

## Global Constraints

- Site title: `Long-run risks` (not “Long-run risks and the cross section”)
- Map chapter title: `Cash flows, then prices`; file `docs/cash-flows-then-prices.md`; URL `/cash-flows-then-prices.html`; `docs/recipe.md` must not exist
- Claim chapter H2s, in order: `## Data`, `## Calibrate cash flows`, `## Solve`, `## Compare pricing moments`
- Documented imports: `import tidyfinance as tf` and `import lrrcs as lrr`; fenced `python`; no `from lrrcs.model import` (or other submodule imports) as the documented form
- No `kiku_value_premium`, `connect_wrds`, `print_value_premium`
- Printed numbers stay: market `8.56` / `7.53`; value `13.88` vs growth `7.81`; model premium about `5.3`; Table II \(\phi\) 6.2 / 2.6 / 2.8
- Cash flows in, prices out: average returns never enter calibration
- Tutorial voice (“you” / “we”), not paper “I construct”
- Stay on Just the Docs; `docs/_config.yml` still excludes `superpowers/`
- Do not change Python solvers, Table II defaults, or `examples/*.py` (except if a docs URL is cited — none are required)
- Run tests with `uv run pytest tests/test_docs.py -v`
- On Windows PowerShell do not use bash heredocs in `git commit`

---

## File map

**Create**

- `docs/getting-started.md` — first book chapter (install, five-line solve, package split)
- `docs/cash-flows-then-prices.md` — map: four steps, IMRS/Euler, skeleton code

**Rewrite**

- `docs/index.md` — landing (pitch, hero code, Start here, two claims)
- `docs/time-series.md` — **The market**, four H2s, URL unchanged
- `docs/cross-section.md` — **Value versus growth**, four H2s, URL unchanged
- `docs/_config.yml` — title, description, footer
- `README.md` — title and docs table
- `docs/package.md` — drop Other portfolios; link the book
- `tests/test_docs.py` — book contract instead of paper-site contract

**Keep, no content change required**

- `docs/installation.md` — extras and WRDS reference (already correct)
- `docs/api.md` — root-function map (already correct)
- `docs/_includes/head_custom.html`, `docs/assets/js/mathjax-script-type.js`, `docs/_sass/color_schemes/kiku.scss`

**Delete (Task 6; those URLs 404)**

- `docs/empirical.md`, `docs/model.md`, `docs/calibration.md`, `docs/implications.md`
- `docs/other-risk-premia.md`, `docs/climate.md`, `docs/further.md`, `docs/generalization.md`
- `docs/replica.md`, `docs/value.md`

---

### Task 1: Site title and book-scaffold tests

**Files:**
- Modify: `tests/test_docs.py` (replace paper-identity tests; keep MathJax and package companion checks)
- Modify: `docs/_config.yml` (title, description, footer)
- Create: `docs/getting-started.md` (stub)
- Create: `docs/cash-flows-then-prices.md` (stub)
- Modify: `docs/time-series.md` front matter only (`nav_order: 4`)
- Modify: `docs/cross-section.md` front matter only (`nav_order: 5`)

**Interfaces:**
- Consumes: existing Just the Docs site; current `tests/test_docs.py`
- Produces: `_config.yml` title `Long-run risks`; stub files with the locked titles and `nav_order`; a `test_docs.py` that no longer requires the paper narrative

- [ ] **Step 1: Write the failing tests**

Replace `tests/test_docs.py` with this file. Do not keep `test_site_is_the_paper_not_a_tutorial`, `test_introduction_is_macro_finance`, `test_index_links_recipe_pages`, or `test_pages_nav_is_paper_order`. Keep MathJax and package-companion checks. Do **not** yet assert that replica pages are deleted (that is Task 6). Do **not** yet assert claim-chapter H2s or the new H1s on `time-series.md` / `cross-section.md` (Tasks 4–5).

```python
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs"

BOOK_PAGES = (
    "index.md",
    "getting-started.md",
    "cash-flows-then-prices.md",
    "time-series.md",
    "cross-section.md",
    "package.md",
    "installation.md",
    "api.md",
)

PACKAGE_PAGES = ("installation.md", "api.md", "package.md")


def _text(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def _parent(name: str) -> str | None:
    for line in _text(name).splitlines()[:12]:
        if line.startswith("parent:"):
            return line.split(":", 1)[1].strip()
    return None


def _front_nav_order(name: str) -> int | None:
    for line in _text(name).splitlines()[:12]:
        if line.startswith("nav_order:"):
            return int(line.split(":", 1)[1].strip())
    return None


def test_just_the_docs_and_title():
    cfg = (ROOT / "_config.yml").read_text(encoding="utf-8")
    assert "just-the-docs" in cfg
    assert "title: Long-run risks\n" in cfg
    assert "and the cross section" not in cfg
    assert "calibrate cash flows" in cfg.lower()
    assert "superpowers" in cfg


def test_book_pages_exist():
    for name in BOOK_PAGES:
        assert (ROOT / name).is_file(), name
    assert not (ROOT / "recipe.md").exists()


def test_new_chapter_front_matter():
    gs = _text("getting-started.md")
    assert "title: Getting started" in gs
    assert "# Getting started" in gs
    assert _parent("getting-started.md") is None
    assert _front_nav_order("getting-started.md") == 2

    cf = _text("cash-flows-then-prices.md")
    assert "title: Cash flows, then prices" in cf
    assert "# Cash flows, then prices" in cf
    assert _parent("cash-flows-then-prices.md") is None
    assert _front_nav_order("cash-flows-then-prices.md") == 3

    assert _parent("time-series.md") is None
    assert _front_nav_order("time-series.md") == 4
    assert _parent("cross-section.md") is None
    assert _front_nav_order("cross-section.md") == 5
    assert _front_nav_order("package.md") == 6
    assert _parent("installation.md") == "Package"
    assert _parent("api.md") == "Package"


def test_mathjax_and_sidebar_theme():
    head = (ROOT / "_includes" / "head_custom.html").read_text(encoding="utf-8")
    assert "mathjax" in head.lower()
    js = (ROOT / "assets" / "js" / "mathjax-script-type.js").read_text(encoding="utf-8")
    assert "math/tex" in js
    assert (ROOT / "_sass" / "color_schemes" / "kiku.scss").exists()


def test_package_pages_are_tidyfinance_companion():
    for name in PACKAGE_PAGES:
        text = _text(name)
        assert "import tidyfinance as tf" in text
        assert "import lrrcs as lrr" in text
        assert "kiku_value_premium" not in text
        assert "connect_wrds" not in text
        assert "from lrrcs.model import" not in text
        assert "from lrrcs.empirical import" not in text
    readme = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    assert "import lrrcs as lrr" in readme
    assert "tidyfinance" in readme
    assert "kiku_value_premium" not in readme


def test_code_fences_use_flat_lrr():
    for name in BOOK_PAGES:
        text = _text(name)
        if "```python" not in text:
            continue
        assert "kiku_value_premium" not in text
        assert "from lrrcs.model import" not in text
        assert "from lrrcs.empirical import" not in text
        assert "from lrrcs.calibration import" not in text
        assert "from lrrcs.implications import" not in text
        assert "print_value_premium" not in text
        assert "lrr." in text or "import lrrcs as lrr" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_docs.py::test_just_the_docs_and_title tests/test_docs.py::test_book_pages_exist tests/test_docs.py::test_new_chapter_front_matter -v`

Expected: FAIL — `_config.yml` still has `title: Long-run risks and the cross section`; `getting-started.md` and `cash-flows-then-prices.md` are missing.

- [ ] **Step 3: Write minimal implementation**

In `docs/_config.yml` set:

```yaml
title: Long-run risks
description: Calibrate cash flows, then ask whether the model matches asset-pricing moments.
```

and

```yaml
footer_content: "Calibrate cash flows, then ask whether asset-pricing moments match. MIT License."
```

Leave `remote_theme`, plugins, `color_scheme: kiku`, MathJax, `aux_links`, `exclude: superpowers`, and callouts unchanged.

Create `docs/getting-started.md`:

```markdown
---
title: Getting started
nav_order: 2
---

# Getting started
```

Create `docs/cash-flows-then-prices.md`:

```markdown
---
title: Cash flows, then prices
nav_order: 3
---

# Cash flows, then prices
```

In `docs/time-series.md` change only the front-matter `nav_order` from `2` to `4`. Leave `title: Time series` and the body.

In `docs/cross-section.md` change only the front-matter `nav_order` from `3` to `5`. Leave `title: Cross section` and the body.

- [ ] **Step 4: Run the tests and make sure they pass**

Run: `uv run pytest tests/test_docs.py -v`

Expected: PASS (all functions in the new file).

- [ ] **Step 5: Commit**

```powershell
git add tests/test_docs.py docs/_config.yml docs/getting-started.md docs/cash-flows-then-prices.md docs/time-series.md docs/cross-section.md
git commit -m "test: scaffold GE book docs title and chapter stubs"
```

---

### Task 2: Landing page and Getting started

**Files:**
- Modify: `tests/test_docs.py` (add `test_home_is_landing`, `test_getting_started`)
- Modify: `docs/index.md` (replace entire file)
- Modify: `docs/getting-started.md` (replace stub)

**Interfaces:**
- Consumes: Task 1 stubs and site title
- Produces: Home H1 `# Long-run risks`; Start here → Getting started; Getting started does not call `set_wrds_credentials`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_docs.py`:

```python
def test_home_is_landing():
    text = _text("index.md")
    assert "# Long-run risks" in text
    assert "## Introduction" not in text
    assert "I show" not in text
    assert "Start here" in text
    assert "getting-started" in text
    assert "cash-flows-then-prices" in text
    assert "time-series" in text
    assert "cross-section" in text
    assert "```python" in text
    assert "import tidyfinance as tf" in text
    assert "import lrrcs as lrr" in text
    assert "print_long_short_premium" in text
    for stem in (
        "empirical",
        "calibration",
        "implications",
        "climate",
        "further",
        "other-risk-premia",
        "generalization",
        "replica",
    ):
        assert f"{stem}.html" not in text
        assert f"{stem}.md" not in text
    assert "model.html" not in text


def test_getting_started():
    text = _text("getting-started.md")
    assert "uv pip install -e ." in text
    assert "import tidyfinance as tf" in text
    assert "import lrrcs as lrr" in text
    assert "solve_analytical" in text
    assert "cash-flows-then-prices" in text
    assert "set_wrds_credentials" not in text
    assert "What that did not" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_docs.py::test_home_is_landing tests/test_docs.py::test_getting_started -v`

Expected: FAIL — `index.md` still has `# Long-run risks and the cross section` and `## Introduction`; Getting started stub has no `uv pip install`.

- [ ] **Step 3: Write the landing and Getting started pages**

Replace `docs/index.md` with:

````markdown
---
title: Home
nav_order: 1
permalink: /
---

# Long-run risks

Calibrate cash flows, then ask whether the model matches asset-pricing moments.

Companion to [tidyfinance](https://www.tidy-finance.org/): tidyfinance gets data and sorts; `lrrcs` calibrates cash-flow loadings and prices claims. Average returns never enter the cash-flow step.

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

[Start here]({{ '/getting-started.html' | relative_url }})

## The four steps

1. Form the claim(s) from data.
2. Calibrate cash-flow dynamics.
3. Solve the long-run risks model.
4. Compare model asset-pricing moments to the data.

That loop is [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}). Then we run it twice: [The market]({{ '/time-series.html' | relative_url }}) and [Value versus growth]({{ '/cross-section.html' | relative_url }}).

[Package]({{ '/package.html' | relative_url }}) · [Installation]({{ '/installation.html' | relative_url }}) · [API]({{ '/api.html' | relative_url }}) · [GitHub](https://github.com/tlorans/kiku-value-premium-replication)
````

Replace `docs/getting-started.md` with:

````markdown
---
title: Getting started
nav_order: 2
---

# Getting started
{: .no_toc }

1. TOC
{:toc}

Python 3.11+. Clone the repository and install in editable mode with `uv`.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

**What that did.** It loaded Table II of Kiku (2006) — the default consumption process, preferences, and dividend loadings — solved the model, and printed the long–short premium the Euler equation assigns. You did not estimate anything.

**What that did not do.** It did not match that premium. Average returns never entered. It did not touch WRDS.

tidyfinance gets data and sorts. `lrrcs` calibrates cash-flow loadings and prices claims. This first run used only `lrrcs`. You will need both when you form claims from CRSP and Compustat.

For Numba, matplotlib, parquet, and WRDS credentials, see [Installation]({{ '/installation.html' | relative_url }}).

Next: [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}).
````

- [ ] **Step 4: Run the tests and make sure they pass**

Run: `uv run pytest tests/test_docs.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add tests/test_docs.py docs/index.md docs/getting-started.md
git commit -m "docs: add book landing and Getting started"
```

---

### Task 3: Cash flows, then prices

**Files:**
- Modify: `tests/test_docs.py` (add `test_cash_flows_then_prices`)
- Modify: `docs/cash-flows-then-prices.md` (replace stub)

**Interfaces:**
- Consumes: Task 2 “Next” link to this page
- Produces: Map chapter with IMRS/Euler, the four step names, and skeleton `tf` + `lrr` code; not a third full pass (no 8.56 / 13.88 result tables)

- [ ] **Step 1: Write the failing test**

Append to `tests/test_docs.py`:

```python
def test_cash_flows_then_prices():
    text = _text("cash-flows-then-prices.md")
    assert "Calibrate cash flows" in text
    assert "Compare pricing moments" in text
    assert "M_{t+1}" in text or "m_{t+1}" in text
    assert "import tidyfinance as tf" in text
    assert "import lrrcs as lrr" in text
    assert "get_table_ii_params" in text
    assert "calibrate_from_data" in text
    assert "compute_asset_pricing_moments" in text or "print_long_short_premium" in text
    assert "time-series" in text
    assert "cross-section" in text
    assert "8.56" not in text
    assert "13.88" not in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_docs.py::test_cash_flows_then_prices -v`

Expected: FAIL — stub has no IMRS and no `calibrate_from_data`.

- [ ] **Step 3: Write the map chapter**

Replace `docs/cash-flows-then-prices.md` with:

````markdown
---
title: Cash flows, then prices
nav_order: 3
---

# Cash flows, then prices
{: .no_toc }

1. TOC
{:toc}

Every claim in this book is judged the same way. Form the claim from data. Calibrate how its dividends move with consumption. Solve for prices. Then ask whether those prices look like the data. Average returns never enter the second step. If they did, the fourth step would not be a test.

The household is Epstein and Zin (1989) / Weil (1989). Risk aversion $$\gamma$$ and the elasticity of intertemporal substitution $$\psi$$ are different numbers. The intertemporal marginal rate of substitution is

$$
M_{t+1}=\delta^\theta (C_{t+1}/C_t)^{-\theta/\psi} R_{c,t+1}^{\theta-1},
\qquad
\theta=\frac{1-\gamma}{1-1/\psi}.
$$

The Euler equation is the whole pricing theory: $$\mathrm{E}_t[M_{t+1}R_{i,t+1}]=1$$. Table II uses $$\delta=0.999$$, $$\gamma=10$$, $$\psi=1.5$$, so $$\theta\neq 1$$ and news about wealth is priced. Under power utility ($$\gamma=1/\psi$$) that news is not priced, and a gap in dividend loadings on slow consumption cannot produce a large premium.

## The four steps

**Data.** Form the claim or claims. Consumption growth and dividend growth are the cash-flow series. tidyfinance supplies CRSP, Compustat, CCM, and NYSE breakpoints. `lrrcs` still builds Campbell–Shiller dividends and historical book equity.

**Calibrate cash flows.** Match mean and persistence of consumption growth, persistence of $$x_t$$, dividend volatilities, and each claim’s loading on slow consumption. Do not match mean returns, Sharpe ratios, or CAPM betas. Table II is the default. `calibrate_from_data` is the first-pass helper for a new sort. If simulated consumption does not look like the sample, stop.

**Solve.** Give those locked cash-flow numbers to `solve_analytical` or `ModelSolver`. The Euler equation returns prices and expected returns.

**Compare pricing moments.** Equity premium, risk-free rate, return volatility, mean $$\log(P/D)$$, and — when there are two legs — the long–short premium and the price–dividend ranking. Success is the model column close to the data column without having seen those numbers in calibration.

## Skeleton

Both later chapters copy this shape.

```python
import pandas as pd
import tidyfinance as tf
import lrrcs as lrr

tf.set_wrds_credentials()
bm = lrr.build_annual_panel(refresh=False)
dc = pd.read_csv("data/consumption_annual.csv").set_index("year")["dc"]

# Table II locks the household. For a new sort, set params.dividends to
# lrr.calibrate_from_data(dc, long=..., short=..., market=...).
params = lrr.get_table_ii_params()
print(lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=params))

lrr.print_long_short_premium(lrr.solve_analytical(params))
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
print(lrr.compute_asset_pricing_moments(solver))
```

Next: run the four steps on [the market]({{ '/time-series.html' | relative_url }}), then on [value versus growth]({{ '/cross-section.html' | relative_url }}).
````

- [ ] **Step 4: Run the tests and make sure they pass**

Run: `uv run pytest tests/test_docs.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add tests/test_docs.py docs/cash-flows-then-prices.md
git commit -m "docs: add Cash flows, then prices map chapter"
```

---

### Task 4: The market (rewrite `time-series.md`)

**Files:**
- Modify: `tests/test_docs.py` (add `test_market_chapter`)
- Modify: `docs/time-series.md` (replace entire file; URL stays `/time-series.html`)

**Interfaces:**
- Consumes: four-step names from Task 3; Table II market $$\phi=2.8$$; printed 8.56 / 7.53
- Produces: title/H1 **The market**; H2s Data → Calibrate cash flows → Solve → Compare pricing moments in that order; no Melin/climate closer; next link is value versus growth

- [ ] **Step 1: Write the failing test**

Append to `tests/test_docs.py`:

```python
H2S = (
    "## Data",
    "## Calibrate cash flows",
    "## Solve",
    "## Compare pricing moments",
)


def test_market_chapter():
    text = _text("time-series.md")
    assert "title: The market" in text
    assert "# The market" in text
    assert _parent("time-series.md") is None
    assert _front_nav_order("time-series.md") == 4
    positions = [text.index(h) for h in H2S]
    assert positions == sorted(positions)
    assert "8.56" in text and "7.53" in text
    assert "```python" in text
    assert "import lrrcs as lrr" in text
    assert "build_annual_panel" in text or "get_table_ii_params" in text
    assert "simulate_cashflow_moments" in text
    assert "Melin" not in text
    assert "other-risk-premia" not in text
    assert "cross-section" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_docs.py::test_market_chapter -v`

Expected: FAIL — page is still `# Time series` and has no `## Data`.

- [ ] **Step 3: Rewrite the market chapter**

Replace `docs/time-series.md` with:

````markdown
---
title: The market
nav_order: 4
---

# The market
{: .no_toc }

1. TOC
{:toc}

**Question.** Can this household price the *market* — the value-weighted claim on all listed stocks — year after year?

That is the test Bansal and Yaron (2004) wrote the model for. One claim. Not a ranking of firms. The four steps are those of [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}).

## Data

Consumption is real per-capita nondurables plus services. Market dividends are Campbell–Shiller dividends on the CRSP value-weighted portfolio of ordinary shares, deflated, 1930–2003. The objects are how consumption and *market* dividends grow. Not the average stock return.

tidyfinance supplies CRSP, Compustat, CCM, and NYSE breakpoints. `lrrcs` still builds Campbell–Shiller dividends.

```python
import pandas as pd
import tidyfinance as tf
import lrrcs as lrr

tf.set_wrds_credentials()
bm = lrr.build_annual_panel(refresh=False)
print(lrr.table_i(bm))
dc = pd.read_csv("data/consumption_annual.csv").set_index("year")["dc"]
print(lrr.table_vi_data(bm, dc))
```

Defaults are 1930–2003. `refresh=True` rebuilds the extracts. Core install without WRDS still solves Table II in the next two steps.

## Calibrate cash flows

Consumption growth is not white noise. It has a small persistent expected-growth piece $$x_t$$ and a variance that itself moves. Market dividends are consumption with extra leverage on those shocks. Monthly loading on $$x_t$$ is $$\phi_m=2.8$$. Persistence is $$\rho=0.98$$.

**What is matched.** Mean and persistence of consumption growth, persistence of $$x_t$$, market dividend volatility, market loading on slow consumption.

**What is not matched.** The average market return, the Sharpe ratio, the CAPM beta of the market.

| Symbol | Value | Meaning |
|:---|---:|:---|
| $$\delta$$ | 0.999 | time discount |
| $$\gamma$$ | 10 | risk aversion |
| $$\psi$$ | 1.5 | EIS |
| $$\mu_c$$ | 0.0015 | mean monthly consumption growth |
| $$\rho$$ | 0.98 | persistence of $$x_t$$ |
| $$\varphi_x$$ | 0.032 | scale of shocks to $$x$$ |
| $$\sigma$$ | 0.0064 | average consumption volatility |

Market dividends: $$\mu=0.0012$$, $$\phi=2.8$$, $$\varphi_\sigma=7.5$$, $$\alpha=0.55$$.

Simulated consumption, 1000 samples of 74 years: mean growth 1.86 percent against 1.96 in the data; volatility 2.16 against 2.20; first autocorrelation 0.43 against 0.44. If those fail, stop. The premium that comes next would then be a free parameter in disguise.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
params.dividends["market"].phi  # 2.8
params.cons.rho                 # 0.98
print(lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=params))
```

## Solve

The IMRS and Euler equation are on [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}). Table II of Kiku (2006) is the default household. `solve_analytical` is the linearization shortcut. `ModelSolver` is the Euler map on a grid.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
lrr.print_long_short_premium(lrr.solve_analytical(params))
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
```

## Compare pricing moments

Given those locked cash-flow numbers, what prices does the Euler equation assign to the market and the safe bond?

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

E[R] is the average simple return, percent per year. E[pd] is average $$\log(P/D)$$. Numbers in parentheses are standard errors across simulated samples. Market return volatility is 20.1 percent in both. The safe rate is about seventy basis points too high. The equity premium is a little short of the sample. Close enough to ask a second question.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
lrr.print_asset_pricing_moments(lrr.compute_asset_pricing_moments(solver))
```

The market column on that printout is this page. Value and growth are [Value versus growth]({{ '/cross-section.html' | relative_url }}). Matching the market does not rank firms.
````

- [ ] **Step 4: Run the tests and make sure they pass**

Run: `uv run pytest tests/test_docs.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add tests/test_docs.py docs/time-series.md
git commit -m "docs: rewrite the market as a four-step pass"
```

---

### Task 5: Value versus growth (rewrite `cross-section.md`)

**Files:**
- Modify: `tests/test_docs.py` (add `test_value_versus_growth_chapter`)
- Modify: `docs/cross-section.md` (replace entire file; URL stays `/cross-section.html`)

**Interfaces:**
- Consumes: same four H2s as Task 4; printed 7.81 / 13.88 / 5.3; $$\phi_V=6.2$$, $$\phi_G=2.6$$
- Produces: title/H1 **Value versus growth**; no link to other-risk-premia or climate; six-percent premium is not a calibration target

- [ ] **Step 1: Write the failing test**

Append to `tests/test_docs.py`:

```python
def test_value_versus_growth_chapter():
    text = _text("cross-section.md")
    assert "title: Value versus growth" in text
    assert "# Value versus growth" in text
    assert _parent("cross-section.md") is None
    assert _front_nav_order("cross-section.md") == 5
    h2s = (
        "## Data",
        "## Calibrate cash flows",
        "## Solve",
        "## Compare pricing moments",
    )
    positions = [text.index(h) for h in h2s]
    assert positions == sorted(positions)
    assert "7.81" in text and "13.88" in text
    assert "5.3" in text
    assert "calibrate_from_data" in text
    assert "```python" in text
    assert "import lrrcs as lrr" in text
    assert "other-risk-premia" not in text
    assert "climate.html" not in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_docs.py::test_value_versus_growth_chapter -v`

Expected: FAIL — page is still `# Cross section`.

- [ ] **Step 3: Rewrite the value-versus-growth chapter**

Replace `docs/cross-section.md` with:

````markdown
---
title: Value versus growth
nav_order: 5
---

# Value versus growth
{: .no_toc }

1. TOC
{:toc}

**Question.** Why do cheap stocks (high book-to-market, *value*) earn more than expensive stocks (low book-to-market, *growth*) when both move about one-for-one with the market?

The last page priced one claim. This page prices two, with the same household. Kiku (2006) is the worked example. The six-percent gap in average returns is a fact to be explained. It is not a number you feed the calibrator.

## Data

Each June, sort ordinary shares on NYSE, AMEX, and NASDAQ by book-to-market, using NYSE cutoffs (Fama and French 1993). Growth is the bottom fifth. Value is the top fifth. Dividends are inferred from the gap between the return with dividends and the return without dividends (Campbell and Shiller). Sample: 1930–2003.

|  | E[R] % | σ(R) % | E[log P/D] |
|:---|---:|---:|---:|
| Growth | 7.81 (1.98) | 20.2 | 3.61 (0.18) |
| Value | 13.88 (1.74) | 29.9 | 3.25 (0.12) |
| Market | 8.56 (1.79) | 20.1 | 3.34 (0.13) |

Value earned about six percent more per year. Value was cheaper (3.25 against 3.61). Both CAPM betas sit near 1.03, so the return gap is not a market-beta fact.

```python
import lrrcs as lrr

bm = lrr.build_annual_panel(refresh=False)
print(lrr.table_i(bm))
```

![Figure 1](figures/figure1.svg)

<p class="caption">Figure 1. Realized value minus growth, 1930–2003. The bars are positive in most years.</p>

## Calibrate cash flows

The household and the consumption process stay those of [the market]({{ '/time-series.html' | relative_url }}). Each claim differs only in four cash-flow numbers: mean dividend growth $$\mu$$, monthly loading $$\phi$$ on $$x_t$$, residual scale $$\varphi$$, and short-run correlation $$\alpha$$.

The data give an *annual* slope of dividend growth on two lags of consumption, equation (19). Printed $$\tilde\phi$$: growth $$-0.38$$ (1.34), value $$2.16$$ (1.44), market $$0.66$$ (1.20). That ranking is the check. The solver wants monthly $$\phi$$. Table II: $$\phi_{\text{value}}=6.2$$, $$\phi_{\text{growth}}=2.6$$. Value gets the larger $$\phi$$ because (19) said so, not because value had a larger average return. The annual slope never enters the solver as a number.

```python
import lrrcs as lrr

dividends = lrr.calibrate_from_data(
    dc, frequency="annual", window=2,
    long=dd_value, short=dd_growth, market=dd_market,
)
params = lrr.get_table_ii_params()
params.dividends["value"].phi   # 6.2 at Table II
params.dividends["growth"].phi  # 2.6
```

There is no argument for returns.

## Solve

Same preferences as the market pass. `solve_analytical` and `ModelSolver` resolve either pair. The market key remains the time-series check on this calibration.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
lrr.print_long_short_premium(lrr.solve_analytical(params))
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
```

## Compare pricing moments

With those four numbers locked, what expected returns and price–dividend ratios does the Euler equation assign?

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Growth | 7.81 (1.98) | 6.07 (2.91) | 3.61 (0.18) | 3.65 (0.06) |
| Value | 13.88 (1.74) | 11.36 (4.30) | 3.25 (0.12) | 3.10 (0.15) |
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

The model gap is about 5.3 percent against about 6 percent in the data. Mean price–dividend levels are about 24.7 on value versus 39.8 on growth. Value is both the high-return claim and the low price–dividend claim. The market row is the time-series check that the same investor still prices the aggregate claim.

Do not confuse $$\phi$$ with a CAPM beta. The model’s ratio of value to growth CAPM betas is 0.92. Value’s market beta is *lower*, as in the data. The priced risk is exposure to $$x_t$$.

Failure would be: value earns less than growth; value’s price–dividend ratio sits above growth’s; or value’s CAPM beta is much larger, so covariance with the market would have been enough.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
lrr.print_asset_pricing_moments(lrr.compute_asset_pricing_moments(solver))
```

![Long-run risk premia](figures/lr_premium_decomposition.svg)

<p class="caption">Analytical long-run premia. The gap is $$\phi_V=6.2$$ versus $$\phi_G=2.6$$, scaled by $$\rho=0.98$$ and the Epstein–Zin price of long-run news.</p>
````

- [ ] **Step 4: Run the tests and make sure they pass**

Run: `uv run pytest tests/test_docs.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add tests/test_docs.py docs/cross-section.md
git commit -m "docs: rewrite value versus growth as a four-step pass"
```

---

### Task 6: Package pages, README, delete replica files

**Files:**
- Modify: `tests/test_docs.py` (add deletion, README, and package-link tests)
- Modify: `docs/package.md` (drop Other portfolios; point at the book)
- Modify: `README.md` (title and docs table)
- Delete: `docs/empirical.md`, `docs/model.md`, `docs/calibration.md`, `docs/implications.md`, `docs/other-risk-premia.md`, `docs/climate.md`, `docs/further.md`, `docs/generalization.md`, `docs/replica.md`, `docs/value.md`

**Interfaces:**
- Consumes: book pages from Tasks 2–5
- Produces: replica URLs 404; README matches the landing; `package.md` does not link `generalization.html`

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_docs.py`:

```python
DELETED = (
    "empirical.md",
    "model.md",
    "calibration.md",
    "implications.md",
    "other-risk-premia.md",
    "climate.md",
    "further.md",
    "generalization.md",
    "replica.md",
    "value.md",
    "recipe.md",
)


def test_deleted_pages_gone():
    for name in DELETED:
        assert not (ROOT / name).exists(), name


def test_package_page_points_at_the_book():
    text = _text("package.md")
    assert "generalization" not in text
    assert "getting-started" in text or "time-series" in text or "cash-flows-then-prices" in text


def test_readme_matches_landing():
    text = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    assert text.startswith("# Long-run risks\n")
    assert "and the cross section" not in text.splitlines()[0]
    assert "six-step" not in text.lower() and "6-step" not in text.lower()
    assert "getting-started" in text
    assert "cash-flows-then-prices" in text
    assert "time-series" in text
    assert "cross-section" in text
    assert "other-risk-premia" not in text
    assert "climate.html" not in text
    assert "import lrrcs as lrr" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_docs.py::test_deleted_pages_gone tests/test_docs.py::test_package_page_points_at_the_book tests/test_docs.py::test_readme_matches_landing -v`

Expected: FAIL — replica files still exist; `package.md` still links `generalization.html`; README still starts with `# Long-run risks and the cross section`.

- [ ] **Step 3: Edit package.md and README, then delete replica files**

Replace `docs/package.md` with:

````markdown
---
title: Package
nav_order: 6
has_children: true
has_toc: false
---

# Package

`lrrcs` is a companion to tidyfinance. tidyfinance gets data and sorts; `lrrcs` calibrates cash-flow loadings and prices claims.

```python
import tidyfinance as tf
import lrrcs as lrr
```

Start with the book: [Getting started]({{ '/getting-started.html' | relative_url }}), [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}), [The market]({{ '/time-series.html' | relative_url }}), [Value versus growth]({{ '/cross-section.html' | relative_url }}).

- [Installation]({{ '/installation.html' | relative_url }})
- [API]({{ '/api.html' | relative_url }})
````

Replace `README.md` with:

````markdown
# Long-run risks

Python package `lrrcs`, a companion to [tidyfinance](https://github.com/tidy-finance/py-tidyfinance).
The model is Bansal and Yaron (2004) long-run risks with Epstein–Zin preferences.
Kiku (2006) is the first cross-sectional column.

tidyfinance gets data and sorts. `lrrcs` calibrates cash-flow loadings and prices claims.
Average returns never enter the cash-flow step.

**Documentation:** [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)

| Page | What it is |
|---|---|
| [Getting started](https://tlorans.github.io/kiku-value-premium-replication/getting-started.html) | Install and a five-line solve |
| [Cash flows, then prices](https://tlorans.github.io/kiku-value-premium-replication/cash-flows-then-prices.html) | The four-step loop |
| [The market](https://tlorans.github.io/kiku-value-premium-replication/time-series.html) | One claim, time series |
| [Value versus growth](https://tlorans.github.io/kiku-value-premium-replication/cross-section.html) | Two legs, same household |

## Install

Python 3.11+.

```bash
git clone https://github.com/tlorans/kiku-value-premium-replication.git
cd kiku-value-premium-replication
uv pip install -e .
```

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

WRDS reconstruction: `uv pip install -e ".[data]"` then `tf.set_wrds_credentials()`.

## License

MIT
````

Delete these files (GitHub Pages will 404; do not add redirect stubs):

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

Leave unused SVGs under `docs/figures/`. Do not delete `figure1.svg`, `lr_premium_decomposition.svg`, or other files still referenced by the two claim chapters.

Do not edit `docs/installation.md` or `docs/api.md` unless a test fails (they already use `tf` + `lrr`).

- [ ] **Step 4: Run the tests and make sure they pass**

Run: `uv run pytest tests/test_docs.py -v`

Expected: PASS. Then run the default suite (only `test_docs.py` opens these markdown paths):

Run: `uv run pytest -m "not wrds" -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```powershell
git add tests/test_docs.py docs/package.md README.md
git add -u docs
git commit -m "docs: drop replica pages and point the package docs at the book"
```

`git add -u docs` stages the deletions. Confirm `git status` shows the ten replica files as deleted and does not stage `src/lrrcs.egg-info/`.

---

## Spec coverage

| Spec section | Task |
|---|---|
| Goal / thesis / shape / sidebar nav_order | 1 (orders, stubs), 2–5 (pages) |
| Homepage landing | 2 |
| Getting started | 2 |
| Cash flows, then prices | 3 |
| The market | 4 |
| Value versus growth | 5 |
| Package pages | 6 (`package.md`); installation/api unchanged |
| Config and README | 1 (config), 6 (README) |
| Files to delete / 404 | 6 |
| Tests contract | 1–6 |
| Non-goals (Quarto, other premia, solvers, redirects) | none of the tasks reopen these |
