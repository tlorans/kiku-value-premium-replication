"""Table 1 sample moments on the shipped 1930–2015 annual file."""
from __future__ import annotations

import numpy as np
import pytest

from geap.lrr.estimation.data import load_annual, sample_moments
from geap.lrr.estimation.goldens import (
    TABLE_1,
    TABLE_2_LRR,
    TABLE_2_LRR_H,
    TABLE_3_LRR_MODEL,
    TABLE_3_SAMPLE,
    TABLE_4_ANNUAL,
    TABLE_5_ANNUAL_MODEL,
)
from geap.lrr.estimation.moments import MOMENT_NAMES
from geap.lrr.estimation.tables import (
    sample_table3,
    table3_frame,
    table3_keys,
    table5_frame,
)


def test_table1_sample_moments_on_shipped_annual():
    data = load_annual()
    assert data["year"].min() == 1930
    assert data["year"].max() == 2015
    m = sample_moments(data)
    # CRSP VW + BEA NIPA. Means should match printed Table 1 to the
    # paper's display precision except where NIPA revisions move
    # consumption.
    assert m["dd_mean"] == pytest.approx(TABLE_1["dd_mean"], abs=0.005)
    assert m["dd_std"] == pytest.approx(TABLE_1["dd_std"], abs=0.02)
    assert m["rm_mean"] == pytest.approx(TABLE_1["rm_mean"], abs=0.005)
    assert m["rm_std"] == pytest.approx(TABLE_1["rm_std"], abs=0.02)
    assert m["log_pd_mean"] == pytest.approx(TABLE_1["log_pd_mean"], abs=0.05)
    assert m["log_pd_std"] == pytest.approx(TABLE_1["log_pd_std"], abs=0.05)
    assert m["dc_mean"] == pytest.approx(TABLE_1["dc_mean"], abs=0.005)
    assert m["dc_std"] == pytest.approx(TABLE_1["dc_std"], abs=0.01)
    assert m["rf_mean"] == pytest.approx(TABLE_1["rf_mean"], abs=0.01)
    assert m["rf_std"] == pytest.approx(TABLE_1["rf_std"], abs=0.02)


def test_quarterly_sample_covers_1948_to_2015():
    from geap.lrr.estimation.data import load_quarterly

    q = load_quarterly()
    assert q["date"].dt.year.min() == 1948
    assert q["date"].dt.year.max() == 2015
    assert len(q) == 272
    assert q["dc"].mean() > 0


# Same abs tolerances as tests/test_bky_aggregation.py for the Table 3
# LRR model column at the published Table 2 vector.
_TABLE3_MODEL_TOL = {
    "mean_rf": 1e-3,
    "mean_zd": 1e-3,
    "mean_excess": 1e-3,
    "vol_dc": 2e-3,
    "ac1_dc": 2e-3,
    "ac2_dc": 2e-3,
    "vol_dd": 2e-3,
    "ac1_dd": 2e-3,
    "corr_dc_dd": 2e-3,
    "vol_zd": 1e-2,
    "ac1_zd": 1e-2,
    "vol_rd": 2e-3,
    "corr_rd_zd": 0.02,
    "corr_dc_zd": 0.08,
}


def test_table3_frame_model_column_at_table2():
    data = load_annual()
    frame = table3_frame(data, TABLE_2_LRR, TABLE_2_LRR_H)
    by_moment = frame.set_index("moment")
    for key, paper in TABLE_3_LRR_MODEL.items():
        assert by_moment.loc[key, "model"] == pytest.approx(
            paper, abs=_TABLE3_MODEL_TOL[key]
        ), key


def test_table3_includes_vol_eta2_in_paper_order():
    keys = table3_keys()
    assert "vol_eta2" in keys
    assert keys.index("e_eta2_s2") < keys.index("vol_eta2") < keys.index("ac1_eta2")
    data = load_annual()
    frame = table3_frame(data, TABLE_2_LRR, TABLE_2_LRR_H)
    by_moment = frame.set_index("moment")
    assert np.isfinite(by_moment.loc["vol_eta2", "model"])
    assert np.isfinite(by_moment.loc["ac1_eta2", "model"])
    assert np.isfinite(by_moment.loc["vol_eta2", "sample"])


def test_table3_frame_has_t_diff_and_sample():
    data = load_annual()
    frame = table3_frame(data, TABLE_2_LRR, TABLE_2_LRR_H)
    assert list(frame.columns) == ["moment", "sample", "model", "t_diff"]
    assert list(frame["moment"]) == list(table3_keys())
    samp = sample_table3(data)
    by_moment = frame.set_index("moment")
    for key, value in samp.items():
        if key not in by_moment.index:
            continue
        assert by_moment.loc[key, "sample"] == pytest.approx(value), key
    # Shipped panel, not the printed Table 3 sample column.
    assert by_moment.loc["ac1_dc", "sample"] != pytest.approx(
        TABLE_3_SAMPLE["ac1_dc"], abs=1e-4
    )
    assert by_moment.loc["mean_rf", "sample"] != pytest.approx(
        TABLE_3_SAMPLE["mean_rf"], abs=1e-4
    )
    for key in table3_keys():
        if key in MOMENT_NAMES:
            assert np.isfinite(by_moment.loc[key, "t_diff"]), key
    assert (by_moment["t_diff"].abs() > 0).any()


def test_table5_frame_model_column_at_annual_spec():
    data = load_annual()
    frame = table5_frame(data, TABLE_4_ANNUAL, h=1)
    by_moment = frame.set_index("moment")
    for key, paper in TABLE_5_ANNUAL_MODEL.items():
        assert by_moment.loc[key, "model"] == pytest.approx(paper, abs=2e-3), key
    assert list(frame.columns) == ["moment", "sample", "model", "t_diff"]


def test_shipped_table1_gaps_are_documented():
    data = load_annual()
    m = sample_moments(data)
    # Vintage lock: NIPA revisions moved consumption; the T-bill is not
    # the paper's series. These gaps must not close silently.
    assert m["dc_mean"] <= TABLE_1["dc_mean"] - 0.001
    assert m["rf_mean"] >= TABLE_1["rf_mean"] + 0.001
    samp = sample_table3(data)
    assert samp["ac1_dc"] < TABLE_3_SAMPLE["ac1_dc"] - 0.01
