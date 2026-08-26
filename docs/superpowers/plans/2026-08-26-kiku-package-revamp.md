# Kiku (2006) Package Revamp Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure `kiku-value-premium` into a 0.3.0 paper-section package (`empirical` / `model` / `calibration` / `implications`) that rebuilds Kiku (2006) 1930–2003 Tables I/VI and Figures 1–4 from WRDS, keeps the Bansal–Yaron / Tauchen–Hussey solver, and rewrites GitHub Pages as her four-section recipe.

**Architecture:** Four installable subpackages matching her Sections 2–5. Core install solves Table II with numpy/scipy/pandas. `[data]` extra pulls CRSP/Compustat via `.env`, writes a committable `data/annual_panel.csv`, and is the only path that talks to WRDS. Data columns must sit inside her printed Newey–West SEs. Climate stays out.

**Tech Stack:** Python ≥3.9, `uv`, numpy, scipy, pandas, pytest, matplotlib; optional numba, wrds, python-dotenv. GitHub Pages (Cayman + MathJax) under `docs/`.

**Spec:** `docs/superpowers/specs/2026-08-26-kiku-package-revamp-design.md`

## Global Constraints

- Identity: Kiku (2006) Bansal–Yaron replica. No `climate_discount`, no `corpo_research_papers`, no Melin–Zhang.
- Sample: `START, END = 1930, 2003`. Figure 2 window is 1952–2003.
- Empirical headline series: WRDS CRSP/Compustat + Davis–Fama–French book equity through 1962. Not Ken French 5×5 as the headline.
- SE gate: `|package − printed| ≤ printed Newey–West SE`. Goldens are her print. Do not edit goldens. Do not widen the band. Do not switch to Ken French if the gate fails — stop and ask.
- Table I / III / VII data SEs: Newey–West 8 lags. Table VI data SEs: Newey–West 4 lags.
- Public API is the four subpackages. No 0.2.0 six-step import shim.
- Package manager: `uv`. Version: 0.3.0.
- `.env` and `data/raw/` are gitignored. `.env` keys: `WRDS_USERNAME`, `WRDS_PASSWORD`.
- Default `uv run pytest` never hits WRDS. Live pull is `pytest -m wrds`.
- `calibrate_from_data` never takes returns or premia.

---

## File structure

Create:

| File | Responsibility |
|------|----------------|
| `.gitignore` | `.env`, `data/raw/`, `__pycache__`, `.venv` |
| `.env.example` | Empty WRDS keys |
| `src/kiku_value_premium/empirical/` | Section 2: WRDS, construction, tables, figures, goldens |
| `src/kiku_value_premium/model/` | Section 3: params, prefs, dynamics, grid, solver, analytical |
| `src/kiku_value_premium/calibration/` | Section 4: eq. 19, Table II, simulated III–V |
| `src/kiku_value_premium/implications/` | Section 5: moments VII–X, mechanism figures |
| `tests/` | One test module per subpackage plus API and WRDS markers |
| `data/annual_panel.csv` | Committable 1930–2003 G/V/M/RF/Δc (after WRDS run) |
| `docs/empirical.md`, `docs/model.md`, `docs/calibration.md`, `docs/implications.md` | Recipe pages |
| `examples/run_paper.py` | Executable Sections 2–5 |

Modify: `pyproject.toml`, `src/kiku_value_premium/__init__.py`, `README.md`, `docs/index.md`, `docs/installation.md`, `docs/api.md`, `docs/generalization.md`, `docs/_config.yml`, `examples/*.py`.

Delete after the move: top-level `src/kiku_value_premium/{params,preferences,analytical,dynamics,moments,calibration,discretization,simulation,solver}.py`; `docs/KIKU_RECIPE.md`, `docs/results.md`, `docs/examples.md`.

---

### Task 1: Repo hygiene and pytest config

**Files:**
- Create: `.gitignore`
- Create: `.env.example`
- Create: `tests/conftest.py`
- Modify: `pyproject.toml`

**Interfaces:**
- Consumes: nothing
- Produces: `[project.optional-dependencies] data = ["wrds", "python-dotenv", "matplotlib"]`; pytest marker `wrds`; version `0.3.0`

- [ ] **Step 1: Write the failing version assertion**

```python
# tests/test_api_layout.py
import kiku_value_premium as k


def test_version_is_0_3_0():
    assert k.__version__ == "0.3.0"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_api_layout.py::test_version_is_0_3_0 -v`

Expected: FAIL (`__version__` is `0.2.0` and/or `pyproject.toml` is `0.1.0`).

- [ ] **Step 3: Write hygiene files and bump versions**

`.gitignore`:

```
.env
.venv/
data/raw/
__pycache__/
*.pyc
.pytest_cache/
```

`.env.example`:

```
WRDS_USERNAME=
WRDS_PASSWORD=
```

`pyproject.toml` — set `version = "0.3.0"` and:

```toml
[project.optional-dependencies]
fast = ["numba>=0.56"]
data = ["wrds", "python-dotenv", "matplotlib"]
dev = ["pytest", "matplotlib", "numba>=0.56"]

[tool.pytest.ini_options]
testpaths = ["tests"]
markers = [
    "wrds: live WRDS reconstruction (needs repo-root .env)",
]
```

`tests/conftest.py`:

```python
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
```

In `src/kiku_value_premium/__init__.py` set `__version__ = "0.3.0"` only. Leave the 0.2 import list until Task 5.

- [ ] **Step 4: Run the version test and install extras**

Run: `uv pip install -e ".[dev]"`

Expected: install succeeds.

Expected: `test_version_is_0_3_0` PASS. Then `uv pip install -e ".[dev]"`.

- [ ] **Step 5: Commit**

```bash
git add .gitignore .env.example pyproject.toml tests/conftest.py tests/test_api_layout.py src/kiku_value_premium/__init__.py
git commit -m "chore: 0.3.0 extras, gitignore, and pytest wrds marker"
```

---

### Task 2: Goldens and Newey–West helper

**Files:**
- Create: `src/kiku_value_premium/empirical/__init__.py`
- Create: `src/kiku_value_premium/empirical/goldens.py`
- Create: `src/kiku_value_premium/empirical/tables.py` (Newey–West + `within_se` only in this task)
- Test: `tests/test_empirical_construction.py`

**Interfaces:**
- Consumes: nothing
- Produces: `START: int = 1930`, `END: int = 2003`, `FIGURE2_START: int = 1952`, `TABLE_I`, `TABLE_I_CORR_RET`, `TABLE_I_CORR_DG`, `TABLE_III_DATA`, `TABLE_VI_PHI`, `TABLE_VI_INNOV` as `{stat: (printed, se)}`; `newey_west_mean(x, lags) -> tuple[float, float]`; `within_se(value, printed, se) -> bool`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_empirical_construction.py
import numpy as np
from kiku_value_premium.empirical.goldens import (
    END,
    FIGURE2_START,
    START,
    TABLE_I,
    TABLE_VI_PHI,
)
from kiku_value_premium.empirical.tables import newey_west_mean, within_se


def test_windows():
    assert START == 1930
    assert END == 2003
    assert FIGURE2_START == 1952


def test_table_i_value_mean_return_golden():
    mu, se = TABLE_I["Value"]["ret_mean"]
    assert mu == 13.88
    assert se == 1.74


def test_table_vi_phi_goldens():
    assert TABLE_VI_PHI["Growth"] == (-0.38, 1.34)
    assert TABLE_VI_PHI["Value"] == (2.16, 1.44)
    assert TABLE_VI_PHI["Market"] == (0.66, 1.20)


def test_newey_west_mean_constant_series():
    mu, se = newey_west_mean(np.ones(20), lags=8)
    assert abs(mu - 1.0) < 1e-12
    assert se == 0.0


def test_within_se_accepts_on_band():
    assert within_se(13.88 + 1.74, 13.88, 1.74)
    assert not within_se(13.88 + 1.75, 13.88, 1.74)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_empirical_construction.py -v`

Expected: FAIL (`empirical` package missing).

- [ ] **Step 3: Write goldens and Newey–West**

`src/kiku_value_premium/empirical/__init__.py` — export only `START`, `END` for now:

```python
from .goldens import END, FIGURE2_START, START

__all__ = ["START", "END", "FIGURE2_START"]
```

`src/kiku_value_premium/empirical/goldens.py`:

```python
START = 1930
END = 2003
FIGURE2_START = 1952

# Table I Panel A: (printed, Newey-West SE, 8 lags). Returns and growth in percent.
TABLE_I = {
    "Growth": {
        "ret_mean": (7.81, 1.98),
        "ret_sd": (20.2, 2.00),
        "dg_mean": (0.68, 1.25),
        "dg_sd": (13.9, 2.24),
        "log_pd": (3.61, 0.18),
    },
    "Value": {
        "ret_mean": (13.88, 1.74),
        "ret_sd": (29.9, 4.34),
        "dg_mean": (3.63, 3.06),
        "dg_sd": (18.1, 2.69),
        "log_pd": (3.25, 0.12),
    },
    "Market": {
        "ret_mean": (8.56, 1.79),
        "ret_sd": (20.1, 2.23),
        "dg_mean": (0.85, 0.95),
        "dg_sd": (10.9, 2.41),
        "log_pd": (3.34, 0.13),
    },
}
TABLE_I_CORR_RET = {
    ("Growth", "Value"): (0.75, 0.05),
    ("Growth", "Market"): (0.95, 0.01),
    ("Value", "Market"): (0.87, 0.04),
}
TABLE_I_CORR_DG = {
    ("Growth", "Value"): (0.32, 0.17),
    ("Growth", "Market"): (0.80, 0.09),
    ("Value", "Market"): (0.53, 0.10),
}
TABLE_III_DATA = {
    "mean": (1.96, 0.32),
    "sd": (2.20, 0.45),
    "ac1": (0.44, 0.12),
    "ac2": (0.16, 0.15),
}
# Table VI uses 4 lags
TABLE_VI_PHI = {
    "Growth": (-0.38, 1.34),
    "Value": (2.16, 1.44),
    "Market": (0.66, 1.20),
}
TABLE_VI_INNOV = {
    "Growth": (0.37, 0.14),
    "Value": (0.30, 0.07),
    "Market": (0.58, 0.15),
}
```

`src/kiku_value_premium/empirical/tables.py` (helpers only):

```python
from __future__ import annotations
import numpy as np


def newey_west_mean(x: np.ndarray, lags: int = 8) -> tuple[float, float]:
    y = np.asarray(x, dtype=float)
    y = y[np.isfinite(y)]
    t = y.size
    if t == 0:
        return float("nan"), float("nan")
    mu = float(y.mean())
    e = y - mu
    gamma0 = float(np.mean(e * e))
    acc = gamma0
    lmax = min(int(lags), t - 1)
    for k in range(1, lmax + 1):
        w = 1.0 - k / (lmax + 1)
        acc += 2.0 * w * float(np.mean(e[k:] * e[:-k]))
    se = float(np.sqrt(max(acc / t, 0.0)))
    return mu, se


def sd_and_se(x: np.ndarray, lags: int = 8) -> tuple[float, float]:
    y = np.asarray(x, dtype=float)
    y = y[np.isfinite(y)]
    if y.size < 2:
        return float("nan"), float("nan")
    sd = float(np.std(y, ddof=1))
    if sd == 0.0:
        return 0.0, 0.0
    m2, se_m2 = newey_west_mean((y - y.mean()) ** 2, lags=lags)
    return sd, float(se_m2 / (2.0 * sd))


def within_se(value: float, printed: float, se: float) -> bool:
    return abs(float(value) - float(printed)) <= float(se) + 1e-12
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `uv run pytest tests/test_empirical_construction.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kiku_value_premium/empirical tests/test_empirical_construction.py
git commit -m "feat: add Kiku printed goldens and Newey-West helper"
```

---

### Task 3: Move the model subpackage

**Files:**
- Create: `src/kiku_value_premium/model/__init__.py`
- Move: `params.py`, `preferences.py`, `dynamics.py`, `discretization.py`, `solver.py`, `analytical.py` → `model/`
- Modify: relative imports stay `from .params import ...` inside `model/`
- Test: `tests/test_model.py`
- Delete: the six top-level copies after the move

**Interfaces:**
- Consumes: current top-level modules
- Produces: `kiku_value_premium.model.{ModelParams, PreferencesParams, ConsumptionParams, DividendParams, get_table_ii_params, get_default_params, EpsteinZinPreferences, Dynamics, StateGrid, ModelSolver, solve_analytical, print_value_premium, AnalyticalSolution}`

- [ ] **Step 1: Write the failing import test**

```python
# tests/test_model.py
from kiku_value_premium.model import (
    Dynamics,
    EpsteinZinPreferences,
    ModelParams,
    ModelSolver,
    get_table_ii_params,
    solve_analytical,
)


def test_table_ii_phi():
    p = get_table_ii_params()
    assert p.prefs.delta == 0.999
    assert p.prefs.gamma == 10.0
    assert p.prefs.psi == 1.5
    assert p.cons.rho == 0.98
    assert p.dividends["value"].phi == 6.2
    assert p.dividends["growth"].phi == 2.6
    assert p.dividends["market"].phi == 2.8


def test_analytical_value_has_higher_lr_premium():
    sol = solve_analytical(get_table_ii_params())
    assert sol.premium_lr["value"] > sol.premium_lr["growth"]


def test_tiny_solver_runs():
    solver = ModelSolver(get_table_ii_params(), n_x=5, n_s=2, n_quad=3)
    solver.solve()
    assert solver.converged
    assert "value" in solver.z
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_model.py -v`

Expected: FAIL (`kiku_value_premium.model` missing).

- [ ] **Step 3: Move files and add `get_table_ii_params`**

Create `src/kiku_value_premium/model/`. Move the six files into it (`git mv`). In `model/params.py` add:

```python
def get_table_ii_params() -> ModelParams:
    """Exact Table II calibration."""
    return ModelParams()


def get_default_params() -> ModelParams:
    return get_table_ii_params()
```

Delete the old `get_default_params` body (keep one definition). Internal `from .params import` paths inside the six files do not change.

`model/__init__.py`:

```python
from .params import (
    ConsumptionParams,
    DividendParams,
    ModelParams,
    PreferencesParams,
    get_default_params,
    get_table_ii_params,
)
from .preferences import EpsteinZinPreferences
from .dynamics import Dynamics
from .discretization import StateGrid
from .solver import ModelSolver
from .analytical import AnalyticalSolution, print_value_premium, solve_analytical

__all__ = [
    "ModelParams",
    "PreferencesParams",
    "ConsumptionParams",
    "DividendParams",
    "get_table_ii_params",
    "get_default_params",
    "EpsteinZinPreferences",
    "Dynamics",
    "StateGrid",
    "ModelSolver",
    "AnalyticalSolution",
    "solve_analytical",
    "print_value_premium",
]
```

Top-level `src/kiku_value_premium/__init__.py` still imports from `.params` etc. Those will break until Task 5. Temporarily point those imports at `.model` so the repo still imports:

```python
from .model import (
    ModelParams,
    PreferencesParams,
    ConsumptionParams,
    DividendParams,
    get_default_params,
    Dynamics,
    EpsteinZinPreferences,
    StateGrid,
    ModelSolver,
    solve_analytical,
    print_value_premium,
)
from .calibration import (
    calibrate_from_data,
    estimate_long_run_leverage,
    get_table_ii_dividends,
)
from .moments import compute_asset_pricing_moments, print_asset_pricing_moments
from .simulation import simulate_moments, print_moments
```

`calibration.py`, `simulation.py`, `moments.py` still do `from .params import` / `from .solver import` / `from .dynamics import`. Update those three files now:

- `calibration.py`: `from .model.params import DividendParams, ModelParams, get_default_params`
- `simulation.py`: `from .model.params import ModelParams, get_default_params` and `from .model.dynamics import Dynamics`
- `moments.py`: `from .model.solver import ModelSolver, HAS_NUMBA, njit` and `from .model.params import get_default_params`

- [ ] **Step 4: Run model tests**

Run: `uv run pytest tests/test_model.py -v`

Expected: PASS (tiny 5×2 solver may take a few seconds).

- [ ] **Step 5: Commit**

```bash
git add src/kiku_value_premium tests/test_model.py
git commit -m "refactor: move Bansal-Yaron solver into model subpackage"
```

---

### Task 4: Move the calibration subpackage

**Files:**
- Create: `src/kiku_value_premium/calibration/__init__.py`
- Create: `src/kiku_value_premium/calibration/leverage.py` (move `estimate_long_run_leverage`)
- Create: `src/kiku_value_premium/calibration/from_data.py` (move `calibrate_from_data`)
- Create: `src/kiku_value_premium/calibration/table_ii.py` (move `get_table_ii_dividends`, `TABLE_II_DIVIDENDS`)
- Create: `src/kiku_value_premium/calibration/simulation.py` (move `simulate_moments` as `simulate_cashflow_moments`)
- Delete: `src/kiku_value_premium/calibration.py`, `src/kiku_value_premium/simulation.py`
- Test: `tests/test_calibration.py`

**Interfaces:**
- Consumes: `kiku_value_premium.model.DividendParams`, `Dynamics`
- Produces: `estimate_long_run_leverage(dc, dd, window=2) -> float`, `calibrate_from_data(dc, dd_dict, frequency="annual", window=2, default_phi_sigma=7.5) -> dict[str, DividendParams]`, `get_table_ii_dividends() -> dict[str, DividendParams]`, `simulate_cashflow_moments(n_sims=200, years=74, seed=42, params=None) -> dict`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_calibration.py
import inspect
import numpy as np
from kiku_value_premium.calibration import (
    calibrate_from_data,
    estimate_long_run_leverage,
    get_table_ii_dividends,
    simulate_cashflow_moments,
)


def test_calibrate_from_data_has_no_returns_argument():
    names = inspect.signature(calibrate_from_data).parameters
    assert "returns" not in names
    assert "premia" not in names
    assert "ret" not in names


def test_eq19_recovers_known_phi():
    rng = np.random.default_rng(0)
    n = 80
    dc = rng.normal(0.02, 0.03, size=n)
    ma = np.array([np.nan, np.nan] + [dc[t - 2 : t].mean() for t in range(2, n)])
    dd = 0.01 + 2.16 * np.nan_to_num(ma, nan=0.0) + rng.normal(0, 0.05, size=n)
    phi = estimate_long_run_leverage(dc, dd, window=2)
    assert abs(phi - 2.16) < 0.4


def test_table_ii_dividends():
    d = get_table_ii_dividends()
    assert d["value"].phi == 6.2
    assert d["growth"].phi == 2.6


def test_simulate_cashflow_moments_keys():
    mom = simulate_cashflow_moments(n_sims=2, years=10, seed=1)
    assert "E[dc]" in mom["consumption"]
    assert "sigma(dc)" in mom["consumption"]
    assert "AC1" in mom["consumption"]
    assert set(mom["dividends"]) == {"growth", "value", "market"}
    assert "E[dd]" in mom["dividends"]["value"]
```

Keep the current return dict (`consumption` / `dividends` nested keys above). Rename `simulate_moments` to `simulate_cashflow_moments`. Public name is `simulate_cashflow_moments` only.

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_calibration.py -v`

Expected: FAIL (package `kiku_value_premium.calibration` is still a module).

- [ ] **Step 3: Split into the calibration package**

Move the existing functions. `leverage.py` / `from_data.py` import `DividendParams` from `..model.params`. `simulation.py` imports `Dynamics` from `..model.dynamics`. `calibrate_from_data` signature must remain `(dc, dd_dict, frequency="annual", window=2, default_phi_sigma=7.5)` — no returns.

`calibration/__init__.py`:

```python
from .leverage import estimate_long_run_leverage
from .from_data import calibrate_from_data, print_calibration_summary
from .table_ii import get_table_ii_dividends
from .simulation import print_moments, simulate_cashflow_moments

__all__ = [
    "estimate_long_run_leverage",
    "calibrate_from_data",
    "get_table_ii_dividends",
    "simulate_cashflow_moments",
    "print_moments",
    "print_calibration_summary",
]
```

Update top-level `__init__.py` calibration imports to the new names.

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_calibration.py tests/test_model.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kiku_value_premium/calibration src/kiku_value_premium/__init__.py tests/test_calibration.py
git add -u src/kiku_value_premium/calibration.py src/kiku_value_premium/simulation.py
git commit -m "refactor: move cash-flow calibration into calibration subpackage"
```

---

### Task 5: Move implications and lock the 0.3 public API

**Files:**
- Create: `src/kiku_value_premium/implications/__init__.py`
- Create: `src/kiku_value_premium/implications/moments.py` (move `compute_asset_pricing_moments`)
- Create: `src/kiku_value_premium/implications/figures.py`
- Delete: `src/kiku_value_premium/moments.py`
- Modify: `src/kiku_value_premium/__init__.py`
- Test: `tests/test_implications.py`, `tests/test_api_layout.py`

**Interfaces:**
- Consumes: `ModelSolver`, `solve_analytical`
- Produces: `compute_asset_pricing_moments(solver) -> dict`, `print_asset_pricing_moments(moments) -> None`, `figure_lr_premium(path)`, `figure_mean_pd(solver, path)`, `figure5(path)`; package `__version__ == "0.3.0"`; package `__all__` is the four-section names in the spec; `import kiku_value_premium.params` fails

- [ ] **Step 1: Write the failing API tests**

Replace `tests/test_api_layout.py` with:

```python
import kiku_value_premium as k


def test_version_is_0_3_0():
    assert k.__version__ == "0.3.0"


def test_section_exports_exist():
    from kiku_value_premium.empirical import START, END
    from kiku_value_premium.model import ModelSolver, solve_analytical, get_table_ii_params
    from kiku_value_premium.calibration import calibrate_from_data, simulate_cashflow_moments
    from kiku_value_premium.implications import compute_asset_pricing_moments
    assert START == 1930 and END == 2003
    assert callable(solve_analytical)
    assert callable(calibrate_from_data)
    assert callable(compute_asset_pricing_moments)


def test_old_flat_modules_are_gone():
    import importlib
    import pytest
    for name in ("params", "solver", "moments", "simulation", "analytical"):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(f"kiku_value_premium.{name}")


def test_no_climate_imports():
    import kiku_value_premium, sys
    banned = [m for m in sys.modules if "climate_discount" in m or "corpo_research_papers" in m]
    assert banned == []
```

```python
# tests/test_implications.py
from kiku_value_premium.model import ModelSolver, get_table_ii_params, solve_analytical
from kiku_value_premium.implications import compute_asset_pricing_moments


def test_value_premium_positive_on_tiny_grid():
    solver = ModelSolver(get_table_ii_params(), n_x=5, n_s=2, n_quad=3)
    solver.solve()
    mom = compute_asset_pricing_moments(solver)
    assert mom["mean_return"]["value"] > mom["mean_return"]["growth"]
    assert mom["mean_log_pd"]["value"] < mom["mean_log_pd"]["growth"]
    assert mom["capm_beta"]["value"] / mom["capm_beta"]["growth"] < 1.05
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_api_layout.py tests/test_implications.py -v`

Expected: FAIL (`implications` missing and/or version still 0.2.0).

- [ ] **Step 3: Move moments, add figures stubs, rewrite package `__init__.py`**

Move `moments.py` to `implications/moments.py`. Change its imports to `from ..model.solver import ModelSolver, HAS_NUMBA, njit` and `from ..model.params import get_default_params`.

`implications/figures.py` — implement `figure_lr_premium` from `solve_analytical` (bar chart of `premium_lr` by asset), `figure_mean_pd` from `solver.mean_pd()` if it exists else `np.dot(solver.stationary, solver.z[name])`, and `figure5` as a placeholder that draws the model-implied premium vs consumption-vol series from `Dynamics` + analytical spread (full simulated analogue of Figure 2; 200 years is enough for the unit test). Save PDF and SVG next to the given `path`.

`implications/__init__.py` exports `compute_asset_pricing_moments`, `print_asset_pricing_moments`, `figure_lr_premium`, `figure_mean_pd`, `figure5`.

Rewrite `src/kiku_value_premium/__init__.py` to the spec docstring (four sections, not six steps), `__version__ = "0.3.0"`, and re-exports listed in spec §3. Do not re-export `simulate_moments` or `get_default_params` at the top level unless they are the spec names (`simulate_cashflow_moments`, `get_table_ii_params`).

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_api_layout.py tests/test_implications.py tests/test_model.py tests/test_calibration.py -v`

Expected: PASS

- [ ] **Step 5: Update examples to the 0.3 imports**

In `examples/demo.py`, `examples/calibration_example.py`, `examples/calibrate_any_portfolio.py`, `examples/calibrate_from_real_data.py` replace:

- `from kiku_value_premium.analytical import ...` → `from kiku_value_premium.model import ...`
- `from kiku_value_premium.params import ...` → `from kiku_value_premium.model import ...`
- `from kiku_value_premium.solver import ModelSolver` → `from kiku_value_premium.model import ModelSolver`
- `from kiku_value_premium.moments import ...` → `from kiku_value_premium.implications import ...`
- `from kiku_value_premium.simulation import simulate_moments` → `from kiku_value_premium.calibration import simulate_cashflow_moments`
- `from kiku_value_premium.calibration import` stays valid (now a package)

- [ ] **Step 6: Commit**

```bash
git add src/kiku_value_premium examples tests
git commit -m "feat: lock 0.3 public API on four paper sections"
```

---

### Task 6: Book equity, NYSE breakpoints, Campbell–Shiller dividends

**Files:**
- Create: `src/kiku_value_premium/empirical/construction.py`
- Create: `src/kiku_value_premium/empirical/dividends.py`
- Modify: `tests/test_empirical_construction.py`

**Interfaces:**
- Consumes: nothing
- Produces: `book_equity(seq, txditc, pstkrv, pstkl, pstk) -> float`; `nyse_quintile_labels(bm_all, bm_nyse) -> ndarray[int]` with 1=growth … 5=value; `campbell_shiller_annual(ret: pd.Series, retx: pd.Series, deflator: pd.Series) -> pd.DataFrame` with columns `year, ret, dgrowth, pd`

- [ ] **Step 1: Write the failing tests**

```python
import numpy as np
import pandas as pd
from kiku_value_premium.empirical.construction import book_equity, nyse_quintile_labels
from kiku_value_premium.empirical.dividends import campbell_shiller_annual


def test_book_equity_prefers_redemption_then_liquidation_then_par():
    assert book_equity(seq=100, txditc=10, pstkrv=5, pstkl=9, pstk=8) == 105.0
    assert book_equity(seq=100, txditc=10, pstkrv=np.nan, pstkl=9, pstk=8) == 101.0
    assert book_equity(seq=100, txditc=np.nan, pstkrv=np.nan, pstkl=np.nan, pstk=8) == 92.0


def test_nyse_breakpoints_assign_extremes():
    nyse = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    all_bm = np.array([0.5, 3.0, 9.0])
    labels = nyse_quintile_labels(all_bm, nyse)
    assert labels[0] == 1  # growth
    assert labels[2] == 5  # value


def test_campbell_shiller_v0_is_100():
    idx = pd.date_range("2000-01-31", periods=24, freq="ME")
    ret = pd.Series(0.01, index=idx)
    retx = pd.Series(0.005, index=idx)
    defl = pd.Series({2000: 1.0, 2001: 1.0})
    out = campbell_shiller_annual(ret, retx, defl)
    assert set(out.columns) >= {"year", "ret", "dgrowth", "pd"}
    assert out["pd"].notna().any()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_empirical_construction.py -v`

Expected: FAIL on the new tests (import errors).

- [ ] **Step 3: Implement construction helpers**

`book_equity`: preferred = first finite of `(pstkrv, pstkl, pstk)`, else 0; txditc missing → 0; return `seq + txditc - preferred`.

`nyse_quintile_labels`: `np.quantile(bm_nyse, [0.2, 0.4, 0.6, 0.8])` then `np.digitize(bm_all, edges, right=True) + 1` so labels are 1..5.

`campbell_shiller_annual`: copy the loop from `corpo_research_papers/papers/02-mz-firm-dcf/code/pull_bm.py` `campbell_shiller_annual` (V0=100, `d=(ret-retx)*v`, `v *= 1+retx`, calendar-year sum of dividends, compound monthly returns, deflate, `pd = v_real/div_real`, `dgrowth = Δ log div_real`, real return via deflator ratio). Do not import that paper repo.

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_empirical_construction.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kiku_value_premium/empirical tests/test_empirical_construction.py
git commit -m "feat: book equity, NYSE breakpoints, Campbell-Shiller dividends"
```

---

### Task 7: Table I, Table VI data, Figures 1–4 from an annual panel

**Files:**
- Modify: `src/kiku_value_premium/empirical/tables.py`
- Create: `src/kiku_value_premium/empirical/figures.py`
- Create: `tests/fixtures/tiny_panel.csv`
- Test: `tests/test_empirical_panel.py`

**Interfaces:**
- Consumes: panel DataFrame with columns `year, claim, ret, dgrowth, pd` plus a consumption series `year, dc`
- Produces: `table_i(bm, start, end) -> pd.DataFrame`; `table_vi_data(bm, dc, start, end) -> pd.DataFrame`; `figure1(bm, path)`, `figure2(bm, dc, path)`, `figure3(dc, path)`, `figure4(bm, dc, path)` writing PDF and SVG

- [ ] **Step 1: Write the failing tests**

Create `tests/fixtures/tiny_panel.csv` with 12 rows (4 years × Growth/Value/Market) of invented numbers, plus `tests/fixtures/tiny_dc.csv`.

```python
# tests/test_empirical_panel.py
from pathlib import Path
import pandas as pd
from kiku_value_premium.empirical.tables import table_i, table_vi_data
from kiku_value_premium.empirical.figures import figure1, figure2, figure3, figure4

FIX = Path(__file__).parent / "fixtures"


def test_table_i_schema():
    bm = pd.read_csv(FIX / "tiny_panel.csv")
    out = table_i(bm, 2000, 2003)
    assert {"claim", "ret_mean", "ret_se", "ret_sd", "dg_mean", "log_pd"} <= set(out.columns)
    assert set(out["claim"]) == {"Growth", "Value", "Market"}


def test_table_vi_schema():
    bm = pd.read_csv(FIX / "tiny_panel.csv")
    dc = pd.read_csv(FIX / "tiny_dc.csv").set_index("year")["dc"]
    out = table_vi_data(bm, dc, 2000, 2003)
    assert {"claim", "phi_tilde", "phi_se", "innov_corr"} <= set(out.columns)


def test_figures_write_files(tmp_path):
    bm = pd.read_csv(FIX / "tiny_panel.csv")
    dc = pd.read_csv(FIX / "tiny_dc.csv").set_index("year")["dc"]
    figure1(bm, tmp_path / "f1.pdf")
    figure2(bm, dc, tmp_path / "f2.pdf")
    figure3(dc, tmp_path / "f3.pdf")
    figure4(bm, dc, tmp_path / "f4.pdf")
    for name in ("f1", "f2", "f3", "f4"):
        pdf = tmp_path / f"{name}.pdf"
        svg = tmp_path / f"{name}.svg"
        assert pdf.exists() and pdf.stat().st_size > 0
        assert svg.exists() and svg.stat().st_size > 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_empirical_panel.py -v`

Expected: FAIL (`table_i` / figures missing).

- [ ] **Step 3: Implement tables and figures**

`table_i`: for each claim, Newey–West 8 lags on `ret`, `dgrowth`, `log(pd)` means; `sd_and_se` for vols; plus a correlations block (or a second returned frame stored as attributes). Return a tidy DataFrame; also attach `corr_ret` and `corr_dg` as DataFrames on a small result object **or** return one DataFrame of means and compute correlations in `table_i_correlations(bm, start, end)`. Prefer two functions: `table_i` (Panel A) and `table_i_corr` (Panel B), both used by the SE gate.

`table_vi_data`: for each claim, OLS of `dgrowth` on 2-year MA of lagged `dc` (same formula as `estimate_long_run_leverage` plus an intercept), Newey–West **4** lags on the coefficient (implement `newey_west_ols_se(y, x, lags=4)`); innovation correlation = corr(eq. 19 residual, AR(1) residual of `dc`).

Figures (matplotlib, her captions):

- Figure 1: bar of 100×(Value−Growth) returns, 1930–2003 (use whatever years the panel has).
- Figure 2: expected premium = OLS of spread on lagged Growth/Value `pd` and `dgrowth`; consumption vol = 3-year MA of squared AR(1) residuals of `dc`; rescale vol to premium mean/sd; slice years ≥ 1952 when present.
- Figure 3: ARMA(1,1) spectrum vs Bartlett periodogram of `dc`.
- Figure 4: two panels, 3-year MA of `dgrowth` vs rescaled 3-year MA of `dc`.

Each `figureN(…, path)` saves `path` and `path.with_suffix(".svg")`.

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_empirical_panel.py tests/test_empirical_construction.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kiku_value_premium/empirical tests/test_empirical_panel.py tests/fixtures
git commit -m "feat: Table I, Table VI data, and Figures 1-4 from an annual panel"
```

---

### Task 8: Consumption, deflator, risk-free rate

**Files:**
- Create: `src/kiku_value_premium/empirical/consumption.py`
- Create: `src/kiku_value_premium/empirical/rates.py`
- Test: `tests/test_empirical_macro.py`

**Interfaces:**
- Consumes: FRED CSVs (public) or local fixtures
- Produces: `load_consumption() -> pd.Series` indexed by year, log growth of real per-capita ND+S; `load_deflator() -> pd.Series`; `real_rf(t90ret, cpi) -> pd.Series` = 90-day T-bill minus 12-month MA of inflation, then calendar-year average

- [ ] **Step 1: Write the failing tests**

```python
import numpy as np
import pandas as pd
from kiku_value_premium.empirical.consumption import consumption_growth_from_levels
from kiku_value_premium.empirical.rates import real_rf_from_monthly


def test_consumption_growth_is_log_diff_of_per_capita():
    years = np.arange(1929, 1934)
    nd = pd.Series([100.0, 102.0, 103.0, 104.0, 105.0], index=years)
    sv = pd.Series([200.0, 202.0, 204.0, 206.0, 208.0], index=years)
    pop = pd.Series([10.0, 10.0, 10.0, 10.0, 10.0], index=years)
    dc = consumption_growth_from_levels(nd, sv, pop)
    assert dc.index.min() == 1930
    level = (nd + sv) / pop
    assert abs(dc.loc[1930] - np.log(level.loc[1930] / level.loc[1929])) < 1e-12


def test_real_rf_subtracts_twelve_month_inflation_ma():
    idx = pd.date_range("1999-01-31", periods=24, freq="ME")
    t90 = pd.Series(0.01 / 12, index=idx)
    cpi = pd.Series(np.linspace(100, 103, 24), index=idx)
    rf = real_rf_from_monthly(t90, cpi)
    assert rf.index.year.min() == 1999 or rf.index.year.min() == 2000
    assert rf.notna().any()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `uv run pytest tests/test_empirical_macro.py -v`

Expected: FAIL

- [ ] **Step 3: Implement**

`consumption_growth_from_levels(nd, sv, pop) = log((nd+sv)/pop).diff().dropna()`.

`load_consumption()` downloads:

- `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DNDGRA3A086NBEA`
- `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DSERRA3A086NBEA`
- `https://fred.stlouisfed.org/graph/fredgraph.csv?id=B230RC0A052NBEA`

`load_deflator()` downloads `DPCERD3A086NBEA`.

`real_rf_from_monthly`: inflation_t = log(cpi_t / cpi_{t-1}); `real = t90ret - inflation.rolling(12).mean()`; annual = mean within calendar year.

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_empirical_macro.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add src/kiku_value_premium/empirical tests/test_empirical_macro.py
git commit -m "feat: NIPA consumption growth and real T-bill"
```

---

### Task 9: WRDS connection and `build_annual_panel`

**Files:**
- Create: `src/kiku_value_premium/empirical/wrds.py`
- Create: `src/kiku_value_premium/empirical/panel.py`
- Create: `src/kiku_value_premium/empirical/construction.py` additions for the FF loop (or a new `portfolios.py` if `construction.py` is getting large — keep in `construction.py` if it stays under ~250 lines)
- Test: `tests/test_empirical_wrds.py`

**Interfaces:**
- Consumes: repo-root `.env`, WRDS, Ken French historical book equity, FRED
- Produces: `class EmpiricalDataError(RuntimeError)`; `connect_wrds() -> wrds.Connection`; `build_annual_panel(refresh: bool = False) -> pd.DataFrame` writing `data/raw/` (gitignored) and `data/annual_panel.csv` with columns `year, claim, ret, dgrowth, pd` plus a companion `data/consumption_annual.csv` (`year, dc`) and RF column or `data/rf_annual.csv`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_empirical_wrds.py
import pytest
from kiku_value_premium.empirical.wrds import EmpiricalDataError, connect_wrds


def test_connect_without_env_raises(monkeypatch, tmp_path):
    monkeypatch.delenv("WRDS_USERNAME", raising=False)
    monkeypatch.delenv("WRDS_PASSWORD", raising=False)
    monkeypatch.chdir(tmp_path)
    with pytest.raises(EmpiricalDataError):
        connect_wrds()


@pytest.mark.wrds
def test_live_panel_covers_1930_2003():
    from kiku_value_premium.empirical.goldens import END, START
    from kiku_value_premium.empirical.panel import build_annual_panel
    bm = build_annual_panel(refresh=True)
    sub = bm[(bm["year"] >= START) & (bm["year"] <= END)]
    assert set(sub["claim"].unique()) == {"Growth", "Value", "Market"}
    assert sub["year"].min() == START
    assert sub["year"].max() == END
    assert sub["ret"].notna().all()
```

- [ ] **Step 2: Run tests**

Run: `uv run pytest tests/test_empirical_wrds.py -v`

Expected: FAIL (`wrds.py` missing). Default pytest (no `-m wrds`) should collect the first test only as non-marked.

Add to `pyproject.toml`:

```toml
addopts = "-m not wrds"
```

so default pytest skips the live test.

- [ ] **Step 3: Implement `connect_wrds`**

```python
# src/kiku_value_premium/empirical/wrds.py
from __future__ import annotations
import os
from pathlib import Path

class EmpiricalDataError(RuntimeError):
    pass

def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError as exc:
        raise EmpiricalDataError(
            "Install the data extra: uv pip install -e '.[data]'"
        ) from exc
    root = Path(__file__).resolve().parents[3]
    env = root / ".env"
    if env.exists():
        load_dotenv(env)

def connect_wrds():
    _load_env()
    user = os.environ.get("WRDS_USERNAME") or os.environ.get("WRDS_USER")
    password = os.environ.get("WRDS_PASSWORD") or os.environ.get("WRDS_PASS")
    if not user or not password:
        raise EmpiricalDataError(
            "Missing WRDS_USERNAME / WRDS_PASSWORD in repo-root .env"
        )
    try:
        import wrds
    except ImportError as exc:
        raise EmpiricalDataError(
            "Install the data extra: uv pip install -e '.[data]'"
        ) from exc
    return wrds.Connection(wrds_username=user, wrds_password=password)
```

Never print the password.

- [ ] **Step 4: Implement `build_annual_panel`**

`panel.py` algorithm (her Section 2.1):

1. Cache directory `data/raw/` at repo root. If `refresh=False` and `msf.parquet`, `funda.parquet`, `names.parquet`, `link.parquet`, `mcti.parquet` exist, skip WRDS.
2. Else `connect_wrds()` and pull:
   - `crsp.msf`: `permno, date, ret, retx, prc, shrout` for 1925-12-01 through 2003-12-31
   - `crsp.msenames`: `permno, namedt, nameendt, shrcd, exchcd`
   - `crsp.ccmxpf_linktable`: `gvkey, lpermno, linkdt, linkenddt, linktype, linkprim` with `linktype in ('LU','LC')` and `linkprim in ('P','C')`
   - `comp.funda`: `gvkey, datadate, fyear, seq, txditc, pstkrv, pstkl, pstk, indfmt, datafmt, consol, popsrc` filtered to `indfmt='INDL'`, `datafmt='STD'`, `consol='C'`, `popsrc='D'`
   - `crsp.mcti`: `caldt, t90ret, cpi`
   - `crsp.msi`: `date, vwretd` (market with dividends) and `vwretx` if present
3. Keep ordinary shares `shrcd in (10, 11)` and `exchcd in (1, 2, 3)`.
4. Book equity = `book_equity(...)`. Merge Compustat BE to PERMNO via the link table on `datadate ∈ [linkdt, linkenddt]`. For fiscal years before Compustat coverage, merge Ken French historical book-equity (download zip from the Ken French data library “Historical Book Equity” file; map PERMNO). Compustat wins when both exist.
5. For each June year t: ME_june = |prc|×shrout; ME_december_t-1 for the BM denominator; BM = BE_{fiscal t-1} / ME_dec_{t-1}. NYSE breakpoints from `exchcd==1`. Assign quintiles. Growth=1, value=5.
6. Hold the sort from July t through June t+1. Value-weight monthly `ret` and `retx` inside each quintile (and the CRSP VW market).
7. `campbell_shiller_annual` each of Growth, Value, Market. Deflate with `load_deflator()`. Slice 1930–2003.
8. RF from `real_rf_from_monthly`. Consumption from `load_consumption()`.
9. Write `data/annual_panel.csv` (`year, claim, ret, dgrowth, pd`) and `data/consumption_annual.csv` (`year, dc`). Return the panel.

Copy `.env` from `C:\DBD\corpo_research_papers\.env` or `C:\DBD\corpo_research_papers\papers\01-discounting\code\.env` into this repo root if the user has not already. Do not commit it.

- [ ] **Step 5: Run the non-WRDS test**

Run: `uv run pytest tests/test_empirical_wrds.py -v`

Expected: `test_connect_without_env_raises` PASS; live test skipped.

- [ ] **Step 6: Run the live test with `.env`**

Run: `uv pip install -e ".[data]"` then `uv run pytest tests/test_empirical_wrds.py -m wrds -v`

Expected: PASS, and `data/annual_panel.csv` exists. If WRDS is unreachable, stop and report; do not substitute Ken French returns.

- [ ] **Step 7: Commit (panel yes, raw no, env no)**

```bash
git add src/kiku_value_premium/empirical tests/test_empirical_wrds.py data/annual_panel.csv data/consumption_annual.csv pyproject.toml
git commit -m "feat: WRDS 1930-2003 value/growth/market annual panel"
```

---

### Task 10: SE-matching gate

**Files:**
- Create: `tests/test_empirical_goldens.py`
- Consumes: committed `data/annual_panel.csv`, `data/consumption_annual.csv`

**Interfaces:**
- Consumes: `table_i`, `table_i_corr`, `table_vi_data`, `within_se`, goldens
- Produces: default pytest fails if any Table I / III / VI data cell lies outside her printed SE

- [ ] **Step 1: Write the failing (or already failing) gate tests**

```python
# tests/test_empirical_goldens.py
from pathlib import Path
import numpy as np
import pandas as pd
from kiku_value_premium.empirical.goldens import (
    END,
    START,
    TABLE_I,
    TABLE_I_CORR_DG,
    TABLE_I_CORR_RET,
    TABLE_III_DATA,
    TABLE_VI_INNOV,
    TABLE_VI_PHI,
)
from kiku_value_premium.empirical.tables import table_i, table_i_corr, table_vi_data, within_se

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "annual_panel.csv"
DC = ROOT / "data" / "consumption_annual.csv"


def _panel():
    assert PANEL.exists(), "run build_annual_panel(refresh=True) first"
    return pd.read_csv(PANEL)


def test_table_i_within_printed_se():
    bm = _panel()
    tab = table_i(bm, START, END).set_index("claim")
    # table_i stores E[R], σ(R), E[Δd], σ(Δd) in percent; log(P/D) in logs.
    for claim, stats in TABLE_I.items():
        for name, (printed, se) in stats.items():
            val = float(tab.loc[claim, name])
            assert within_se(val, printed, se), f"{claim} {name}: {val} vs {printed} ({se})"


def test_table_i_correlations_within_se():
    bm = _panel()
    corr_ret, corr_dg = table_i_corr(bm, START, END)
    for (a, b), (printed, se) in TABLE_I_CORR_RET.items():
        assert within_se(float(corr_ret.loc[a, b]), printed, se), (a, b, corr_ret.loc[a, b])
    for (a, b), (printed, se) in TABLE_I_CORR_DG.items():
        assert within_se(float(corr_dg.loc[a, b]), printed, se), (a, b, corr_dg.loc[a, b])


def test_table_iii_consumption_within_se():
    dc = pd.read_csv(DC).set_index("year")["dc"]
    x = dc.loc[START:END].to_numpy() * 100.0
    from kiku_value_premium.empirical.tables import newey_west_mean, sd_and_se
    mu, se_mu = newey_west_mean(x, lags=8)
    sd, se_sd = sd_and_se(x, lags=8)
    ac1 = float(np.corrcoef(x[1:], x[:-1])[0, 1])
    ac2 = float(np.corrcoef(x[2:], x[:-2])[0, 1])
    assert within_se(mu, *TABLE_III_DATA["mean"])
    assert within_se(sd, *TABLE_III_DATA["sd"])
    assert within_se(ac1, *TABLE_III_DATA["ac1"])
    assert within_se(ac2, *TABLE_III_DATA["ac2"])


def test_table_vi_within_se():
    bm = _panel()
    dc = pd.read_csv(DC).set_index("year")["dc"]
    tab = table_vi_data(bm, dc, START, END).set_index("claim")
    for claim, (printed, se) in TABLE_VI_PHI.items():
        assert within_se(float(tab.loc[claim, "phi_tilde"]), printed, se), claim
    for claim, (printed, se) in TABLE_VI_INNOV.items():
        assert within_se(float(tab.loc[claim, "innov_corr"]), printed, se), claim
```

`table_i` stores `ret_mean`, `ret_sd`, `dg_mean`, `dg_sd` in percent and `log_pd` in logs, matching her print. The test indexes those same column names.

- [ ] **Step 2: Run the gate**

Run: `uv run pytest tests/test_empirical_goldens.py -v`

Expected: FAIL on at least one cell if construction is off.

- [ ] **Step 3: Construction-audit loop**

Walk this list, re-run the gate after each change, do not edit goldens:

1. `shrcd` in {10, 11} and `exchcd` in {1, 2, 3}
2. NYSE-only breakpoints
3. DFF book-equity merge through 1962
4. Campbell–Shiller `ret` vs `retx`, V0=100
5. PCE deflator on dividends, prices, and returns
6. Calendar-year aggregation (not July–June)

If a cell still fails after the six checks, **stop and ask**. Do not switch the headline series to Ken French. Do not widen `within_se`.

- [ ] **Step 4: Run the full default suite**

Run: `uv run pytest -v`

Expected: PASS (wrds tests skipped).

- [ ] **Step 5: Commit**

```bash
git add tests/test_empirical_goldens.py src/kiku_value_premium/empirical data/annual_panel.csv data/consumption_annual.csv
git commit -m "test: SE gate against Kiku printed Table I, III, and VI"
```

---

### Task 11: Model-column ranking tests and Figure 5

**Files:**
- Modify: `tests/test_implications.py`
- Modify: `src/kiku_value_premium/implications/figures.py`
- Create: copy SVGs into `docs/figures/` when generated

**Interfaces:**
- Consumes: `simulate_cashflow_moments`, `ModelSolver`, `compute_asset_pricing_moments`, `solve_analytical`
- Produces: tests that value E[R] > market > growth, value log(P/D) < growth, `capm_beta["value"] / capm_beta["growth"] < 1`, simulated consumption mean in [1.0, 3.0]; `figure5` writes PDF/SVG

- [ ] **Step 1: Write the failing ranking tests**

```python
# append to tests/test_implications.py
from kiku_value_premium.calibration import simulate_cashflow_moments
from kiku_value_premium.implications.figures import figure5, figure_lr_premium, figure_mean_pd


def test_simulated_consumption_moment_ranking():
    mom = simulate_cashflow_moments(n_sims=20, years=74, seed=1)
    assert 1.0 <= mom["consumption"]["E[dc]"] <= 3.0


def test_figures_lr_and_5(tmp_path):
    from kiku_value_premium.model import ModelSolver, get_table_ii_params
    figure_lr_premium(tmp_path / "lr.pdf")
    solver = ModelSolver(get_table_ii_params(), n_x=5, n_s=2, n_quad=3)
    solver.solve()
    figure_mean_pd(solver, tmp_path / "pd.pdf")
    figure5(tmp_path / "f5.pdf")
    assert (tmp_path / "lr.pdf").stat().st_size > 0
    assert (tmp_path / "f5.pdf").stat().st_size > 0
```

- [ ] **Step 2: Run tests**

Run: `uv run pytest tests/test_implications.py -v`

Expected: FAIL until `figure5` exists and ranking holds.

- [ ] **Step 3: Implement `figure5`**

Simulate 1000 annual observations from `Dynamics` (monthly then annualize). Construct the model-implied value premium as in Figure 2 (project simulated value−growth returns on lagged P/D and Δd). Plot against 3-year MA of squared AR(1) consumption residuals, rescaled. Save PDF and SVG.

Also generate `figures/lr_premium_decomposition.svg` and `figures/mean_log_pd.svg` from Table II and copy them to `docs/figures/`.

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_implications.py tests/test_model.py tests/test_calibration.py -v`

Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add tests/test_implications.py src/kiku_value_premium/implications figures docs/figures
git commit -m "test: model ranking and Kiku Figures 5 / mechanism plots"
```

---

### Task 12: Docs, README, and `run_paper.py`

**Files:**
- Create: `docs/empirical.md`, `docs/model.md`, `docs/calibration.md`, `docs/implications.md`
- Create: `examples/run_paper.py`
- Modify: `docs/index.md`, `docs/installation.md`, `docs/api.md`, `docs/generalization.md`, `docs/_config.yml`, `README.md`
- Delete: `docs/KIKU_RECIPE.md`, `docs/results.md`, `docs/examples.md`

**Interfaces:**
- Consumes: 0.3 public API
- Produces: GitHub Pages nav in paper order; README is a pointer; `examples/run_paper.py` runs §2 if `[data]`+`.env` exist else skips and continues from Table II

- [ ] **Step 1: Write a failing prose/nav check**

```python
# tests/test_docs.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs"


def test_pages_nav_is_paper_order():
    cfg = (ROOT / "_config.yml").read_text(encoding="utf-8")
    for name in ("empirical.md", "model.md", "calibration.md", "implications.md"):
        assert name in cfg
    for gone in ("KIKU_RECIPE.md", "results.md", "examples.md"):
        assert gone not in cfg
        assert not (ROOT / gone).exists()


def test_readme_does_not_host_six_step_recipe():
    text = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    assert "6-step" not in text.lower() and "six-step" not in text.lower()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `uv run pytest tests/test_docs.py -v`

Expected: FAIL (`KIKU_RECIPE.md` still in nav).

- [ ] **Step 3: Rewrite Pages**

`docs/_config.yml` `header_pages`:

```yaml
header_pages:
  - index.md
  - installation.md
  - empirical.md
  - model.md
  - calibration.md
  - implications.md
  - api.md
  - generalization.md
```

Each of `empirical.md`, `model.md`, `calibration.md`, `implications.md` has three blocks: **What she does**, **What you call** (0.3 imports), **What you should see** (printed cells from goldens + figure embeds from `docs/figures/`).

`index.md`: identity, four-section table, link to installation. No six-step table.

`installation.md`: `uv pip install -e .`, `uv pip install -e ".[fast]"`, `uv pip install -e ".[data]"`, `.env` keys, “without WRDS you can still solve Table II”.

`api.md`: the spec §3 table.

`generalization.md`: `calibrate_from_data` on other portfolios. Delete climate-kernel language. Do not mention `climate_discount`.

`README.md`: identity, `uv` install, link to Pages. No second copy of the recipe.

`examples/run_paper.py`:

```python
from pathlib import Path

def main():
    print("Kiku (2006) recipe — paper order")
    try:
        from kiku_value_premium.empirical.panel import build_annual_panel
        from kiku_value_premium.empirical.tables import table_i
        from kiku_value_premium.empirical.goldens import START, END
        bm = build_annual_panel(refresh=False)
        print(table_i(bm, START, END))
    except Exception as exc:
        print(f"Section 2 skipped ({exc}). Continuing from Table II.")
    from kiku_value_premium.model import get_table_ii_params, solve_analytical, ModelSolver, print_value_premium
    from kiku_value_premium.calibration import simulate_cashflow_moments
    from kiku_value_premium.implications import compute_asset_pricing_moments, print_asset_pricing_moments
    params = get_table_ii_params()
    print_value_premium(solve_analytical(params))
    print(simulate_cashflow_moments(n_sims=20, years=74, seed=1))
    solver = ModelSolver(params, n_x=15, n_s=4, n_quad=7)
    solver.solve()
    print_asset_pricing_moments(compute_asset_pricing_moments(solver))

if __name__ == "__main__":
    main()
```

Use `n_x=15` in the example so it finishes; document that the paper default is 30.

- [ ] **Step 4: Run tests**

Run: `uv run pytest tests/test_docs.py tests/test_api_layout.py -v`

Expected: PASS

- [ ] **Step 5: Full suite**

Run: `uv run pytest -v`

Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add docs README.md examples/run_paper.py tests/test_docs.py
git add -u docs/KIKU_RECIPE.md docs/results.md docs/examples.md
git commit -m "docs: paper-order GitHub Pages recipe for Kiku (2006)"
```

---

## Self-review

**Spec coverage**

| Spec section | Task |
|--------------|------|
| §1 Identity | 5, 12 |
| §2 Locked decisions | 1, 9, 10 |
| §3 Public API | 3, 4, 5 |
| §4 Data flow | 8, 9 |
| §5 WRDS pipeline | 6, 7, 8, 9 |
| §5.4 Figures 1–4 | 7 |
| §6 Model/calibration/implications | 3, 4, 5, 11 |
| §7 Documentation | 12 |
| §8 SE gate | 2, 10 |
| §9 Files | all |
| §10 Out of scope | 5 (`test_no_climate_imports`), 12 (no climate in generalization) |
| §11 Key decisions | 9 extra, 10 goldens, 12 Pages |
| Figure 5 | 11 |
| `.env` / gitignore | 1, 9 |

**Placeholder scan:** `simulate_cashflow_moments` keys are locked (`consumption["E[dc]"]`, nested `dividends`). `table_i` columns are locked as percent except `log_pd`. No TBD remains in the construction algorithm.

**Type consistency:** `get_table_ii_params`, `simulate_cashflow_moments`, `build_annual_panel(refresh: bool)`, `EmpiricalDataError`, `START/END`, `within_se`, `table_i`, `table_vi_data`, `figure1`–`figure5` are the names later tasks import.
