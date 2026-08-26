import kiku_value_premium as k


def test_version_is_0_3_0():
    assert k.__version__ == "0.3.0"


def test_section_exports_exist():
    from kiku_value_premium.empirical import (
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
    from kiku_value_premium.model import ModelSolver, solve_analytical, get_table_ii_params
    from kiku_value_premium.calibration import calibrate_from_data, simulate_cashflow_moments
    from kiku_value_premium.implications import compute_asset_pricing_moments
    assert START == 1930 and END == 2003
    assert callable(connect_wrds)
    assert callable(build_annual_panel)
    assert callable(table_i)
    assert callable(table_vi_data)
    assert callable(figure1) and callable(figure2) and callable(figure3) and callable(figure4)
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
