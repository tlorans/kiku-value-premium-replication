import lrrcs as k


def test_version_is_0_4_0():
    assert k.__version__ == "0.4.0"


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


def test_legacy_import_name():
    import kiku_value_premium as old
    import lrrcs as new
    assert old.__version__ == new.__version__


def test_no_climate_imports():
    import lrrcs, sys
    banned = [m for m in sys.modules if "climate_discount" in m or "corpo_research_papers" in m]
    assert banned == []
