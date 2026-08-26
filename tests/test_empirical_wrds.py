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
