# Follow-along Financial data and The market Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship two Tidy-Finance-style follow-along chapters (Financial data; The market) plus root helpers `expected_growth_proxy` and `filter_expected_growth`.

**Architecture:** Keep Just the Docs. Add `src/lrrcs/calibration/expected_growth.py` and re-export from `calibration/__init__.py` so auto-discovery puts the names at `lrr.`. Docs tests in `tests/test_docs.py` encode nav, H2s, and the polars/plotnine contract. Tutorial charts stay in markdown; no plotnine wrappers in the library.

**Tech Stack:** Python ≥ 3.11, numpy, scipy, polars/plotnine in `[data]`, pytest, `uv run pytest`, Just the Docs.

**Spec:** `docs/superpowers/specs/2026-08-27-follow-along-chapters-design.md`

## Global Constraints

- Documented imports on the two chapters, in this order when all four appear: `import polars as pl`, `import plotnine as p9`, `import tidyfinance as tf`, `import lrrcs as lrr`
- Fenced `python`; public names at `lrr.`; no `from lrrcs.model import` (or other submodule imports) as the documented form
- No `kiku_value_premium`, `connect_wrds`, `print_value_premium`
- The market H2s, exact strings in order: `## What long-run risk is`, `## Estimate x_t`, `## Calibrate dividends`, `## Simulate cash flows`, `## Solve and check returns and prices`
- Financial data title/H1 `Financial data`; `nav_order: 3`; no parent
- Nav: Getting started 2, Financial data 3, Cash flows then prices 4, The market 5, Value versus growth 6, Package 7
- Printed market numbers stay: `8.56` / `7.53`; value page still `7.81` / `13.88` / `5.3`
- Simulation and pricing use `lrr.get_table_ii_params()`, not annual \(\tilde\phi\) as monthly \(\phi\)
- Average returns never enter calibration
- `[data]` = `matplotlib`, `pyarrow`, `polars`, `plotnine`; core required deps unchanged
- Do not change solvers, Table II parameter values, `examples/*.py`, or `docs/cross-section.md` body
- Stay on Just the Docs; `docs/_config.yml` still excludes `superpowers/`
- Run tests with `uv run pytest`
- On Windows PowerShell do not use bash heredocs in `git commit`

---

## File map

**Create**

- `src/lrrcs/calibration/expected_growth.py` — `expected_growth_proxy`, `filter_expected_growth`
- `tests/test_expected_growth.py` — unit tests for those two
- `docs/financial-data.md` — retrieval chapter

**Modify**

- `src/lrrcs/calibration/__init__.py` — re-export the two names (required for `lrr.` auto-discovery)
- `src/lrrcs/calibration/leverage.py` — MA via `expected_growth_proxy`
- `tests/test_api_layout.py` — root names + `[data]` extras
- `tests/test_docs.py` — book contract
- `pyproject.toml` — `[data]` extras
- `docs/time-series.md` — rewrite The market
- `docs/index.md`, `docs/getting-started.md`, `docs/cash-flows-then-prices.md` (nav + pointer), `docs/cross-section.md` (nav_order only), `docs/package.md`, `docs/installation.md`, `docs/api.md`, `README.md`

**Do not touch**

- `src/lrrcs/model/solver.py`, `src/lrrcs/model/params.py` Table II numbers, `examples/*.py`, `docs/cross-section.md` body, paper SVGs

---

### Task 1: `expected_growth_proxy`

**Files:**
- Create: `tests/test_expected_growth.py`
- Create: `src/lrrcs/calibration/expected_growth.py`
- Modify: `src/lrrcs/calibration/__init__.py`
- Modify: `src/lrrcs/calibration/leverage.py`
- Test: `tests/test_expected_growth.py`, `tests/test_calibration.py`

**Interfaces:**
- Consumes: current `estimate_long_run_leverage(dc, dd, window=2) -> float`
- Produces: `expected_growth_proxy(dc, window: int = 2) -> np.ndarray` (same length as `dc`; `nan` for `t < window`; `ValueError` if `window < 1` or `len(dc) <= window`)

- [ ] **Step 1: Write the failing tests**

Create `tests/test_expected_growth.py`:

```python
import numpy as np
import pytest

from lrrcs.calibration.expected_growth import expected_growth_proxy
from lrrcs.calibration.leverage import estimate_long_run_leverage


def test_expected_growth_proxy_window_2():
    out = expected_growth_proxy([1, 2, 3, 4], window=2)
    assert isinstance(out, np.ndarray)
    np.testing.assert_allclose(out, [np.nan, np.nan, 1.5, 2.5], equal_nan=True)


def test_expected_growth_proxy_rejects_bad_window():
    with pytest.raises(ValueError):
        expected_growth_proxy([1.0, 2.0, 3.0], window=0)


def test_expected_growth_proxy_rejects_short_series():
    with pytest.raises(ValueError):
        expected_growth_proxy([1.0, 2.0], window=2)


def test_expected_growth_proxy_polars_series_returns_ndarray():
    import polars as pl

    out = expected_growth_proxy(pl.Series("dc", [1.0, 2.0, 3.0, 4.0]), window=2)
    assert isinstance(out, np.ndarray)
    np.testing.assert_allclose(out, [np.nan, np.nan, 1.5, 2.5], equal_nan=True)


def test_leverage_still_recovers_known_phi_via_proxy():
    rng = np.random.default_rng(2)
    n = 80
    dc = rng.normal(0.02, 0.03, size=n)
    ma = expected_growth_proxy(dc, window=2)
    dd = 0.01 + 2.16 * np.nan_to_num(ma, nan=0.0) + rng.normal(0, 0.05, size=n)
    phi = estimate_long_run_leverage(dc, dd, window=2)
    assert abs(phi - 2.16) < 0.4
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_expected_growth.py -v`

Expected: FAIL with `ModuleNotFoundError` or `ImportError` for `lrrcs.calibration.expected_growth`.

- [ ] **Step 3: Implement `expected_growth_proxy`**

Create `src/lrrcs/calibration/expected_growth.py`:

```python
"""Annual (or sample-frequency) expected-growth proxies for x_t."""
from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


def expected_growth_proxy(dc: ArrayLike, window: int = 2) -> np.ndarray:
    """Moving average of lagged consumption growth (Kiku eq. 19 regressor).

    Entry ``t`` is ``mean(dc[t-window:t])`` for ``t >= window``, and ``nan``
    before that.

    Examples
    --------
    ```python
    import lrrcs as lrr
    x_hat = lrr.expected_growth_proxy(dc, window=2)
    ```
    """
    y = np.asarray(dc, dtype=float).ravel()
    if window < 1:
        raise ValueError("window must be >= 1")
    if y.size <= window:
        raise ValueError("Series too short for the requested window")
    ma = np.full(y.size, np.nan)
    for t in range(window, y.size):
        ma[t] = float(np.mean(y[t - window : t]))
    return ma
```

Replace `src/lrrcs/calibration/leverage.py` with:

```python
"""Long-run leverage φ̃ via Kiku (2006) equation (19)."""
from __future__ import annotations
import numpy as np

from .expected_growth import expected_growth_proxy


def estimate_long_run_leverage(
    dc: np.ndarray,
    dd: np.ndarray,
    window: int = 2,
) -> float:
    """
    Estimate the long-run leverage coefficient φ̃ exactly as in the paper’s
    equation (19):

        Δd_t = d0 + φ̃ * MA(Δc, window) + ε_t

    Parameters
    ----------
    dc, dd : 1-d arrays of consumption and dividend growth (same frequency).
    window : number of lags to average (paper uses 2 years).

    Returns
    -------
    The OLS coefficient φ̃ on the moving average of lagged consumption growth.
    """
    dc = np.asarray(dc, dtype=float).ravel()
    dd = np.asarray(dd, dtype=float).ravel()
    if len(dc) != len(dd):
        raise ValueError("dc and dd must have the same length")
    ma = expected_growth_proxy(dc, window=window)
    mask = ~np.isnan(ma)
    y = dd[mask]
    x = ma[mask]
    x_demean = x - x.mean()
    y_demean = y - y.mean()
    phi = float(np.dot(x_demean, y_demean) / np.dot(x_demean, x_demean))
    return phi
```

Replace `src/lrrcs/calibration/__init__.py` with:

```python
from .leverage import estimate_long_run_leverage
from .expected_growth import expected_growth_proxy
from .from_data import calibrate_from_data, print_calibration_summary
from .table_ii import get_table_ii_dividends
from .simulation import print_moments, simulate_cashflow_moments

__all__ = [
    "estimate_long_run_leverage",
    "expected_growth_proxy",
    "calibrate_from_data",
    "get_table_ii_dividends",
    "simulate_cashflow_moments",
    "print_moments",
    "print_calibration_summary",
]
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_expected_growth.py tests/test_calibration.py -v`

Expected: PASS (all tests in both files).

- [ ] **Step 5: Commit**

```bash
git add tests/test_expected_growth.py src/lrrcs/calibration/expected_growth.py src/lrrcs/calibration/__init__.py src/lrrcs/calibration/leverage.py
git commit -m "feat: add expected_growth_proxy for the eq. 19 MA of lagged consumption"
```

---

### Task 2: `filter_expected_growth`

**Files:**
- Modify: `src/lrrcs/calibration/expected_growth.py`
- Modify: `src/lrrcs/calibration/__init__.py`
- Modify: `tests/test_expected_growth.py`
- Test: `tests/test_expected_growth.py`

**Interfaces:**
- Consumes: `expected_growth_proxy` from Task 1
- Produces: `filter_expected_growth(dc) -> dict` with keys `x`, `mu`, `rho`, `q`, `r`, `loglik`. `x` is `np.ndarray` length `n`. `ValueError` if `len(dc) < 8` or MLE fails. Measurement \(y_t=\mu+x_t+v_t\), state \(x_{t+1}=\rho x_t+w_t\), \(x_{0|-1}=0\).

- [ ] **Step 1: Write the failing tests**

Append to `tests/test_expected_growth.py`:

```python
from lrrcs.calibration.expected_growth import filter_expected_growth


def test_filter_expected_growth_too_short():
    with pytest.raises(ValueError):
        filter_expected_growth(np.ones(7))


def test_filter_expected_growth_recovers_persistent_state():
    rng = np.random.default_rng(0)
    n = 200
    rho_true = 0.6
    mu = 0.02
    q = 0.001
    r = 0.002
    x = np.zeros(n)
    for t in range(n - 1):
        x[t + 1] = rho_true * x[t] + rng.normal(0.0, np.sqrt(q))
    y = mu + x + rng.normal(0.0, np.sqrt(r), size=n)
    out = filter_expected_growth(y)
    assert set(out) == {"x", "mu", "rho", "q", "r", "loglik"}
    assert isinstance(out["x"], np.ndarray)
    assert out["x"].shape == (n,)
    assert 0.3 < out["rho"] < 0.9
    assert float(np.std(out["x"])) < float(np.std(y))
    assert np.isfinite(out["loglik"])
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_expected_growth.py::test_filter_expected_growth_too_short tests/test_expected_growth.py::test_filter_expected_growth_recovers_persistent_state -v`

Expected: FAIL with `ImportError` or `filter_expected_growth` is not defined.

- [ ] **Step 3: Implement the Kalman filter**

Add these functions to `src/lrrcs/calibration/expected_growth.py` (keep `expected_growth_proxy` as in Task 1). Add `from scipy.optimize import minimize` at the top.

```python
def _kalman_filter(
    y: np.ndarray, mu: float, rho: float, q: float, r: float
) -> tuple[float, np.ndarray]:
    """Filtered means E[x_t | y_{1:t}] and Gaussian log-likelihood."""
    n = y.size
    x_filt = np.empty(n)
    x_pred = 0.0
    p_pred = q / max(1.0 - rho * rho, 1e-8)
    loglik = 0.0
    two_pi = 2.0 * np.pi
    for t in range(n):
        innov = y[t] - mu - x_pred
        s = p_pred + r
        if not np.isfinite(s) or s <= 1e-18:
            return -np.inf, x_filt
        k = p_pred / s
        x_upd = x_pred + k * innov
        p_upd = (1.0 - k) * p_pred
        loglik += -0.5 * (np.log(two_pi * s) + innov * innov / s)
        x_filt[t] = x_upd
        x_pred = rho * x_upd
        p_pred = rho * rho * p_upd + q
    return float(loglik), x_filt


def filter_expected_growth(dc: ArrayLike) -> dict:
    """Univariate Kalman / AR(1) filter for expected consumption growth.

    State space (sample frequency, typically annual)::

        y_t = mu + x_t + v_t
        x_{t+1} = rho * x_t + w_t

    ``rho`` is *not* the monthly Table II value 0.98. Starting values are
    AC1(y) and half the sample variance. MLE uses ``scipy.optimize.minimize``.

    Examples
    --------
    ```python
    import lrrcs as lrr
    out = lrr.filter_expected_growth(dc)
    ```
    """
    y = np.asarray(dc, dtype=float).ravel()
    if y.size < 8:
        raise ValueError("Series too short for Kalman filter")
    mu = float(np.mean(y))
    var = float(np.var(y))
    if var < 1e-18:
        raise ValueError("Consumption growth has no variation")
    rho0 = float(np.corrcoef(y[:-1], y[1:])[0, 1])
    if not np.isfinite(rho0):
        rho0 = 0.5
    rho0 = float(np.clip(rho0, 1e-6, 0.999))
    q0 = r0 = max(var / 2.0, 1e-12)

    def nll(theta: np.ndarray) -> float:
        rho, q, r = float(theta[0]), float(theta[1]), float(theta[2])
        ll, _ = _kalman_filter(y, mu, rho, q, r)
        if not np.isfinite(ll):
            return 1e20
        return -ll

    res = minimize(
        nll,
        x0=np.array([rho0, q0, r0], dtype=float),
        method="L-BFGS-B",
        bounds=[(1e-6, 0.999), (1e-12, None), (1e-12, None)],
    )
    if not res.success:
        raise ValueError(f"Kalman MLE did not converge: {res.message}")
    rho, q, r = (float(res.x[0]), float(res.x[1]), float(res.x[2]))
    loglik, x_filt = _kalman_filter(y, mu, rho, q, r)
    if not np.isfinite(loglik):
        raise ValueError("Kalman MLE did not converge: non-finite likelihood")
    return {
        "x": x_filt,
        "mu": mu,
        "rho": rho,
        "q": q,
        "r": r,
        "loglik": loglik,
    }
```

Add to `src/lrrcs/calibration/__init__.py`:

- import: `from .expected_growth import expected_growth_proxy, filter_expected_growth`
- `__all__` entry: `"filter_expected_growth"` after `"expected_growth_proxy"`

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_expected_growth.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_expected_growth.py src/lrrcs/calibration/expected_growth.py src/lrrcs/calibration/__init__.py
git commit -m "feat: add filter_expected_growth Kalman AR(1) for annual x_t"
```

---

### Task 3: Root API and `[data]` extras

**Files:**
- Modify: `tests/test_api_layout.py`
- Modify: `pyproject.toml`
- Modify: `docs/installation.md`
- Modify: `docs/api.md`
- Test: `tests/test_api_layout.py`

**Interfaces:**
- Consumes: Task 1–2 names on `lrrcs.calibration`
- Produces: `lrr.expected_growth_proxy` and `lrr.filter_expected_growth` in `__all__`; `[data]` extras `matplotlib`, `pyarrow`, `polars`, `plotnine`

- [ ] **Step 1: Write the failing tests**

In `tests/test_api_layout.py`, add `"expected_growth_proxy"` and `"filter_expected_growth"` to the tuple in `test_root_api_has_companion_names`.

In `test_pyproject_companion_metadata`, after the existing asserts, add:

```python
    data_extra = "\n".join(extras["data"])
    assert "matplotlib" in data_extra
    assert "pyarrow" in data_extra
    assert "polars" in data_extra
    assert "plotnine" in data_extra
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_api_layout.py::test_root_api_has_companion_names tests/test_api_layout.py::test_pyproject_companion_metadata -v`

Expected: FAIL — `polars`/`plotnine` missing from `[data]`, and/or root names missing if auto-discovery did not pick up `__init__.py` exports (they should exist after Task 2; if names already pass, extras still fail).

- [ ] **Step 3: Update extras and docs**

In `pyproject.toml` set:

```toml
data = ["matplotlib", "pyarrow", "polars", "plotnine"]
```

In `docs/installation.md` replace the sentence `` `[fast]` is Numba. `[data]` is matplotlib and pyarrow. `` with:

```markdown
`[fast]` is Numba. `[data]` is matplotlib, pyarrow, polars, and plotnine.
```

In `docs/api.md` replace the root-function table with:

```markdown
| Object | Call |
|:---|:---|
| Book-to-market panel, 1930–2003 | `lrr.build_annual_panel` |
| Table I / Table VI | `lrr.table_i`, `lrr.table_vi_data` |
| IMRS, dynamics, solver | `lrr.get_table_ii_params`, `lrr.ModelSolver`, `lrr.solve_analytical` |
| Expected growth \(x_t\) | `lrr.expected_growth_proxy`, `lrr.filter_expected_growth` |
| Cash-flow loadings | `lrr.calibrate_from_data` |
| Prices and returns | `lrr.compute_asset_pricing_moments` |
```

Do not add plotnine figure helpers. Keep `import tidyfinance as tf` and `import lrrcs as lrr` on this page.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_api_layout.py tests/test_docs.py::test_package_pages_are_tidyfinance_companion -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_api_layout.py pyproject.toml docs/installation.md docs/api.md
git commit -m "feat: export x_t helpers at lrr. and add polars/plotnine to [data]"
```

---

### Task 4: Nav scaffold and docs tests (structure)

**Files:**
- Modify: `tests/test_docs.py`
- Create: `docs/financial-data.md` (stub with front matter + H1 only)
- Modify: `docs/cash-flows-then-prices.md` (front matter `nav_order: 4` plus one retrieval pointer)
- Modify: `docs/time-series.md` (front matter `nav_order: 5` only)
- Modify: `docs/cross-section.md` (front matter `nav_order: 6` only)
- Modify: `docs/package.md` (`nav_order: 7` and list Financial data)
- Modify: `docs/index.md` (link Financial data)
- Modify: `docs/getting-started.md` (Next → Financial data)
- Modify: `README.md` (docs table row)
- Test: `tests/test_docs.py`

**Interfaces:**
- Consumes: current book tests
- Produces: Financial data page exists; nav_order table from the spec; Home / Getting started / Package / README contain `financial-data`. Does **not** yet require The market’s five H2s or plotnine (Tasks 5–6).

- [ ] **Step 1: Write the failing tests**

In `tests/test_docs.py`:

1. Add `"financial-data.md"` to `BOOK_PAGES` (after `"getting-started.md"`).
2. Replace `test_new_chapter_front_matter` with:

```python
def test_new_chapter_front_matter():
    gs = _text("getting-started.md")
    assert "title: Getting started" in gs
    assert "# Getting started" in gs
    assert _parent("getting-started.md") is None
    assert _front_nav_order("getting-started.md") == 2

    fd = _text("financial-data.md")
    assert "title: Financial data" in fd
    assert "# Financial data" in fd
    assert _parent("financial-data.md") is None
    assert _front_nav_order("financial-data.md") == 3

    cf = _text("cash-flows-then-prices.md")
    assert "title: Cash flows, then prices" in cf
    assert "# Cash flows, then prices" in cf
    assert _parent("cash-flows-then-prices.md") is None
    assert _front_nav_order("cash-flows-then-prices.md") == 4

    assert _parent("time-series.md") is None
    assert _front_nav_order("time-series.md") == 5
    assert _parent("cross-section.md") is None
    assert _front_nav_order("cross-section.md") == 6
    assert _front_nav_order("package.md") == 7
    assert _parent("installation.md") == "Package"
    assert _parent("api.md") == "Package"
```

3. In `test_home_is_landing`, add `assert "financial-data" in text` (keep the cash-flows / time-series / cross-section asserts).
4. In `test_getting_started`, replace `assert "cash-flows-then-prices" in text` with `assert "financial-data" in text`. Keep `set_wrds_credentials` not in text.
5. In `test_value_versus_growth_chapter`, change `_front_nav_order("cross-section.md") == 5` to `== 6`.
6. In `test_market_chapter`, change `_front_nav_order("time-series.md") == 4` to `== 5`. Leave the four-H2 `H2S` asserts for now (the file still has them until Task 6).
7. In `test_package_page_points_at_the_book`, add `assert "financial-data" in text`.
8. In `test_readme_matches_landing`, add `assert "financial-data" in text`.

Do **not** yet add `test_financial_data_chapter` or change The market’s H2 tuple.

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_docs.py -v`

Expected: FAIL — `financial-data.md` missing and/or nav_order mismatches.

- [ ] **Step 3: Scaffold nav**

Create `docs/financial-data.md`:

```markdown
---
title: Financial data
nav_order: 3
---

# Financial data
```

Change `nav_order` only:

- `docs/cash-flows-then-prices.md`: `nav_order: 4`
- `docs/time-series.md`: `nav_order: 5`
- `docs/cross-section.md`: `nav_order: 6`
- `docs/package.md`: `nav_order: 7`

In `docs/cash-flows-then-prices.md`, in the **Data.** paragraph, after the first sentence, add:

```markdown
How to retrieve those series is [Financial data]({{ '/financial-data.html' | relative_url }}).
```

In `docs/index.md`, replace the paragraph that starts `That loop is` with:

```markdown
Series are on [Financial data]({{ '/financial-data.html' | relative_url }}). The loop is [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}). Then we run it twice: [The market]({{ '/time-series.html' | relative_url }}) and [Value versus growth]({{ '/cross-section.html' | relative_url }}).
```

In `docs/getting-started.md`, replace the last line with:

```markdown
Next: [Financial data]({{ '/financial-data.html' | relative_url }}).
```

In `docs/package.md`, replace the “Start with the book” sentence with:

```markdown
Start with the book: [Getting started]({{ '/getting-started.html' | relative_url }}), [Financial data]({{ '/financial-data.html' | relative_url }}), [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}), [The market]({{ '/time-series.html' | relative_url }}), [Value versus growth]({{ '/cross-section.html' | relative_url }}).
```

In `README.md`, insert this row after Getting started:

```markdown
| [Financial data](https://tlorans.github.io/kiku-value-premium-replication/financial-data.html) | Consumption, Campbell–Shiller dividends, the annual panel |
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_docs.py -v`

Expected: PASS. The market still has the old four H2s (Task 6 rewrites them). Financial data is a stub (Task 5 fills it).

- [ ] **Step 5: Commit**

```bash
git add tests/test_docs.py docs/financial-data.md docs/cash-flows-then-prices.md docs/time-series.md docs/cross-section.md docs/package.md docs/index.md docs/getting-started.md README.md
git commit -m "docs: insert Financial data in the book nav"
```

---

### Task 5: Financial data chapter

**Files:**
- Modify: `tests/test_docs.py`
- Modify: `docs/financial-data.md` (full page)
- Test: `tests/test_docs.py`

**Interfaces:**
- Consumes: Task 4 stub and nav
- Produces: follow-along Financial data page with polars/plotnine then `lrr.` calls; three CSV paths; two Tidy Finance URLs

- [ ] **Step 1: Write the failing tests**

Add to `tests/test_docs.py`:

```python
def test_financial_data_chapter():
    text = _text("financial-data.md")
    assert "title: Financial data" in text
    assert "# Financial data" in text
    assert _parent("financial-data.md") is None
    assert _front_nav_order("financial-data.md") == 3
    assert "accessing-and-managing-financial-data" in text
    assert "wrds-crsp-and-compustat" in text
    assert "data/consumption_annual.csv" in text
    assert "data/annual_panel.csv" in text
    assert "data/rf_annual.csv" in text
    assert "import polars as pl" in text
    assert "import plotnine as p9" in text
    assert "import tidyfinance as tf" in text
    assert "import lrrcs as lrr" in text
    assert "load_consumption" in text
    assert "campbell_shiller_annual" in text
    assert "build_annual_panel" in text
    assert "from lrrcs.model import" not in text
    assert "kiku_value_premium" not in text
    assert "time-series" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_docs.py::test_financial_data_chapter -v`

Expected: FAIL — stub lacks imports and URLs.

- [ ] **Step 3: Write the chapter**

Replace `docs/financial-data.md` with this file:

```markdown
---
title: Financial data
nav_order: 3
---

# Financial data
{: .no_toc }

1. TOC
{:toc}

The later chapters need three annual series, 1930–2003: consumption growth, a claims panel (returns, dividend growth, price–dividend), and a real T-bill. This page shows how to retrieve them. It is not a WRDS tutorial.

Tidy Finance already covers Fama–French files, q-factors, and how to store downloads in [Accessing and managing financial data](https://www.tidy-finance.org/chapters/accessing-and-managing-financial-data.html), and credentials plus CRSP / Compustat / CCM in [WRDS, CRSP, and Compustat](https://www.tidy-finance.org/chapters/wrds-crsp-and-compustat.html). Set credentials with `tf.set_wrds_credentials()`; see [Installation]({{ '/installation.html' | relative_url }}).

What is new here is NIPA consumption, the PCE deflator, Campbell–Shiller dividends from `ret` versus `retx`, the real T-bill, and the annual claims panel. Live FRED or WRDS would not be the replica sample. After each retrieval sketch we read the files in `data/`.

```python
import polars as pl
import plotnine as p9
import tidyfinance as tf
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
panel = pl.read_csv("data/annual_panel.csv")
rf = pl.read_csv("data/rf_annual.csv")
```

`panel` columns are `year`, `claim` (`Growth`, `Value`, `Market`), `ret`, `dgrowth`, `pd`.

## Consumption

Long-run risk lives in consumption, not in average returns. The series is log growth of real per-capita nondurables plus services (NIPA, via FRED).

```python
import polars as pl
import numpy as np

nd = pl.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DNDGRA3A086NBEA")
sv = pl.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DSERRA3A086NBEA")
pop = pl.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=B230RC0A052NBEA")
# DATE plus one value column on each file. Align on year, then:
# level = (ND + SV) / pop
# dc = log(level).diff()
```

You do not need to run that download. The package does it:

```python
import lrrcs as lrr

dc_live = lrr.load_consumption()
```

`dc_live` continues past 2003. This book uses 1930–2003:

```python
import polars as pl
import plotnine as p9

dc = pl.read_csv("data/consumption_annual.csv")
(
    p9.ggplot(dc.to_pandas(), p9.aes("year", "dc"))
    + p9.geom_line()
    + p9.labs(x="Year", y="Δc", title="Real per-capita ND+S growth, 1930–2003")
)
```

The PCE deflator (`DPCERD3A086NBEA`) turns nominal CRSP dividends into reals. `lrr.load_deflator()` is the wrapper. The shipped panel is already deflated.

## CRSP, then Campbell–Shiller dividends

One `tf.download_data` call is enough to see the companion pattern. Filters, delisting, and CCM are in the Tidy Finance WRDS chapter.

```python
import tidyfinance as tf
import lrrcs as lrr

tf.set_wrds_credentials()
crsp = tf.download_data(
    domain="WRDS",
    dataset="crsp_monthly",
    start_date="1925-12-01",
    end_date="2003-12-31",
    version="v1",
    additional_columns=["retx"],
)
```

Tidy Finance gives you returns. It does not build dividends. Campbell and Shiller infer them from the gap between the return with dividends (`ret`) and the capital-gain return (`retx`):

$$
D_t = (r_t - r_t^{x})\, V_{t-1}.
$$

```python
# toy month: r = 0.02, r^x = 0.01, V = 100 → D = 1
d = (0.02 - 0.01) * 100
```

Then `lrr.campbell_shiller_annual(ret, retx, deflator)` compounds to annual real dividend growth and year-end \(P/D\). You do not need WRDS to finish this page: the Market rows of `data/annual_panel.csv` already store `dgrowth` and `pd`.

```python
import polars as pl
import plotnine as p9

dc = pl.read_csv("data/consumption_annual.csv")
panel = pl.read_csv("data/annual_panel.csv")
mkt = panel.filter(pl.col("claim") == "Market").join(dc, on="year")

(
    p9.ggplot(mkt.to_pandas(), p9.aes("dc", "dgrowth"))
    + p9.geom_point()
    + p9.labs(x="Δc", y="Market Δd", title="Cash flows, not returns")
)

(
    p9.ggplot(
        mkt.with_columns(pl.col("pd").log().alias("log_pd")).to_pandas(),
        p9.aes("year", "log_pd"),
    )
    + p9.geom_line()
    + p9.labs(x="Year", y="log(P/D)", title="Market price–dividend, 1930–2003")
)
```

The second chart is the price moment the Euler equation has to match later. There is no \(x_t\) on this page.

## Real T-bill and the annual panel

The real safe rate comes from CRSP index files (`mcti`: T-bill and CPI), not from Ken French’s risk-free column. The shipped file is `data/rf_annual.csv`.

The claims panel puts June book-to-market quintiles (NYSE breaks — Tidy Finance’s `assign_portfolio`) together with Campbell–Shiller dividends. Historical Davis–Fama–French book equity fills the early Compustat gap inside `lrr.build_annual_panel`. Optional rebuild:

```python
import lrrcs as lrr

bm = lrr.build_annual_panel(refresh=False)
print(lrr.table_i(bm))
```

`refresh=True` hits WRDS again. The rest of this book reads `data/annual_panel.csv`, `data/consumption_annual.csv`, and `data/rf_annual.csv`.

Next: [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}) for the recipe, or skip to [The market]({{ '/time-series.html' | relative_url }}).
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_docs.py -v`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tests/test_docs.py docs/financial-data.md
git commit -m "docs: write follow-along Financial data chapter"
```

---

### Task 6: Rewrite The market

**Files:**
- Modify: `tests/test_docs.py`
- Modify: `docs/time-series.md` (full rewrite; title/URL unchanged)
- Test: `tests/test_docs.py`

**Interfaces:**
- Consumes: `lrr.expected_growth_proxy`, `lrr.filter_expected_growth` (Tasks 1–2); shipped CSVs; `lrr.Dynamics`, `lrr.solve_analytical`
- Produces: The market as a five-H2 follow-along chapter. No `## Data`. Path plot is chapter code, not a new public function.

- [ ] **Step 1: Write the failing tests**

In `tests/test_docs.py`, replace `H2S` and `test_market_chapter` with:

```python
MARKET_H2S = (
    "## What long-run risk is",
    "## Estimate x_t",
    "## Calibrate dividends",
    "## Simulate cash flows",
    "## Solve and check returns and prices",
)


def test_market_chapter():
    text = _text("time-series.md")
    assert "title: The market" in text
    assert "# The market" in text
    assert _parent("time-series.md") is None
    assert _front_nav_order("time-series.md") == 5
    positions = [text.index(h) for h in MARKET_H2S]
    assert positions == sorted(positions)
    assert "## Data" not in text
    assert "8.56" in text and "7.53" in text
    assert "expected_growth_proxy" in text
    assert "filter_expected_growth" in text
    assert "simulate_cashflow_moments" in text
    assert "compute_asset_pricing_moments" in text
    assert "import polars as pl" in text
    assert "import plotnine as p9" in text
    assert "import lrrcs as lrr" in text
    assert "```python" in text
    assert "from lrrcs.model import" not in text
    assert "kiku_value_premium" not in text
    assert "Melin" not in text
    assert "other-risk-premia" not in text
    assert "cross-section" in text
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_docs.py::test_market_chapter -v`

Expected: FAIL — old four H2s, no `expected_growth_proxy` / plotnine.

- [ ] **Step 3: Rewrite the chapter**

Replace `docs/time-series.md` with this file:

```markdown
---
title: The market
nav_order: 5
---

# The market
{: .no_toc }

1. TOC
{:toc}

**Question.** Can this household price the *market* — the value-weighted claim on all listed stocks — year after year?

That is the test Bansal and Yaron (2004) wrote the model for. One claim. Not a ranking of firms. Consumption and market dividends come from [Financial data]({{ '/financial-data.html' | relative_url }}). The recipe is [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}).

```python
import polars as pl
import plotnine as p9
import tidyfinance as tf
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
panel = pl.read_csv("data/annual_panel.csv")
rf = pl.read_csv("data/rf_annual.csv")
mkt = panel.filter(pl.col("claim") == "Market").join(dc, on="year")
```

## What long-run risk is

Consumption growth is not white noise. It has a small persistent expected-growth piece $$x_t$$:

$$
\Delta c_{t+1}=\mu+x_t+\sigma_t\eta_{t+1},\qquad x_{t+1}=\rho x_t+\varphi_x\sigma_t e_{t+1}.
$$

News about $$x_t$$ is long-run risk. Epstein–Zin with $$\psi\neq 1/\gamma$$ prices that news. A claim’s loading $$\phi$$ on $$x_t$$ is how much of it the claim inherits.

The annual picture is a two-year moving average of lagged $$\Delta c$$. Raw growth is jagged. The MA is the slow component.

```python
import polars as pl
import plotnine as p9

dc = pl.read_csv("data/consumption_annual.csv").sort("year")
plot_df = dc.with_columns(
    pl.col("dc").shift(1).rolling_mean(window_size=2).alias("ma")
)
(
    p9.ggplot(plot_df.to_pandas(), p9.aes("year"))
    + p9.geom_line(p9.aes(y="dc"))
    + p9.geom_line(p9.aes(y="ma"), color="steelblue")
    + p9.labs(x="Year", y="Δc", title="Consumption growth and a two-year MA of lags")
)
```

The blue line is the annual stand-in for $$x_t$$. Table II’s monthly $$\rho=0.98$$ is the same object on a finer clock.

## Estimate x_t

**Proxy (the estimator we keep).** Same MA, then the package:

```python
import polars as pl
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
x_ma = lrr.expected_growth_proxy(dc["dc"], window=2)
```

`x_ma[t]` is the mean of `dc[t-2:t]`, `nan` on the first two years.

**Filter (the link to the solver).** A univariate Kalman / AR(1) on annual $$\Delta c$$:

$$
y_t=\mu+x_t+v_t,\qquad x_{t+1}=\rho x_t+w_t.
$$

```python
import numpy as np
import polars as pl
import plotnine as p9
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
y = dc["dc"].to_numpy()
mu = float(y.mean())
rho0 = float(np.corrcoef(y[:-1], y[1:])[0, 1])
# ... Kalman MLE for rho, q, r, then the filtered path ...

out = lrr.filter_expected_growth(dc["dc"])
out["rho"]   # annual persistence, not monthly 0.98
plot_df = dc.with_columns(
    pl.Series("ma", lrr.expected_growth_proxy(dc["dc"], window=2)),
    pl.Series("x_filt", out["x"]),
)
(
    p9.ggplot(plot_df.to_pandas(), p9.aes("year"))
    + p9.geom_line(p9.aes(y="dc"))
    + p9.geom_line(p9.aes(y="ma"), color="steelblue")
    + p9.geom_line(p9.aes(y="x_filt"), color="darkorange")
    + p9.labs(x="Year", y="Δc", title="MA proxy and filtered x̂_t")
)
```

Do not take $$\phi$$ or Table II numbers from this filter. Calibration below uses the MA.

## Calibrate dividends

Kiku (2006) equation (19): $$\Delta d_t=d_0+\tilde\phi\,\mathrm{MA}(\Delta c,2)+\varepsilon_t$$.

```python
import numpy as np
import polars as pl
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
mkt = pl.read_csv("data/annual_panel.csv").filter(pl.col("claim") == "Market")
joined = mkt.join(dc, on="year").drop_nulls()
x = lrr.expected_growth_proxy(joined["dc"], window=2)
y = joined["dgrowth"].to_numpy()
mask = np.isfinite(x)
phi_tilde = float(np.cov(y[mask], x[mask], ddof=0)[0, 1] / np.var(x[mask], ddof=0))
```

Then the same slope from the package, and the rest of the dividend process:

```python
import polars as pl
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
mkt = pl.read_csv("data/annual_panel.csv").filter(pl.col("claim") == "Market")
joined = mkt.join(dc, on="year").drop_nulls()
phi_tilde = lrr.estimate_long_run_leverage(joined["dc"], joined["dgrowth"], window=2)
div = lrr.calibrate_from_data(
    joined["dc"].to_numpy(),
    market=joined["dgrowth"].to_numpy(),
    frequency="annual",
    window=2,
)
div["market"].mu, div["market"].phi, div["market"].phi_sigma, div["market"].alpha
```

Printed $$\tilde\phi$$ on the market is about $$0.66$$. That number is a *ranking check*. The solver wants monthly $$\phi$$. Table II locks market $$\mu=0.0012$$, $$\phi=2.8$$, $$\varphi_\sigma=7.5$$, $$\alpha=0.55$$. Simulation and pricing below use `lrr.get_table_ii_params()`, not the annual slope as a monthly loading. Average returns never enter.

## Simulate cash flows

The recursion is the same one as above, now monthly, with Table II numbers:

$$
\Delta c_{t+1}=\mu_c+x_t+\sigma_t\eta_{t+1},\qquad
\Delta d_{t+1}=\mu_d+\phi x_t+\varphi_\sigma\sigma_t u_{t+1}.
$$

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
params.dividends["market"].phi  # 2.8
params.cons.rho                 # 0.98
print(lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=params))
```

Prose target (1000 samples of 74 years): consumption mean growth 1.86 percent against 1.96 in the data; volatility 2.16 against 2.20; first autocorrelation 0.43 against 0.44. Market dividend moments print on the same object. If those fail, stop. The premium that comes next would then be a free parameter in disguise.

## Solve and check returns and prices

The IMRS and Euler equation are on [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}). Table II is the default household.

```python
import lrrcs as lrr

params = lrr.get_table_ii_params()
lrr.print_long_short_premium(lrr.solve_analytical(params))
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
lrr.print_asset_pricing_moments(lrr.compute_asset_pricing_moments(solver))
```

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

E[R] is the average simple return, percent per year. E[pd] is average $$\log(P/D)$$. Market return volatility is 20.1 percent in both. Success is **both** columns close. A match on returns with a wrong price–dividend ratio is a fail. The safe rate is about seventy basis points too high. The equity premium is a little short of the sample. Close enough to ask a second question.

One simulated path, so you see the series, not only the table. Log $$P/D$$ uses the analytical map $$z=\bar z+A_1 x+A_2(\sigma^2-\bar\sigma^2)$$. That is chapter code, not a new helper.

```python
import numpy as np
import polars as pl
import plotnine as p9
import lrrcs as lrr

params = lrr.get_table_ii_params()
path = lrr.Dynamics(params, seed=1).simulate_cashflows(T=74 * 12)
sol = lrr.solve_analytical(params)
x = path["x"]
s2 = path["sigma2"]
z = (
    sol.mean_log_pd["market"]
    + sol.A1["market"] * x
    + sol.A2["market"] * (s2 - params.cons.sigma**2)
)
sim = pl.DataFrame({"t": np.arange(len(x)), "x": x, "dd": path["dd_market"], "log_pd": z})
pdf = sim.to_pandas()
(
    p9.ggplot(pdf, p9.aes("t", "x"))
    + p9.geom_line()
    + p9.labs(x="Month", y="x_t", title="Simulated long-run risk")
)
(
    p9.ggplot(pdf, p9.aes("t", "dd"))
    + p9.geom_line()
    + p9.labs(x="Month", y="Δd", title="Simulated market dividend growth")
)
(
    p9.ggplot(pdf, p9.aes("t", "log_pd"))
    + p9.geom_line()
    + p9.labs(x="Month", y="log(P/D)", title="Model price–dividend along the path")
)
```

Value and growth are [Value versus growth]({{ '/cross-section.html' | relative_url }}). Matching the market does not rank firms.
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_docs.py tests/test_expected_growth.py tests/test_api_layout.py tests/test_calibration.py -v`

Expected: PASS. `test_code_fences_use_flat_lrr` must still pass (no `from lrrcs.model import`).

- [ ] **Step 5: Commit**

```bash
git add tests/test_docs.py docs/time-series.md
git commit -m "docs: rewrite The market as a follow-along x_t chapter"
```

---

## Self-review (spec coverage)

| Spec requirement | Task |
|---|---|
| `expected_growth_proxy` + leverage refactor | 1 |
| `filter_expected_growth` Kalman dict | 2 |
| Root export, `[data]` polars/plotnine, installation + API map | 3 |
| Nav 3–7, Home/Getting started/Package/README links, cash-flows pointer | 4 |
| Financial data page, Tidy Finance URLs, three CSVs, three charts, no WRDS required | 5 |
| The market five H2s, MA then Kalman, dividend calibration, cash-flow MC, Euler return **and** price moments, path plot, 8.56/7.53 | 6 |
| Value versus growth body unchanged; four H2s; nav_order 6 | 4 (nav only) |
| No plotnine helpers, no `simulate_asset_pricing_moments`, no solver/Table II edits | Global / file map |

No placeholders. Signatures are `expected_growth_proxy(dc, window=2) -> np.ndarray` and `filter_expected_growth(dc) -> dict` with keys `x`, `mu`, `rho`, `q`, `r`, `loglik` in every task that mentions them.
