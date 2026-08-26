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


@pytest.mark.wrds
def test_live_table_i_hard_gate_within_se():
    """Re-check Table I E[R], σ(R), log(P/D), and return correlations on a live panel.

    Value cash-flow ranking cells (dg_sd, Value–Market Δd corr, φ̃, innov_corr)
    stay off this gate; they do not sit inside the printed SE.
    """
    from kiku_value_premium.empirical.goldens import (
        END,
        START,
        TABLE_I,
        TABLE_I_CORR_RET,
    )
    from kiku_value_premium.empirical.panel import _cache_ready, build_annual_panel
    from kiku_value_premium.empirical.tables import table_i, table_i_corr, within_se

    bm = build_annual_panel(refresh=not _cache_ready())
    tab = table_i(bm, START, END).set_index("claim")
    for claim, stats in TABLE_I.items():
        for name in ("ret_mean", "ret_sd", "log_pd"):
            printed, se = stats[name]
            val = float(tab.loc[claim, name])
            assert within_se(val, printed, se), f"{claim} {name}: {val} vs {printed} ({se})"
    corr_ret, _ = table_i_corr(bm, START, END)
    for (a, b), (printed, se) in TABLE_I_CORR_RET.items():
        assert within_se(float(corr_ret.loc[a, b]), printed, se), (a, b, corr_ret.loc[a, b])
