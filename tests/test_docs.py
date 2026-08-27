from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs"

BOOK_PAGES = (
    "index.md",
    "getting-started.md",
    "financial-data.md",
    "cash-flows-then-prices.md",
    "time-series.md",
    "cross-section.md",
    "package.md",
    "installation.md",
    "api.md",
)

PACKAGE_PAGES = ("installation.md", "api.md", "package.md")


def _text(name: str) -> str:
    return (ROOT / name).read_text(encoding="utf-8")


def _parent(name: str) -> str | None:
    for line in _text(name).splitlines()[:12]:
        if line.startswith("parent:"):
            return line.split(":", 1)[1].strip()
    return None


def _front_nav_order(name: str) -> int | None:
    for line in _text(name).splitlines()[:12]:
        if line.startswith("nav_order:"):
            return int(line.split(":", 1)[1].strip())
    return None


def test_just_the_docs_and_title():
    cfg = (ROOT / "_config.yml").read_text(encoding="utf-8")
    assert "just-the-docs" in cfg
    assert "title: Long-run risks\n" in cfg
    assert "and the cross section" not in cfg
    assert "calibrate cash flows" in cfg.lower()
    assert "superpowers" in cfg


def test_book_pages_exist():
    for name in BOOK_PAGES:
        assert (ROOT / name).is_file(), name
    assert not (ROOT / "recipe.md").exists()


def test_new_chapter_front_matter():
    gs = _text("getting-started.md")
    assert "title: Getting started" in gs
    assert "# Getting started" in gs
    assert _parent("getting-started.md") is None
    assert _front_nav_order("getting-started.md") == 2

    fd = _text("financial-data.md")
    assert "title: Financial data" in fd
    assert "# Financial data" in fd
    assert _parent("financial-data.md") is None
    assert _front_nav_order("financial-data.md") == 3

    cf = _text("cash-flows-then-prices.md")
    assert "title: Cash flows, then prices" in cf
    assert "# Cash flows, then prices" in cf
    assert _parent("cash-flows-then-prices.md") is None
    assert _front_nav_order("cash-flows-then-prices.md") == 4

    assert _parent("time-series.md") is None
    assert _front_nav_order("time-series.md") == 5
    assert _parent("cross-section.md") is None
    assert _front_nav_order("cross-section.md") == 6
    assert _front_nav_order("package.md") == 7
    assert _parent("installation.md") == "Package"
    assert _parent("api.md") == "Package"


def test_mathjax_and_sidebar_theme():
    head = (ROOT / "_includes" / "head_custom.html").read_text(encoding="utf-8")
    assert "mathjax" in head.lower()
    js = (ROOT / "assets" / "js" / "mathjax-script-type.js").read_text(encoding="utf-8")
    assert "math/tex" in js
    assert (ROOT / "_sass" / "color_schemes" / "kiku.scss").exists()


def test_package_pages_are_tidyfinance_companion():
    for name in PACKAGE_PAGES:
        text = _text(name)
        assert "import tidyfinance as tf" in text
        assert "import lrrcs as lrr" in text
        assert "kiku_value_premium" not in text
        assert "connect_wrds" not in text
        assert "from lrrcs.model import" not in text
        assert "from lrrcs.empirical import" not in text
    readme = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    assert "import lrrcs as lrr" in readme
    assert "tidyfinance" in readme
    assert "kiku_value_premium" not in readme


def test_code_fences_use_flat_lrr():
    for name in BOOK_PAGES:
        text = _text(name)
        if "```python" not in text:
            continue
        assert "kiku_value_premium" not in text
        assert "from lrrcs.model import" not in text
        assert "from lrrcs.empirical import" not in text
        assert "from lrrcs.calibration import" not in text
        assert "from lrrcs.implications import" not in text
        assert "print_value_premium" not in text
        assert "lrr." in text or "import lrrcs as lrr" in text


def test_home_is_landing():
    text = _text("index.md")
    assert "# Long-run risks" in text
    assert "## Introduction" not in text
    assert "I show" not in text
    assert "Start here" in text
    assert "getting-started" in text
    assert "financial-data" in text
    assert "cash-flows-then-prices" in text
    assert "time-series" in text
    assert "cross-section" in text
    assert "```python" in text
    assert "import tidyfinance as tf" in text
    assert "import lrrcs as lrr" in text
    assert "print_long_short_premium" in text
    for stem in (
        "empirical",
        "calibration",
        "implications",
        "climate",
        "further",
        "other-risk-premia",
        "generalization",
        "replica",
    ):
        assert f"{stem}.html" not in text
        assert f"{stem}.md" not in text
    assert "model.html" not in text


def test_getting_started():
    text = _text("getting-started.md")
    assert "uv pip install -e ." in text
    assert "import tidyfinance as tf" in text
    assert "import lrrcs as lrr" in text
    assert "solve_analytical" in text
    assert "financial-data" in text
    assert "set_wrds_credentials" not in text
    assert "What that did not" in text


def test_financial_data_chapter():
    text = _text("financial-data.md")
    assert "title: Financial data" in text
    assert "# Financial data" in text
    assert _parent("financial-data.md") is None
    assert _front_nav_order("financial-data.md") == 3
    assert "accessing-and-managing-financial-data" in text
    assert "wrds-crsp-and-compustat" in text
    assert "data/consumption_annual.csv" in text
    assert "data/annual_panel.csv" in text
    assert "data/rf_annual.csv" in text
    assert "import polars as pl" in text
    assert "import plotnine as p9" in text
    assert "import tidyfinance as tf" in text
    assert "import lrrcs as lrr" in text
    assert "load_consumption" in text
    assert "campbell_shiller_annual" in text
    assert "build_annual_panel" in text
    assert "DNDGRA3A086NBEA" in text
    assert "fredgraph.csv" in text
    assert "retx" in text
    assert "Historical_BE_Data" in text
    assert "real_rf_from_monthly" in text
    assert "consumption_growth_from_levels" in text
    assert "from lrrcs.model import" not in text
    assert "kiku_value_premium" not in text
    assert "time-series" in text
    assert "figures/consumption_growth.svg" in text
    assert "figures/market_dd_vs_dc.svg" in text
    assert "figures/market_log_pd.svg" in text
    assert "8.52" in text and "13.67" in text


def test_cash_flows_then_prices():
    text = _text("cash-flows-then-prices.md")
    assert "Calibrate cash flows" in text
    assert "Compare pricing moments" in text
    assert "M_{t+1}" in text or "m_{t+1}" in text
    assert "import tidyfinance as tf" in text
    assert "import lrrcs as lrr" in text
    assert "get_table_ii_params" in text
    assert "calibrate_from_data" in text
    assert "compute_asset_pricing_moments" in text or "print_long_short_premium" in text
    assert "time-series" in text
    assert "cross-section" in text
    assert "8.56" not in text
    assert "13.88" not in text


MARKET_H2S = (
    "## What long-run risk is",
    "## Estimate x_t",
    "## Calibrate dividends",
    "## Simulate cash flows",
    "## Solve and check returns and prices",
)


def test_market_chapter():
    text = _text("time-series.md")
    assert "title: The market" in text
    assert "# The market" in text
    assert _parent("time-series.md") is None
    assert _front_nav_order("time-series.md") == 5
    positions = [text.index(h) for h in MARKET_H2S]
    assert positions == sorted(positions)
    assert "## Data" not in text
    assert "8.56" in text and "7.53" in text
    assert "expected_growth_proxy" in text
    assert "filter_expected_growth" in text
    assert "simulate_cashflow_moments" in text
    assert "compute_asset_pricing_moments" in text
    assert "import polars as pl" in text
    assert "import plotnine as p9" in text
    assert "import lrrcs as lrr" in text
    assert "```python" in text
    assert "from lrrcs.model import" not in text
    assert "kiku_value_premium" not in text
    assert "Melin" not in text
    assert "other-risk-premia" not in text
    assert "cross-section" in text
    assert "figures/consumption_ma.svg" in text
    assert "figures/xt_proxy_filter.svg" in text
    assert "figures/sim_xt.svg" in text
    assert "figures/sim_dd.svg" in text
    assert "figures/sim_log_pd.svg" in text
    assert "0.722" in text
    assert "1.82%" in text
    assert "Lambda_eps" in text


TUTORIAL_FIGURES = (
    "consumption_growth.svg",
    "market_dd_vs_dc.svg",
    "market_log_pd.svg",
    "consumption_ma.svg",
    "xt_proxy_filter.svg",
    "sim_xt.svg",
    "sim_dd.svg",
    "sim_log_pd.svg",
)


def test_tutorial_figures_exist():
    fig = ROOT / "figures"
    for name in TUTORIAL_FIGURES:
        path = fig / name
        assert path.is_file(), name
        assert path.stat().st_size > 500, name


def test_value_versus_growth_chapter():
    text = _text("cross-section.md")
    assert "title: Value versus growth" in text
    assert "# Value versus growth" in text
    assert _parent("cross-section.md") is None
    assert _front_nav_order("cross-section.md") == 6
    h2s = (
        "## Data",
        "## Calibrate cash flows",
        "## Solve",
        "## Compare pricing moments",
    )
    positions = [text.index(h) for h in h2s]
    assert positions == sorted(positions)
    assert "7.81" in text and "13.88" in text
    assert "5.3" in text
    assert "calibrate_from_data" in text
    assert "```python" in text
    assert "import lrrcs as lrr" in text
    assert "other-risk-premia" not in text
    assert "climate.html" not in text


DELETED = (
    "empirical.md",
    "model.md",
    "calibration.md",
    "implications.md",
    "other-risk-premia.md",
    "climate.md",
    "further.md",
    "generalization.md",
    "replica.md",
    "value.md",
    "recipe.md",
)


def test_deleted_pages_gone():
    for name in DELETED:
        assert not (ROOT / name).exists(), name


def test_package_page_points_at_the_book():
    text = _text("package.md")
    assert "generalization" not in text
    assert "getting-started" in text or "time-series" in text or "cash-flows-then-prices" in text
    assert "financial-data" in text


def test_readme_matches_landing():
    text = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    assert text.startswith("# Long-run risks\n")
    assert "and the cross section" not in text.splitlines()[0]
    assert "six-step" not in text.lower() and "6-step" not in text.lower()
    assert "getting-started" in text
    assert "financial-data" in text
    assert "cash-flows-then-prices" in text
    assert "time-series" in text
    assert "cross-section" in text
    assert "other-risk-premia" not in text
    assert "climate.html" not in text
    assert "import lrrcs as lrr" in text
