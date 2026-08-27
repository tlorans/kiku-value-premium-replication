import numpy as np
import pandas as pd
from lrrcs.empirical.construction import (
    apply_delisting_returns,
    book_equity,
    nyse_quintile_labels,
    value_weight_monthly,
)
from lrrcs.empirical.dividends import campbell_shiller_annual
from lrrcs.empirical.goldens import (
    END,
    FIGURE2_START,
    START,
    TABLE_I,
    TABLE_VI_PHI,
)
from lrrcs.empirical.tables import newey_west_mean, within_se


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


def test_missing_retx_is_not_filled_with_ret():
    idx = pd.to_datetime(["2000-06-30", "2000-07-31"])
    msf = pd.DataFrame(
        {
            "permno": [1, 1],
            "date": idx,
            "ret": [0.02, 0.10],
            "retx": [0.01, np.nan],
            "prc": [10.0, 10.5],
            "shrout": [1000.0, 1000.0],
            "exchcd": [1, 1],
        }
    )
    asg = pd.DataFrame(
        {"permno": [1], "sort_year": [2000], "quintile": [5], "me_june": [10.0]}
    )
    out = value_weight_monthly(msf, asg)
    july = out[out["date"] == idx[1]].iloc[0]
    assert july["ret"] == 0.10
    assert abs(july["retx"] - 0.05) < 1e-12
    assert abs((july["ret"] - july["retx"]) - 0.05) < 1e-12


def test_delisting_compounds_ret_and_retx_separately():
    msf = pd.DataFrame(
        {
            "permno": [1],
            "date": [pd.Timestamp("2000-03-31")],
            "ret": [0.10],
            "retx": [0.08],
            "prc": [10.0],
            "shrout": [1000.0],
            "exchcd": [1],
        }
    )
    dl = pd.DataFrame(
        {
            "permno": [1],
            "dlstdt": [pd.Timestamp("2000-03-15")],
            "dlstcd": [231],
            "dlret": [-0.04],
            "dlretx": [-0.05],
        }
    )
    out = apply_delisting_returns(msf, dl)
    assert abs(float(out["ret"].iloc[0]) - ((1.10 * 0.96) - 1.0)) < 1e-12
    assert abs(float(out["retx"].iloc[0]) - ((1.08 * 0.95) - 1.0)) < 1e-12


def test_campbell_shiller_v0_is_100():
    idx = pd.date_range("2000-01-31", periods=24, freq="ME")
    ret = pd.Series(0.01, index=idx)
    retx = pd.Series(0.005, index=idx)
    defl = pd.Series({2000: 1.0, 2001: 1.0})
    out = campbell_shiller_annual(ret, retx, defl)
    assert set(out.columns) >= {"year", "ret", "dgrowth", "pd"}
    assert out["pd"].notna().any()


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

    idx = pd.date_range("1999-12-31", periods=2, freq="6ME")
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
