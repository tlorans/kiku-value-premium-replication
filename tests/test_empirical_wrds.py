import pandas as pd
import pytest
from geap.lrr.empirical.wrds import (
    EmpiricalDataError,
    _normalize_crsp_monthly,
    _wrds_connection,
)
from geap.lrr.empirical.panel import _filter_universe, _pull_wrds


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

    monkeypatch.setattr("geap.lrr.empirical.wrds.tf.download_data", fake_download)

    class DummyConn:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False

    monkeypatch.setattr(
        "geap.lrr.empirical.wrds._wrds_connection", lambda: DummyConn()
    )
    def fake_read_sql(query, conn):
        q = query.lower()
        if "msedelist" in q or "dlret" in q:
            return pd.DataFrame(
                columns=["permno", "dlstdt", "dlret", "dlretx", "dlstcd"]
            )
        if "msi" in q:
            return pd.DataFrame(
                {
                    "date": [pd.Timestamp("2000-06-30")],
                    "vwretd": [0.01],
                    "vwretx": [0.005],
                }
            )
        return pd.DataFrame(
            {
                "caldt": [pd.Timestamp("2000-06-30")],
                "t90ret": [0.004],
                "cpi": [100.0],
            }
        )

    monkeypatch.setattr("geap.lrr.empirical.wrds._read_sql", fake_read_sql)
    tables = _pull_wrds()
    datasets = {c["dataset"] for c in calls}
    assert "crsp_monthly" in datasets
    assert "compustat_annual" in datasets
    assert "ccm_links" in datasets
    crsp_call = next(c for c in calls if c["dataset"] == "crsp_monthly")
    assert crsp_call.get("version") == "v1"
    assert "retx" in crsp_call.get("additional_columns", [])
    assert "msf" in tables and "funda" in tables and "link" in tables
    assert set(tables["msf"]["exchcd"]) <= {1, 2, 3}
    assert set(tables["names"]["exchcd"]) <= {1, 2, 3}


def test_normalize_crsp_monthly_recodes_exchcd_31_32_33():
    raw = pd.DataFrame(
        {
            "permno": [1, 2, 3, 4],
            "date": [pd.Timestamp("2000-01-31")] * 4,
            "ret": [0.01] * 4,
            "retx": [0.0] * 4,
            "prc": [10.0] * 4,
            "shrout": [1000.0] * 4,
            "exchcd": [31, 32, 33, 1],
        }
    )
    out = _normalize_crsp_monthly(raw)
    assert list(out["exchcd"]) == [1, 2, 3, 1]


def test_normalize_crsp_monthly_missing_columns_raises():
    raw = pd.DataFrame(
        {
            "permno": [1],
            "date": [pd.Timestamp("2000-01-31")],
            "ret": [0.01],
            "retx": [0.0],
            "prc": [10.0],
            "exchcd": [1],
        }
    )
    with pytest.raises(EmpiricalDataError, match="missing columns"):
        _normalize_crsp_monthly(raw)


def test_filter_universe_uses_monthly_exchcd_not_frozen_names():
    msf = pd.DataFrame(
        {
            "permno": [1, 1, 1],
            "date": pd.to_datetime(["2000-01-31", "2000-02-29", "2000-03-31"]),
            "ret": [0.01, 0.01, 0.01],
            "retx": [0.0, 0.0, 0.0],
            "prc": [10.0, 10.0, 10.0],
            "shrout": [1000.0, 1000.0, 1000.0],
            "exchcd": [1, 4, 1],
        }
    )
    names = pd.DataFrame(
        {
            "permno": [1],
            "exchcd": [1],
            "namedt": [pd.Timestamp("1925-01-01")],
            "nameendt": [pd.Timestamp("2099-12-31")],
            "shrcd": [11],
        }
    )
    out = _filter_universe(msf, names)
    assert set(pd.to_datetime(out["date"])) == {
        pd.Timestamp("2000-01-31"),
        pd.Timestamp("2000-03-31"),
    }


def test_permno_starting_on_exchcd_31_stays_in_universe():
    raw = pd.DataFrame(
        {
            "permno": [1, 1],
            "date": pd.to_datetime(["2000-01-31", "2000-02-29"]),
            "ret": [0.01, 0.01],
            "retx": [0.0, 0.0],
            "prc": [10.0, 10.0],
            "shrout": [1000.0, 1000.0],
            "exchcd": [31, 1],
        }
    )
    out = _filter_universe(_normalize_crsp_monthly(raw), pd.DataFrame())
    assert len(out) == 2
    assert set(out["exchcd"]) == {1}


@pytest.mark.wrds
def test_live_panel_covers_1930_2003():
    from geap.lrr.empirical.panel import build_annual_panel
    bm = build_annual_panel(refresh=True)
    assert set(bm["claim"].unique()) == {"Growth", "Value", "Market"}
    assert bm["year"].min() == 1930
    assert bm["year"].max() == 2003
    assert bm["ret"].notna().all()


@pytest.mark.wrds
def test_live_table_i_hard_gate_within_se():
    """Re-check Table I E[R], σ(R), log(P/D), and return correlations on a live panel.

    Value cash-flow ranking cells (dg_sd, Value–Market Δd corr, φ̃, innov_corr)
    stay off this gate; they do not sit inside the printed SE.
    """
    from geap.lrr.empirical.goldens import (
        END,
        START,
        TABLE_I,
        TABLE_I_CORR_RET,
    )
    from geap.lrr.empirical.panel import _cache_ready, build_annual_panel
    from geap.lrr.empirical.tables import table_i, table_i_corr, within_se

    bm = build_annual_panel(refresh=not _cache_ready())
    tab = table_i(bm).set_index("claim")
    for claim, stats in TABLE_I.items():
        for name in ("ret_mean", "ret_sd", "log_pd"):
            printed, se = stats[name]
            val = float(tab.loc[claim, name])
            assert within_se(val, printed, se), f"{claim} {name}: {val} vs {printed} ({se})"
    corr_ret, _ = table_i_corr(bm, START, END)
    for (a, b), (printed, se) in TABLE_I_CORR_RET.items():
        assert within_se(float(corr_ret.loc[a, b]), printed, se), (a, b, corr_ret.loc[a, b])
