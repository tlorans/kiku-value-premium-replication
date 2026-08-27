from pathlib import Path
import pandas as pd
from lrrcs.empirical.tables import table_i, table_vi_data
from lrrcs.empirical.figures import figure1, figure2, figure3, figure4

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


def test_table_vi_ignores_dc_outside_window():
    bm = pd.read_csv(FIX / "tiny_panel.csv")
    dc = pd.read_csv(FIX / "tiny_dc.csv").set_index("year")["dc"]
    long_dc = pd.concat(
        [pd.Series({1998: 0.99, 1999: -0.50, 2004: 0.80, 2005: -0.40}), dc]
    ).sort_index()
    wide = table_vi_data(bm, long_dc, 2000, 2003).set_index("claim")
    sliced = table_vi_data(bm, dc.loc[2000:2003], 2000, 2003).set_index("claim")
    for claim in ("Growth", "Value", "Market"):
        for col in ("phi_tilde", "innov_corr"):
            a, b = wide.loc[claim, col], sliced.loc[claim, col]
            if pd.isna(a) and pd.isna(b):
                continue
            assert a == b, (claim, col, a, b)


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
