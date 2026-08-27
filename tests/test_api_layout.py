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

    data_extra = "\n".join(extras["data"])
    assert "matplotlib" in data_extra
    assert "pyarrow" in data_extra
    assert "polars" in data_extra
    assert "plotnine" in data_extra


def test_root_api_has_companion_names():
    for name in (
        "solve_analytical",
        "get_table_ii_params",
        "print_long_short_premium",
        "ModelSolver",
        "calibrate_from_data",
        "compute_asset_pricing_moments",
        "build_annual_panel",
        "load_consumption",
        "load_deflator",
        "campbell_shiller_annual",
        "real_rf_from_monthly",
        "table_i",
        "table_vi_data",
        "figure1",
        "EmpiricalDataError",
        "expected_growth_proxy",
        "filter_expected_growth",
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
