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



def test_section_exports_exist():
    from lrrcs.empirical import (
        START,
        END,
        connect_wrds,
        build_annual_panel,
        table_i,
        table_vi_data,
        figure1,
        figure2,
        figure3,
        figure4,
    )
    from lrrcs.model import ModelSolver, solve_analytical, get_table_ii_params, print_long_short_premium
    from lrrcs.calibration import calibrate_from_data, simulate_cashflow_moments
    from lrrcs.implications import compute_asset_pricing_moments
    assert START == 1930 and END == 2003
    assert callable(connect_wrds)
    assert callable(build_annual_panel)
    assert callable(table_i)
    assert callable(table_vi_data)
    assert callable(figure1) and callable(figure2) and callable(figure3) and callable(figure4)
    assert callable(solve_analytical)
    assert callable(print_long_short_premium)
    assert callable(calibrate_from_data)
    assert callable(compute_asset_pricing_moments)


def test_old_flat_modules_are_gone():
    import importlib
    import pytest
    for name in ("params", "solver", "moments", "simulation", "analytical"):
        with pytest.raises(ModuleNotFoundError):
            importlib.import_module(f"lrrcs.{name}")


def test_kiku_value_premium_is_gone():
    import importlib
    import pytest
    with pytest.raises(ModuleNotFoundError):
        importlib.import_module("kiku_value_premium")


def test_no_climate_imports():
    import lrrcs, sys
    banned = [m for m in sys.modules if "climate_discount" in m or "corpo_research_papers" in m]
    assert banned == []
