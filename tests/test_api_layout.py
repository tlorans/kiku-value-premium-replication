from pathlib import Path
import lrrcs as lrr


def test_version_is_0_6_0():
    assert lrr.__version__ == "0.6.0"


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
    assert project["version"] == "0.6.0"
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
        # the model and its results
        "LongRunRisksModel",
        "GridResults",
        "AnalyticalResults",
        "SimulationResults",
        "Summary",
        # parameters and errors
        "ModelParams",
        "PreferencesParams",
        "ConsumptionParams",
        "DividendParams",
        "SolverDivergenceError",
        "EmpiricalDataError",
        # measuring loadings and building data
        "estimate_long_run_leverage",
        "expected_growth_proxy",
        "filter_expected_growth",
        "build_annual_panel",
        "load_consumption",
        "load_deflator",
        "campbell_shiller_annual",
        "real_rf_from_monthly",
        "table_i",
        "table_vi_data",
    ):
        assert hasattr(lrr, name), name
        assert name in lrr.__all__, name


def test_root_api_is_small():
    """The documented surface stays curated rather than hoisting everything."""
    assert len(lrr.__all__) <= 25


def test_root_api_dropped_names():
    for name in (
        # never public
        "connect_wrds",
        "print_value_premium",
        "START",
        "END",
        "FIGURE2_START",
        "ROLE_ALIASES",
        "download_data",
        "set_wrds_credentials",
        # replaced by the model facade in 0.6.0
        "solve_analytical",
        "ModelSolver",
        "compute_asset_pricing_moments",
        "simulate_table_vii",
        "get_table_ii_params",
        "get_default_params",
        "price_from_loadings",
        "print_long_short_premium",
        "print_asset_pricing_moments",
        "print_table_vii",
        "print_calibration_summary",
        "print_moments",
        # reachable through lrrcs.calibration, not at the root
        "calibrate_from_data",
        "get_table_ii_dividends",
        "simulate_cashflow_moments",
        # reachable through lrrcs.empirical, not at the root
        "figure1",
    ):
        assert name not in lrr.__all__, name
        assert not hasattr(lrr, name), name


def test_engines_stay_importable_by_module_path():
    """The clean break is at the root namespace, not in the subpackages."""
    from lrrcs.calibration import calibrate_from_data, simulate_cashflow_moments
    from lrrcs.empirical import figure1
    from lrrcs.implications import compute_asset_pricing_moments, simulate_table_vii
    from lrrcs.model import ModelSolver, solve_analytical

    for obj in (
        calibrate_from_data,
        simulate_cashflow_moments,
        figure1,
        compute_asset_pricing_moments,
        simulate_table_vii,
        ModelSolver,
        solve_analytical,
    ):
        assert callable(obj)


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


def test_results_frames_follow_the_backend():
    import pandas as pd
    import polars as pl
    import tidyfinance as tf
    res = lrr.LongRunRisksModel().solve(n_x=15, n_s=4)
    tf.set_backend("pandas")
    assert isinstance(res.to_frame(), pd.DataFrame)
    tf.set_backend("polars")
    try:
        assert isinstance(res.to_frame(), pl.DataFrame)
    finally:
        tf.set_backend("pandas")


def test_no_lrr_set_backend():
    import lrrcs as lrr
    assert not hasattr(lrr, "set_backend")
