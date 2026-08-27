# lrrcs as a tidyfinance companion Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship `lrrcs` 0.5.0 as a tidyfinance companion: required dependency, flat `import lrrcs as lrr` API, empirical plumbing through tidyfinance, paper site kept and restyled as `tf` + `lrr`.

**Architecture:** `src/lrrcs/` becomes the only package (delete `kiku_value_premium`). Root `__init__.py` auto-discovers public functions/classes. Empirical code calls only public tidyfinance names; model/calibration/implications stay numpy. Data-bearing empirical functions honor `tf.get_backend()` via a local converter. Campbell–Shiller, historical book equity, consumption, and CRSP index files stay in `lrrcs`.

**Tech Stack:** Python ≥ 3.11, `tidyfinance>=0.5.0`, numpy, scipy, pandas, pytest, `uv`, Just the Docs.

**Spec:** `docs/superpowers/specs/2026-08-27-tidyfinance-companion-design.md`

## Global Constraints

- Version `0.5.0`; `requires-python = ">=3.11"`
- Required: `tidyfinance>=0.5.0`, `numpy>=1.26`, `scipy>=1.7`, `pandas>=2.2`
- `[fast]`: `numba>=0.56`; `[data]`: `matplotlib`, `pyarrow` only (no `wrds`, no `python-dotenv`)
- Documented import: `import tidyfinance as tf` and `import lrrcs as lrr`
- Do not re-export tidyfinance symbols; do not import tidyfinance privates (`_use_backend`, `_download_*`)
- No `lrr.set_backend`; no `kiku_value_premium`; no `connect_wrds`; no `print_value_premium`
- Model / calibration / implications must not import tidyfinance
- Empirical internals stay pandas; public data-bearing functions honor `tf.get_backend()`
- Printed 1930–2003 bands remain the replica target (goldens rematch, paper numbers do not change)
- Default CI: `uv run pytest -m "not wrds"`
- Paper narrative stays on Just the Docs; no Great Docs, no hatchling, no Ruff-only pass

## File map

**Create**

- `src/lrrcs/_backend.py` — pandas/polars conversion; `use_backend` wrapper
- `docs/superpowers/plans/` (this file)

**Become the real package (move, then edit)**

- `src/lrrcs/__init__.py` — auto-discovery + backend wrap list
- `src/lrrcs/model/` — current `src/kiku_value_premium/model/`
- `src/lrrcs/calibration/` — current `src/kiku_value_premium/calibration/`
- `src/lrrcs/implications/` — current `src/kiku_value_premium/implications/`
- `src/lrrcs/empirical/` — current `src/kiku_value_premium/empirical/`
  - `wrds.py` — tidyfinance adapter (`EmpiricalDataError` + private download helpers)
  - `panel.py` — `build_annual_panel` using those helpers
  - `construction.py` — `form_bm_quintiles` via `tf.assign_portfolio`
  - `tables.py` — default `start=1930`, `end=2003`
  - `figures.py` — `figure2(..., start=1952)`

**Modify**

- `pyproject.toml` — version, python, deps, extras
- `tests/test_api_layout.py` and every `tests/test_*.py` that imports `kiku_value_premium`
- `tests/test_docs.py` — companion import language
- `examples/*.py`
- `README.md`, `docs/installation.md`, `docs/api.md`, `docs/package.md`, `docs/index.md`
- Replica pages: `docs/empirical.md`, `docs/model.md`, `docs/calibration.md`, `docs/implications.md`, `docs/time-series.md`, `docs/cross-section.md`, `docs/further.md`, `docs/climate.md`, `docs/other-risk-premia.md`, `docs/generalization.md`

**Delete**

- `src/kiku_value_premium/` (entire tree)

---

### Task 1: 0.5.0 metadata and tidyfinance dependency

**Files:**
- Modify: `pyproject.toml`
- Modify: `src/kiku_value_premium/__init__.py` (`__version__` only; package move is Task 2)
- Modify: `src/lrrcs/__init__.py` (re-export still works; version comes from kiku until Task 2)
- Test: `tests/test_api_layout.py`

**Interfaces:**
- Consumes: current 0.4.0 package
- Produces: installable 0.5.0 env with `import tidyfinance` working; `lrrcs.__version__ == "0.5.0"`

- [ ] **Step 1: Write the failing tests**

In `tests/test_api_layout.py` replace `test_version_is_0_4_0` and add a dependency test:

```python
from pathlib import Path
import lrrcs as lrr


def test_version_is_0_5_0():
    assert lrr.__version__ == "0.5.0"


def test_tidyfinance_is_a_runtime_dependency():
    import tidyfinance as tf
    assert callable(tf.download_data)
    assert callable(tf.set_wrds_credentials)
    assert callable(tf.get_backend)


def test_pyproject_companion_metadata():
    import tomllib
    data = tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))
    project = data["project"]
    deps = "\n".join(project["dependencies"])
    extras = project["optional-dependencies"]
    extra_blob = "\n".join(x for group in extras.values() for x in group)
    assert project["name"] == "lrrcs"
    assert project["version"] == "0.5.0"
    assert project["requires-python"] == ">=3.11"
    assert "tidyfinance>=0.5.0" in deps
    assert "numpy>=1.26" in deps
    assert "pandas>=2.2" in deps
    assert "wrds" not in deps and "wrds" not in extra_blob
    assert "python-dotenv" not in deps and "python-dotenv" not in extra_blob
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_api_layout.py::test_version_is_0_5_0 tests/test_api_layout.py::test_tidyfinance_is_a_runtime_dependency tests/test_api_layout.py::test_pyproject_companion_metadata -v`

Expected: FAIL (`0.4.0`, `ModuleNotFoundError: tidyfinance`, and/or missing pyproject pins).

- [ ] **Step 3: Update pyproject and version**

`pyproject.toml` `[project]` block must be:

```toml
[project]
name = "lrrcs"
version = "0.5.0"
description = "Long-run risks in the time series and the cross section."
readme = "README.md"
requires-python = ">=3.11"
license = {text = "MIT"}
authors = [
    {name = "Replication Team (Grok, Lucas, Harper, Benjamin)"}
]
dependencies = [
    "numpy>=1.26",
    "scipy>=1.7",
    "pandas>=2.2",
    "tidyfinance>=0.5.0",
]

[project.optional-dependencies]
fast = ["numba>=0.56"]
data = ["matplotlib", "pyarrow"]
dev = ["pytest", "matplotlib", "numba>=0.56"]
```

Keep existing `[build-system]`, `[tool.pytest.ini_options]`, and `[tool.setuptools.packages.find]`.

Set `__version__ = "0.5.0"` in `src/kiku_value_premium/__init__.py`.

Then install:

```bash
uv add "tidyfinance>=0.5.0"
uv add "numpy>=1.26" "pandas>=2.2"
uv pip install -e ".[dev]"
```

If `uv add` rewrites `pyproject.toml` dependency formatting, re-read it and keep the version floors above. Do not reintroduce `wrds` or `python-dotenv`.

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_api_layout.py::test_version_is_0_5_0 tests/test_api_layout.py::test_tidyfinance_is_a_runtime_dependency tests/test_api_layout.py::test_pyproject_companion_metadata -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add pyproject.toml uv.lock src/kiku_value_premium/__init__.py tests/test_api_layout.py
git commit -m "feat: require tidyfinance and bump lrrcs to 0.5.0"
```

---

### Task 2: Make `src/lrrcs/` the only package

**Files:**
- Create (via `git mv`): every `.py` under `src/kiku_value_premium/{model,calibration,implications,empirical}/` into the matching `src/lrrcs/` subpackage
- Modify: `src/lrrcs/__init__.py` — copy the current `kiku_value_premium` `__init__` (explicit exports, version 0.5.0)
- Modify: every test and example that imports `kiku_value_premium`
- Delete: `src/kiku_value_premium/`
- Test: `tests/test_api_layout.py` plus the full non-WRDS suite

**Interfaces:**
- Consumes: Task 1 version/deps
- Produces: `import lrrcs` loads real modules from `src/lrrcs/`; `import kiku_value_premium` raises `ModuleNotFoundError`; internal imports are `from lrrcs.model import ...`

- [ ] **Step 1: Write the failing gone-package test**

Replace `test_legacy_import_name` in `tests/test_api_layout.py` with:

```python
def test_kiku_value_premium_is_gone():
    import importlib
    import pytest
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("kiku_value_premium")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_api_layout.py::test_kiku_value_premium_is_gone -v`

Expected: FAIL (module still imports).

- [ ] **Step 3: Move the implementation**

From the repo root, overwrite the shim subpackages with the real modules. On PowerShell:

```powershell
$subs = @("model","calibration","implications","empirical")
foreach ($s in $subs) {
  Get-ChildItem "src/kiku_value_premium/$s" -File -Filter *.py | ForEach-Object {
    git mv -f $_.FullName "src/lrrcs/$s/$($_.Name)"
  }
}
git mv -f src/kiku_value_premium/__init__.py src/lrrcs/__init__.py
Remove-Item -Recurse -Force src/kiku_value_premium
```

If `git mv -f` refuses a target that is already tracked, `git rm` the shim `__init__.py` first, then `git mv` the real file.

Confirm `src/lrrcs/__init__.py` is the former kiku file (version 0.5.0, explicit `__all__`). Delete any leftover `from kiku_value_premium import *`.

Replace every `kiku_value_premium` import in `tests/` and `examples/`:

```text
kiku_value_premium  →  lrrcs
```

Files that need the substitution (all of them):

- `tests/test_api_layout.py`
- `tests/test_calibration.py`
- `tests/test_docs.py` (only if it mentions the old name)
- `tests/test_empirical_construction.py`
- `tests/test_empirical_goldens.py`
- `tests/test_empirical_macro.py`
- `tests/test_empirical_panel.py`
- `tests/test_empirical_wrds.py`
- `tests/test_implications.py`
- `tests/test_legs.py`
- `tests/test_model.py`
- `examples/demo.py`
- `examples/run_paper.py`
- `examples/calibration_example.py`
- `examples/calibrate_any_portfolio.py`
- `examples/calibrate_from_real_data.py`

In `examples/demo.py` and `examples/run_paper.py`, change `print_value_premium` to `print_long_short_premium` so examples still run after the move (the alias still exists until Task 3).

- [ ] **Step 4: Run the non-WRDS suite**

Run: `uv run pytest -m "not wrds" -q`

Expected: PASS, including `test_kiku_value_premium_is_gone`. If `src/kiku_value_premium.egg-info` confuses imports, delete that egg-info directory; do not commit it.

- [ ] **Step 5: Commit**

```bash
git add src/lrrcs src/kiku_value_premium tests examples
git commit -m "feat: move implementation into lrrcs and drop kiku_value_premium"
```

---

### Task 3: Flat auto-discovered public API

**Files:**
- Modify: `src/lrrcs/__init__.py` (replace explicit imports with auto-discovery)
- Modify: `src/lrrcs/model/analytical.py` — delete `print_value_premium = print_long_short_premium`
- Modify: `src/lrrcs/model/__init__.py` — drop `print_value_premium` from `__all__`
- Modify: `src/lrrcs/empirical/__init__.py` — stop exporting `START`/`END`/`FIGURE2_START`/`connect_wrds`
- Modify: `src/lrrcs/empirical/tables.py` — default `start=1930`, `end=2003` on `table_i`, `table_i_corr`, `table_vi_data`
- Modify: `src/lrrcs/empirical/figures.py` — `figure2(..., start: int = 1952)`
- Modify: `src/lrrcs/empirical/panel.py` — `build_annual_panel(refresh=False, start=1930, end=2003)`
- Test: `tests/test_api_layout.py`

**Interfaces:**
- Consumes: Task 2 real package
- Produces: `lrr.solve_analytical`, `lrr.build_annual_panel`, `lrr.EmpiricalDataError` at the root; constants and `print_value_premium`/`connect_wrds` absent from `dir(lrr)`

- [ ] **Step 1: Write the failing API-layout tests**

Replace `test_section_exports_exist` in `tests/test_api_layout.py` with root-level checks. Keep `test_old_flat_modules_are_gone` and `test_kiku_value_premium_is_gone`.

```python
import lrrcs as lrr


def test_root_api_has_companion_names():
    for name in (
        "solve_analytical",
        "get_table_ii_params",
        "print_long_short_premium",
        "ModelSolver",
        "calibrate_from_data",
        "compute_asset_pricing_moments",
        "build_annual_panel",
        "table_i",
        "table_vi_data",
        "figure1",
        "EmpiricalDataError",
    ):
        assert hasattr(lrr, name), name
        assert name in lrr.__all__


def test_root_api_dropped_names():
    for name in (
        "connect_wrds",
        "print_value_premium",
        "START",
        "END",
        "FIGURE2_START",
        "ROLE_ALIASES",
        "download_data",
        "set_wrds_credentials",
    ):
        assert name not in lrr.__all__
        assert name not in dir(lrr)


def test_table_helpers_default_to_1930_2003():
    import inspect
    sig = inspect.signature(lrr.table_i)
    assert sig.parameters["start"].default == 1930
    assert sig.parameters["end"].default == 2003
    sig = inspect.signature(lrr.build_annual_panel)
    assert sig.parameters["start"].default == 1930
    assert sig.parameters["end"].default == 2003
```

`test_root_api_dropped_names`: `download_data` / `set_wrds_credentials` must not be re-exported. `hasattr(lrr, "download_data")` must be false.

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_api_layout.py -v`

Expected: FAIL (`build_annual_panel` not on root, `START` still exported, `print_value_premium` still an alias, `table_i` still requires `start`).

- [ ] **Step 3: Implement auto-discovery and the clean break**

Replace `src/lrrcs/__init__.py` with:

```python
"""Long-run risks in the time series and the cross section.

Companion to tidyfinance. Documented import::

    import tidyfinance as tf
    import lrrcs as lrr
"""

from __future__ import annotations

import importlib
import pkgutil
import types

__version__ = "0.5.0"

_EXCLUDE = {"annotations"}
__all__: list[str] = []
_seen: set[str] = set()

if "__path__" in globals():
    for _finder, _module_name, _ispkg in pkgutil.iter_modules(__path__):
        if _module_name.startswith("_"):
            continue
        _module = importlib.import_module(f".{_module_name}", package=__name__)
        for _name in dir(_module):
            if _name.startswith("__") and _name.endswith("__"):
                continue
            if _name.startswith("_"):
                continue
            if _name in _EXCLUDE or _name in _seen:
                continue
            _obj = getattr(_module, _name)
            if not isinstance(_obj, (types.FunctionType, type)):
                continue
            if not getattr(_obj, "__module__", "").startswith(__name__):
                continue
            globals()[_name] = _obj
            __all__.append(_name)
            _seen.add(_name)

del importlib, pkgutil, types
del _seen
for _leaked in (
    "_finder",
    "_ispkg",
    "_module_name",
    "_module",
    "_name",
    "_obj",
    "_leaked",
):
    globals().pop(_leaked, None)
```

Do **not** wrap backends yet (Task 4).

In `src/lrrcs/model/analytical.py` delete the line `print_value_premium = print_long_short_premium`.

In `src/lrrcs/model/__init__.py` remove `print_value_premium` from the import and `__all__`.

In `src/lrrcs/empirical/__init__.py` stop importing `START`, `END`, `FIGURE2_START`, `connect_wrds`. Keep:

```python
from .figures import figure1, figure2, figure3, figure4
from .panel import build_annual_panel
from .tables import table_i, table_vi_data
from .wrds import EmpiricalDataError

__all__ = [
    "EmpiricalDataError",
    "build_annual_panel",
    "table_i",
    "table_vi_data",
    "figure1",
    "figure2",
    "figure3",
    "figure4",
]
```

`START`/`END`/`FIGURE2_START` remain as **internal** names in `empirical/goldens.py` for tests that import that module.

Change signatures:

`tables.py`:

```python
def table_i(bm: pd.DataFrame, start: int = 1930, end: int = 2003) -> pd.DataFrame:
    ...

def table_i_corr(bm: pd.DataFrame, start: int = 1930, end: int = 2003):
    ...

def table_vi_data(
    bm: pd.DataFrame, dc: pd.Series, start: int = 1930, end: int = 2003
) -> pd.DataFrame:
    ...
```

`figures.py`:

```python
def figure2(bm: pd.DataFrame, dc: pd.Series, path, start: int = 1952) -> None:
    ...
    if (prem.index >= start).any():
        prem = prem[prem.index >= start]
        vol = vol[vol.index >= start]
```

`panel.py` `build_annual_panel`:

```python
def build_annual_panel(
    refresh: bool = False, start: int = 1930, end: int = 2003
) -> pd.DataFrame:
```

Thread `start`/`end` into `_annualize` and `_write_outputs` instead of importing `START`/`END` for the public cut. Keep pulling CRSP from 1925 as today.

Add a one-paragraph NumPy docstring plus a fenced `python` example on `solve_analytical`, `print_long_short_premium`, `calibrate_from_data`, and `build_annual_panel` (public faces). Example shape:

````text
Examples
--------
```python
import lrrcs as lrr
lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```
````

- [ ] **Step 4: Run API tests and the non-WRDS suite**

Run: `uv run pytest tests/test_api_layout.py tests/test_empirical_panel.py tests/test_model.py -q`

Then: `uv run pytest -m "not wrds" -q`

Expected: PASS. Auto-discovery will also export `print_moments` and `print_calibration_summary`; that is allowed (they are public functions in public submodules). It must not export `connect_wrds` or `print_value_premium`.

- [ ] **Step 5: Commit**

```bash
git add src/lrrcs tests/test_api_layout.py
git commit -m "feat: flatten lrrcs public API like tidyfinance"
```

---

### Task 4: Honor tidyfinance's pandas/polars backend

**Files:**
- Create: `src/lrrcs/_backend.py`
- Modify: `src/lrrcs/__init__.py` — wrap `build_annual_panel`, `table_i`, `table_vi_data` after discovery
- Test: `tests/test_api_layout.py` (backend tests)

**Interfaces:**
- Consumes: Task 3 auto-discovery; `tidyfinance.get_backend` / `set_backend`
- Produces: `lrrcs._backend.to_pandas`, `to_polars`, `to_backend`, `use_backend`; wrapped empirical frame functions

- [ ] **Step 1: Write the failing backend tests**

Append to `tests/test_api_layout.py`:

```python
def test_table_i_returns_pandas_by_default():
    import pandas as pd
    import tidyfinance as tf
    import lrrcs as lrr
    tf.set_backend("pandas")
    bm = pd.read_csv("tests/fixtures/tiny_panel.csv")
    out = lrr.table_i(bm)
    assert isinstance(out, pd.DataFrame)


def test_table_i_returns_polars_when_backend_is_polars():
    import pandas as pd
    import polars as pl
    import tidyfinance as tf
    import lrrcs as lrr
    tf.set_backend("polars")
    try:
        bm = pd.read_csv("tests/fixtures/tiny_panel.csv")
        out = lrr.table_i(bm)
        assert isinstance(out, pl.DataFrame)
        out2 = lrr.table_i(pl.from_pandas(bm))
        assert isinstance(out2, pl.DataFrame)
    finally:
        tf.set_backend("pandas")


def test_no_lrr_set_backend():
    import lrrcs as lrr
    assert not hasattr(lrr, "set_backend")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_api_layout.py::test_table_i_returns_polars_when_backend_is_polars -v`

Expected: FAIL (`out` is still a pandas DataFrame).

- [ ] **Step 3: Implement `src/lrrcs/_backend.py` and wrap at the boundary**

```python
"""Convert frames at the lrrcs public boundary.

Honor tidyfinance.get_backend(). Do not import tidyfinance.backend privates.
"""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable


def get_active_backend() -> str:
    import tidyfinance as tf
    return tf.get_backend()


def to_pandas(obj: Any) -> Any:
    to_pd = getattr(obj, "to_pandas", None)
    if callable(to_pd):
        return to_pd()
    return obj


def to_polars(obj: Any) -> Any:
    import pandas as pd
    import polars as pl
    if isinstance(obj, (pl.DataFrame, pl.Series)):
        return obj
    if isinstance(obj, pd.DataFrame):
        return pl.from_pandas(obj)
    if isinstance(obj, pd.Series):
        name = obj.name if obj.name is not None else "value"
        return pl.from_pandas(obj.rename(name).to_frame())[name]
    return obj


def to_backend(obj: Any, backend: str | None = None) -> Any:
    backend = backend or get_active_backend()
    if backend == "polars":
        return to_polars(obj)
    return to_pandas(obj)


def use_backend(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapped(*args, **kwargs):
        args = tuple(to_pandas(a) for a in args)
        kwargs = {k: to_pandas(v) for k, v in kwargs.items()}
        return to_backend(fn(*args, **kwargs))
    return wrapped
```

In `src/lrrcs/__init__.py`, **after** auto-discovery and **before** the `del` cleanup, add:

```python
from ._backend import use_backend as _use_backend

_BACKEND_WRAPPED = ("build_annual_panel", "table_i", "table_vi_data")
for _name in _BACKEND_WRAPPED:
    if _name not in globals():
        raise RuntimeError(f"{_name!r} missing from public API")
    globals()[_name] = _use_backend(globals()[_name])
```

Include `_use_backend` in the leaked-name cleanup (`del _use_backend`). Do not wrap figure helpers.

- [ ] **Step 4: Run backend tests**

Run: `uv run pytest tests/test_api_layout.py -v`

Expected: PASS. Then `uv run pytest -m "not wrds" -q` — PASS.

- [ ] **Step 5: Commit**

```bash
git add src/lrrcs/_backend.py src/lrrcs/__init__.py tests/test_api_layout.py
git commit -m "feat: honor tidyfinance pandas/polars backend at lrrcs boundary"
```

---

### Task 5: Empirical downloads through tidyfinance

**Files:**
- Modify: `src/lrrcs/empirical/wrds.py` — adapter; delete `connect_wrds` and `_load_env`
- Modify: `src/lrrcs/empirical/panel.py` — `_pull_wrds` uses the adapter
- Modify: `tests/test_empirical_wrds.py`
- Test: `tests/test_empirical_wrds.py`

**Interfaces:**
- Consumes: Task 2–4 package; public `tf.download_data`, `tf.get_wrds_connection`, `tf.disconnect_connection`, `tf.set_wrds_credentials`
- Produces: `_download_crsp_monthly`, `_download_compustat_annual`, `_download_ccm_links`, `_download_crsp_msi`, `_download_crsp_mcti`, `_wrds_connection` (all private); `EmpiricalDataError`; `build_annual_panel` no longer imports `wrds`

Normalization contract for CRSP (tidyfinance v1 `crsp_monthly` is a processed file):

- Request `version="v1"` and `additional_columns=["retx", "prc"]`
- Prefer `calculation_date` as `date` when present (their `date` is month-truncated)
- Map `altprc` → `prc` only if `prc` is missing
- If `shrout` looks like shares (median > 1e5) divide by 1000 back to CRSP thousands
- Keep `ret` (raw), `retx`, `exchcd` or map `exchange` strings back to 1/2/3
- Do not use their `ret_adj` / `ret_excess` as Campbell–Shiller inputs
- After their extract, still run `apply_delisting_returns` on `retx` (and `ret` if their `ret` is unadjusted). Performance delists 400–599 with missing delisting return get −30% on **both** `ret` and `retx`

Compustat: call `tf.download_data("WRDS", "compustat_annual", start, end, additional_columns=["seq", "txditc", "pstkrv", "pstkl", "pstk"])` and recompute book equity with `book_equity_frame` (do not use tidyfinance's `be` column).

CCM: `tf.download_data("WRDS", "ccm_links")`. Rename `permno` → `lpermno` if needed so `_compustat_be` still works, **or** update `_compustat_be` to accept `permno`.

`msi` / `mcti`: there is no tidyfinance dataset. Use `_wrds_connection()` and pandas/`read_sql` with the existing queries in `panel.py`. Close via `tf.disconnect_connection`.

- [ ] **Step 1: Write failing credential and adapter tests**

Replace `tests/test_empirical_wrds.py` contents (keep the two `@pytest.mark.wrds` live tests, but import from `lrrcs` and drop `connect_wrds`):

```python
import pandas as pd
import pytest
from lrrcs.empirical.wrds import EmpiricalDataError, _wrds_connection
from lrrcs.empirical.panel import _pull_wrds


def test_wrds_connection_without_credentials_raises(monkeypatch, tmp_path):
    monkeypatch.delenv("WRDS_USER", raising=False)
    monkeypatch.delenv("WRDS_USERNAME", raising=False)
    monkeypatch.delenv("WRDS_PASSWORD", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(EmpiricalDataError, match="set_wrds_credentials"):
        _wrds_connection()


def test_pull_wrds_calls_tidyfinance_download_data(monkeypatch):
    calls = []

    def fake_download(**kwargs):
        calls.append(kwargs)
        domain = kwargs.get("domain")
        dataset = kwargs.get("dataset")
        if dataset == "crsp_monthly":
            return pd.DataFrame(
                {
                    "permno": [1],
                    "date": [pd.Timestamp("2000-06-30")],
                    "calculation_date": [pd.Timestamp("2000-06-30")],
                    "ret": [0.01],
                    "retx": [0.005],
                    "prc": [10.0],
                    "shrout": [1000.0],
                    "exchcd": [1],
                }
            )
        if dataset == "compustat_annual":
            return pd.DataFrame(
                {
                    "gvkey": ["001001"],
                    "datadate": [pd.Timestamp("1999-12-31")],
                    "seq": [100.0],
                    "txditc": [0.0],
                    "pstkrv": [0.0],
                    "pstkl": [0.0],
                    "pstk": [0.0],
                }
            )
        if dataset == "ccm_links":
            return pd.DataFrame(
                {
                    "permno": [1],
                    "gvkey": ["001001"],
                    "linkdt": [pd.Timestamp("1990-01-01")],
                    "linkenddt": [pd.Timestamp("2099-01-01")],
                }
            )
        raise AssertionError((domain, dataset))

    monkeypatch.setattr("lrrcs.empirical.wrds.tf.download_data", fake_download)

    class DummyConn:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False

    monkeypatch.setattr(
        "lrrcs.empirical.wrds._wrds_connection", lambda: DummyConn()
    )
    monkeypatch.setattr(
        "lrrcs.empirical.wrds._read_sql",
        lambda query, conn: pd.DataFrame(
            {"date": [pd.Timestamp("2000-06-30")], "vwretd": [0.01], "vwretx": [0.005]}
            if "msi" in query
            else {
                "caldt": [pd.Timestamp("2000-06-30")],
                "t90ret": [0.004],
                "cpi": [100.0],
            }
        ),
    )
    tables = _pull_wrds()
    datasets = {c["dataset"] for c in calls}
    assert "crsp_monthly" in datasets
    assert "compustat_annual" in datasets
    assert "ccm_links" in datasets
    crsp_call = next(c for c in calls if c["dataset"] == "crsp_monthly")
    assert crsp_call.get("version") == "v1"
    assert "retx" in crsp_call.get("additional_columns", [])
    assert "msf" in tables and "funda" in tables and "link" in tables
```

If `_pull_wrds` is still the old SQL function, this test fails on `connect_wrds` / missing `tf`.

Keep the live WRDS tests at the bottom, importing `from lrrcs.empirical.panel import build_annual_panel` and using `start`/`end` defaults instead of `START`/`END` unless they still import goldens internally.

- [ ] **Step 2: Run the new unit tests to verify they fail**

Run: `uv run pytest tests/test_empirical_wrds.py::test_wrds_connection_without_credentials_raises tests/test_empirical_wrds.py::test_pull_wrds_calls_tidyfinance_download_data -v`

Expected: FAIL (`connect_wrds` gone or `tf` not used).

- [ ] **Step 3: Implement the adapter and rewire `_pull_wrds`**

`src/lrrcs/empirical/wrds.py`:

```python
from __future__ import annotations

import pandas as pd
import tidyfinance as tf

from lrrcs._backend import to_pandas


class EmpiricalDataError(RuntimeError):
    pass


def _wrds_connection():
    try:
        return tf.get_wrds_connection()
    except Exception as exc:
        raise EmpiricalDataError(
            "WRDS credentials missing or rejected. "
            "Call tidyfinance.set_wrds_credentials()."
        ) from exc


def _read_sql(query: str, conn) -> pd.DataFrame:
    return pd.read_sql(query, conn)


def _download_crsp_monthly(
    start_date: str = "1925-12-01", end_date: str = "2003-12-31"
) -> pd.DataFrame:
    raw = to_pandas(
        tf.download_data(
            domain="WRDS",
            dataset="crsp_monthly",
            start_date=start_date,
            end_date=end_date,
            version="v1",
            additional_columns=["retx", "prc"],
        )
    )
    return _normalize_crsp_monthly(raw)


def _normalize_crsp_monthly(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).lower() for c in out.columns]
    if "calculation_date" in out.columns:
        out["date"] = pd.to_datetime(out["calculation_date"])
    else:
        out["date"] = pd.to_datetime(out["date"])
    if "prc" not in out.columns and "altprc" in out.columns:
        out["prc"] = out["altprc"]
    if "exchcd" not in out.columns and "exchange" in out.columns:
        out["exchcd"] = out["exchange"].map(
            {"NYSE": 1, "AMEX": 2, "NASDAQ": 3}
        )
    if out["shrout"].median() > 1e5:
        out["shrout"] = out["shrout"] / 1000.0
    need = ["permno", "date", "ret", "retx", "prc", "shrout", "exchcd"]
    missing = [c for c in need if c not in out.columns]
    if missing:
        raise EmpiricalDataError(
            f"CRSP extract missing columns {missing}; "
            "pass them via additional_columns"
        )
    return out[need]


def _download_compustat_annual(
    start_date: str = "1925-01-01", end_date: str = "2003-12-31"
) -> pd.DataFrame:
    return to_pandas(
        tf.download_data(
            domain="WRDS",
            dataset="compustat_annual",
            start_date=start_date,
            end_date=end_date,
            additional_columns=["seq", "txditc", "pstkrv", "pstkl", "pstk"],
        )
    )


def _download_ccm_links() -> pd.DataFrame:
    out = to_pandas(tf.download_data(domain="WRDS", dataset="ccm_links"))
    if "lpermno" not in out.columns and "permno" in out.columns:
        out = out.rename(columns={"permno": "lpermno"})
    return out


def _download_crsp_msi(
    start_date: str = "1925-12-01", end_date: str = "2003-12-31"
) -> pd.DataFrame:
    conn = _wrds_connection()
    try:
        return _read_sql(
            f"""
            SELECT date, vwretd, vwretx
            FROM crsp.msi
            WHERE date BETWEEN '{start_date}' AND '{end_date}'
            """,
            conn,
        )
    finally:
        tf.disconnect_connection(conn)


def _download_crsp_mcti(
    start_date: str = "1925-12-01", end_date: str = "2003-12-31"
) -> pd.DataFrame:
    conn = _wrds_connection()
    try:
        return _read_sql(
            f"""
            SELECT caldt, t90ret, cpiind AS cpi
            FROM crsp.mcti
            WHERE caldt BETWEEN '{start_date}' AND '{end_date}'
            """,
            conn,
        )
    finally:
        tf.disconnect_connection(conn)
```

If `tf.disconnect_connection` is not a public name, call `tidyfinance.download_wrds.disconnect_connection` only after confirming it is a documented public function; otherwise `conn.close()`.

Rewrite `panel.py` `_pull_wrds` to:

```python
from .wrds import (
    EmpiricalDataError,
    _download_ccm_links,
    _download_compustat_annual,
    _download_crsp_mcti,
    _download_crsp_monthly,
    _download_crsp_msi,
)

def _pull_wrds() -> dict[str, pd.DataFrame]:
    try:
        msf = _download_crsp_monthly()
        funda = _download_compustat_annual()
        link = _download_ccm_links()
        msi = _download_crsp_msi()
        mcti = _download_crsp_mcti()
    except EmpiricalDataError:
        raise
    except Exception as exc:
        raise EmpiricalDataError("WRDS download failed") from exc
    # tidyfinance v1 already keeps shrcd 10/11. Synthesize a names table
    # so _filter_universe still runs.
    names = (
        msf[["permno", "exchcd"]]
        .drop_duplicates("permno")
        .assign(
            namedt=pd.Timestamp("1925-01-01"),
            nameendt=pd.Timestamp("2099-12-31"),
            shrcd=11,
        )
    )
    return {
        "msf": msf,
        "names": names,
        "link": link,
        "funda": funda,
        "mcti": mcti,
        "msi": msi,
    }
```

Remove `_sql`, `_pull_msf`, and `connect_wrds` uses from `panel.py`. Keep parquet cache keys: if `names` is now derived, stop requiring a `names.parquet` in `_cache_ready` **or** still write `names` to parquet from the derived table so cache layout stays `msf`, `funda`, `names`, `link`, `mcti` plus `msi`. Keep writing all of them so `_cache_ready` does not need a rewrite.

`_filter_universe` currently requires `namedt`/`nameendt`/`shrcd`/`exchcd`. The synthetic names table above satisfies that.

Ken French historical BE download stays as it is.

- [ ] **Step 4: Run unit tests**

Run: `uv run pytest tests/test_empirical_wrds.py -m "not wrds" tests/test_empirical_construction.py tests/test_empirical_panel.py -q`

Expected: PASS. Do not run live WRDS in this task unless credentials are present; if they are, `uv run pytest tests/test_empirical_wrds.py -m wrds` may fail goldens — rematch only after Task 6 (sorts also change). If unit tests fail because `_filter_universe` drops the fake names, fix the synthetic names to include one row per permno with `exchcd` 1–3.

- [ ] **Step 5: Commit**

```bash
git add src/lrrcs/empirical/wrds.py src/lrrcs/empirical/panel.py tests/test_empirical_wrds.py
git commit -m "feat: pull WRDS extracts through tidyfinance"
```

---

### Task 6: NYSE BM quintiles through `assign_portfolio`

**Files:**
- Modify: `src/lrrcs/empirical/construction.py` — `form_bm_quintiles`
- Test: `tests/test_empirical_construction.py`

**Interfaces:**
- Consumes: Task 5 CRSP/Compustat frames with `exchcd`; public `tf.assign_portfolio`, `tf.breakpoint_options`, `tf.data_options`
- Produces: `form_bm_quintiles` still returns `permno, sort_year, quintile, me_june` with quintile 1 = growth, 5 = value

- [ ] **Step 1: Write the failing sort test**

Append to `tests/test_empirical_construction.py`:

```python
def test_form_bm_quintiles_uses_assign_portfolio(monkeypatch):
    import pandas as pd
    from lrrcs.empirical.construction import form_bm_quintiles

    seen = {}

    def fake_assign(data, sorting_variable, breakpoint_options=None, data_options=None, **kwargs):
        seen["sorting_variable"] = sorting_variable
        seen["n_portfolios"] = breakpoint_options["n_portfolios"]
        seen["exchanges"] = breakpoint_options["breakpoints_exchanges"]
        seen["exchange_col"] = data_options["exchange"]
        n = len(data)
        # 1 = growth ... 5 = value
        return pd.Series([1] * n)

    monkeypatch.setattr("lrrcs.empirical.construction.tf.assign_portfolio", fake_assign)
    monkeypatch.setattr(
        "lrrcs.empirical.construction.tf.breakpoint_options",
        lambda **kw: kw,
    )
    monkeypatch.setattr(
        "lrrcs.empirical.construction.tf.data_options",
        lambda **kw: kw,
    )

    idx = pd.date_range("1999-12-31", periods=2, freq="ME")
    # two dates: Dec 1999 and Jun 2000 so the June sort can see lagged Dec ME
    msf = pd.DataFrame(
        {
            "permno": [1, 1],
            "date": idx,
            "ret": [0.0, 0.0],
            "retx": [0.0, 0.0],
            "prc": [10.0, 10.0],
            "shrout": [1000.0, 1000.0],
            "exchcd": [1, 1],
        }
    )
    book = pd.DataFrame({"permno": [1], "year": [1999], "be": [50.0]})
    out = form_bm_quintiles(msf, book)
    assert seen["sorting_variable"] == "bm"
    assert seen["n_portfolios"] == 5
    assert seen["exchanges"] == "NYSE"
    assert not out.empty
    assert set(out["quintile"]) == {1}
```

If `freq="ME"` is too new, use `freq="M"`.

- [ ] **Step 2: Run it to verify it fails**

Run: `uv run pytest tests/test_empirical_construction.py::test_form_bm_quintiles_uses_assign_portfolio -v`

Expected: FAIL (`tf` not referenced in `construction.py`).

- [ ] **Step 3: Implement `form_bm_quintiles` with tidyfinance**

At the top of `construction.py` add `import tidyfinance as tf`. Keep `nyse_quintile_labels` (existing unit test). Replace the per-year `nyse_quintile_labels` call inside `form_bm_quintiles` with:

```python
        labeled = g.copy()
        labeled["exchange"] = labeled["exchcd"].map(
            {1: "NYSE", 2: "AMEX", 3: "NASDAQ"}
        )
        labeled["quintile"] = tf.assign_portfolio(
            labeled,
            sorting_variable="bm",
            breakpoint_options=tf.breakpoint_options(
                n_portfolios=5,
                breakpoints_exchanges="NYSE",
            ),
            data_options=tf.data_options(exchange="exchange"),
        ).astype(int)
```

`tf.assign_portfolio` honors the active backend: with default pandas it returns a pandas Series aligned to `labeled`. If a Series index misaligns, `labeled["quintile"] = ...to_numpy()`.

Leave `value_weight_monthly` and Campbell–Shiller unchanged.

- [ ] **Step 4: Run construction tests, then goldens if WRDS is available**

Run: `uv run pytest tests/test_empirical_construction.py -q`

Expected: PASS, including `test_nyse_breakpoints_assign_extremes` (old helper still exists).

If WRDS credentials exist:

Run: `uv run pytest tests/test_empirical_wrds.py tests/test_empirical_goldens.py -m wrds -v`

Expected: Table I E[R], σ(R), log(P/D), and return correlations still inside printed SEs (`within_se`). If a hard-gate cell fails, fix **our** normalization (CRSP columns, delisting on `retx`, June ME, exchange mapping), not the printed goldens. Value cash-flow ranking cells stay off the hard gate as in `CASHFLOW_NOTE`.

- [ ] **Step 5: Commit**

```bash
git add src/lrrcs/empirical/construction.py tests/test_empirical_construction.py
git commit -m "feat: assign BM quintiles with tidyfinance.assign_portfolio"
```

---

### Task 7: Companion docs and examples

**Files:**
- Modify: `README.md`, `docs/installation.md`, `docs/api.md`, `docs/package.md`, `docs/index.md`
- Modify: `docs/empirical.md`, `docs/model.md`, `docs/calibration.md`, `docs/implications.md`, `docs/time-series.md`, `docs/cross-section.md`, `docs/further.md`, `docs/climate.md`, `docs/other-risk-premia.md`, `docs/generalization.md`
- Modify: `examples/*.py` if any `from lrrcs.model import` remains
- Test: `tests/test_docs.py`

**Interfaces:**
- Consumes: Tasks 1–6 public API
- Produces: documented `tf` + `lrr` language; no `kiku_value_premium`; no `from lrrcs.model import` as the documented form; paper prose unchanged

Canonical snippets (use these, do not invent a third import style):

Package / README / index:

```python
import tidyfinance as tf
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

Empirical:

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

Calibration / other sorts:

```python
import lrrcs as lrr

dividends = lrr.calibrate_from_data(
    dc, long=dd_value, short=dd_growth, market=dd_market,
    frequency="annual", window=2,
)
params = lrr.get_table_ii_params()
params.dividends = dividends
solver = lrr.ModelSolver(params)
solver.solve()
print(lrr.compute_asset_pricing_moments(solver))
```

- [ ] **Step 1: Write failing docs tests**

Append to `tests/test_docs.py`:

```python
PACKAGE_PAGES = ("installation.md", "api.md", "package.md")
CODE_PAGES = SECTIONS + ("index.md",)


def test_package_pages_are_tidyfinance_companion():
    for name in PACKAGE_PAGES:
        text = (ROOT / name).read_text(encoding="utf-8")
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


def test_replica_code_uses_flat_lrr():
    for name in CODE_PAGES:
        text = (ROOT / name).read_text(encoding="utf-8")
        if "```python" not in text:
            continue
        assert "kiku_value_premium" not in text
        assert "from lrrcs.model import" not in text
        assert "from lrrcs.empirical import" not in text
        assert "from lrrcs.calibration import" not in text
        assert "from lrrcs.implications import" not in text
        assert "print_value_premium" not in text
        assert "lrr." in text or "import lrrcs as lrr" in text


def test_empirical_page_shows_tidyfinance_plumbing():
    text = (ROOT / "empirical.md").read_text(encoding="utf-8")
    assert "set_wrds_credentials" in text
    assert "import tidyfinance as tf" in text
    assert "lrr.build_annual_panel" in text
```

- [ ] **Step 2: Run them to verify they fail**

Run: `uv run pytest tests/test_docs.py::test_package_pages_are_tidyfinance_companion tests/test_docs.py::test_replica_code_uses_flat_lrr tests/test_docs.py::test_empirical_page_shows_tidyfinance_plumbing -v`

Expected: FAIL (old `from lrrcs.model import` / `kiku_value_premium` still on pages).

- [ ] **Step 3: Restyle the pages**

**README.md** install + example:

```markdown
# Long-run risks and the cross section

Python package `lrrcs`, a companion to [tidyfinance](https://github.com/tidy-finance/py-tidyfinance).
The model is Bansal and Yaron (2004) long-run risks with Epstein–Zin preferences.
Kiku (2006) is the first cross-sectional column.

tidyfinance gets data and sorts. `lrrcs` calibrates cash-flow loadings and prices claims.
Average returns never enter the cash-flow step.

**Documentation:** [tlorans.github.io/kiku-value-premium-replication](https://tlorans.github.io/kiku-value-premium-replication/)

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
```

Keep the existing page table (Time series / Cross section / …).

**docs/installation.md:** Python ≥ 3.11, required tidyfinance, `uv pip install -e .`, extras `[fast]` and `[data]` (matplotlib/pyarrow), WRDS via `tf.set_wrds_credentials()`, canonical two-import example. No `connect_wrds`, no `kiku_value_premium`.

**docs/api.md:** root-function map (`lrr.solve_analytical`, `lrr.build_annual_panel`, `lrr.calibrate_from_data`, …). One short note that submodules exist but are not the documented path. Empirical row mentions tidyfinance downloads/sorts.

**docs/package.md:** companion framing in two sentences, then links to installation/API/other portfolios.

**docs/index.md:** replace the current `from lrrcs.model import ...` fence with the canonical two-import example. Do not rewrite the introduction prose.

**Replica pages:** replace only fenced Python and any running `from lrrcs... import` / `kiku_value_premium` / `print_value_premium` / `connect_wrds` / `START, END` in those fences. Use `lrr.table_i(bm)` (defaults) instead of `table_i(bm, START, END)`. On `empirical.md`, add two sentences of plumbing: tidyfinance supplies CRSP/Compustat/CCM and NYSE breakpoints; `lrrcs` still builds Campbell–Shiller dividends and historical book equity. Do not change printed tables or economic paragraphs.

**examples:** every file starts with `import lrrcs as lrr` and calls `lrr.solve_analytical` etc. `demo.py` uses `print_long_short_premium`.

- [ ] **Step 4: Run docs tests and the full default suite**

Run: `uv run pytest tests/test_docs.py -q`

Then: `uv run pytest -m "not wrds" -q`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add README.md docs tests/test_docs.py examples
git commit -m "docs: present lrrcs as a tidyfinance companion"
```

---

## Self-review

**Spec coverage**

| Spec section | Task |
|---|---|
| Companion imports, no re-export | 3, 7 |
| `src/lrrcs/` only; delete `kiku_value_premium` | 2 |
| Auto-discovery `__init__` | 3 |
| Deps / 0.5.0 / 3.11 / extras | 1 |
| Public names stay/go; year defaults | 3 |
| Empirical via `tf.download_data` v1 + `retx` | 5 |
| `assign_portfolio` NYSE quintiles | 6 |
| Campbell–Shiller, hist BE, msi/mcti, consumption stay | 5 (untouched helpers) |
| `retx` delisting −30% 400–599 | 5 |
| `EmpiricalDataError` → `set_wrds_credentials` | 5 |
| Backend wrap list | 4 |
| No `lrr.set_backend`; no privates | 4 |
| Tests patch tidyfinance; default CI not live WRDS | 5, 6 |
| Docs package + replica restyle | 7 |
| Examples | 2 (imports), 7 (style) |
| Goldens rematch, paper numbers fixed | 6 live step |
| Out of scope (Great Docs, hatchling, PyPI, solver) | not tasked |

**Placeholders:** none of TBD / “similar to Task N” / “add error handling” remain.

**Types:** `build_annual_panel(refresh=False, start=1930, end=2003) -> DataFrame`; `table_i(bm, start=1930, end=2003)`; `table_vi_data(bm, dc, start=1930, end=2003)`; `_download_crsp_monthly() -> pd.DataFrame`; wrapper returns pandas or polars per `tf.get_backend()`.
