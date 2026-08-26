from pathlib import Path
import numpy as np
import pandas as pd
from kiku_value_premium.empirical.goldens import (
    END,
    START,
    TABLE_I,
    TABLE_I_CORR_DG,
    TABLE_I_CORR_RET,
    TABLE_III_DATA,
    TABLE_VI_INNOV,
    TABLE_VI_PHI,
)
from kiku_value_premium.empirical.tables import table_i, table_i_corr, table_vi_data, within_se

ROOT = Path(__file__).resolve().parents[1]
PANEL = ROOT / "data" / "annual_panel.csv"
DC = ROOT / "data" / "consumption_annual.csv"


def _panel():
    assert PANEL.exists(), "run build_annual_panel(refresh=True) first"
    return pd.read_csv(PANEL)


def test_table_i_within_printed_se():
    bm = _panel()
    tab = table_i(bm, START, END).set_index("claim")
    # table_i stores E[R], σ(R), E[Δd], σ(Δd) in percent; log(P/D) in logs.
    for claim, stats in TABLE_I.items():
        for name, (printed, se) in stats.items():
            val = float(tab.loc[claim, name])
            assert within_se(val, printed, se), f"{claim} {name}: {val} vs {printed} ({se})"


def test_table_i_correlations_within_se():
    bm = _panel()
    corr_ret, corr_dg = table_i_corr(bm, START, END)
    for (a, b), (printed, se) in TABLE_I_CORR_RET.items():
        assert within_se(float(corr_ret.loc[a, b]), printed, se), (a, b, corr_ret.loc[a, b])
    for (a, b), (printed, se) in TABLE_I_CORR_DG.items():
        assert within_se(float(corr_dg.loc[a, b]), printed, se), (a, b, corr_dg.loc[a, b])


def test_table_iii_consumption_within_se():
    dc = pd.read_csv(DC).set_index("year")["dc"]
    x = dc.loc[START:END].to_numpy() * 100.0
    from kiku_value_premium.empirical.tables import newey_west_mean, sd_and_se
    mu, se_mu = newey_west_mean(x, lags=8)
    sd, se_sd = sd_and_se(x, lags=8)
    ac1 = float(np.corrcoef(x[1:], x[:-1])[0, 1])
    ac2 = float(np.corrcoef(x[2:], x[:-2])[0, 1])
    assert within_se(mu, *TABLE_III_DATA["mean"])
    assert within_se(sd, *TABLE_III_DATA["sd"])
    assert within_se(ac1, *TABLE_III_DATA["ac1"])
    assert within_se(ac2, *TABLE_III_DATA["ac2"])


def test_table_vi_within_se():
    bm = _panel()
    dc = pd.read_csv(DC).set_index("year")["dc"]
    tab = table_vi_data(bm, dc, START, END).set_index("claim")
    for claim, (printed, se) in TABLE_VI_PHI.items():
        assert within_se(float(tab.loc[claim, "phi_tilde"]), printed, se), claim
    for claim, (printed, se) in TABLE_VI_INNOV.items():
        assert within_se(float(tab.loc[claim, "innov_corr"]), printed, se), claim
