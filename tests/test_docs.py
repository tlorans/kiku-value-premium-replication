from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs"

BOOK_PAGES = (
    "index.md",
    "getting-started.md",
    "financial-data.md",
    "long-run-risks-model.md",
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

    cf = _text("long-run-risks-model.md")
    assert "title: The long-run risks model" in cf
    assert "# The long-run risks model" in cf
    assert _parent("long-run-risks-model.md") is None
    assert _front_nav_order("long-run-risks-model.md") == 4

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
    assert "long-run-risks-model" in text
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
    assert "{{ '/model.html'" not in text


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
    assert "year_div" in text
    assert "real_rf_from_monthly" in text
    assert "consumption_growth_from_levels" in text
    assert "from lrrcs.model import" not in text
    assert "kiku_value_premium" not in text
    assert "time-series" in text
    assert "figures/consumption_growth.svg" in text
    assert "figures/market_dd_vs_dc.svg" in text
    assert "figures/market_log_pd.svg" in text
    assert "8.52" in text and "13.67" in text


MODEL_H2S = (
    "## The consumption process",
    "## The household",
    "## The security market line",
)


def test_long_run_risks_model_chapter():
    text = _text("long-run-risks-model.md")
    assert "title: The long-run risks model" in text
    assert "# The long-run risks model" in text
    assert _parent("long-run-risks-model.md") is None
    assert _front_nav_order("long-run-risks-model.md") == 4
    positions = [text.index(h) for h in MODEL_H2S]
    assert positions == sorted(positions)
    assert "## Consumption is not white noise" not in text
    assert "figures/consumption_growth.svg" not in text
    assert "M_{t+1}" in text or "m_{t+1}" in text
    assert "Bansal" in text
    assert "Epstein" in text
    assert "import lrrcs as lrr" in text
    assert "import polars as pl" in text
    assert "import plotnine as p9" in text
    assert "p9.ggplot" in text
    assert "capital-asset-pricing-model" in text
    assert "Lambda_eps" in text or "A_1" in text
    assert "figures/lrr_sml.svg" in text
    assert "figures/lrr_state.svg" in text
    assert "figures/lrr_consumption_paths.svg" in text
    assert "## Key takeaways" in text
    assert "## Exercises" in text
    assert "time-series" in text
    assert "cross-section" in text
    assert "8.56" not in text
    assert "13.88" not in text
    assert "cash-flows-then-prices" not in text
    assert "expected_growth_proxy" not in text
    assert "kalman_filter" not in text


MARKET_H2S = (
    "## Preparing the sample",
    "## Extract expected growth",
    "## One cash-flow exposure",
    "## Simulate cash flows",
    "## Solve and check returns and prices",
)


def test_market_chapter():
    text = _text("time-series.md")
    assert "title: The Time Series" in text
    assert "# The Time Series" in text
    assert _parent("time-series.md") is None
    assert _front_nav_order("time-series.md") == 5
    positions = [text.index(h) for h in MARKET_H2S]
    assert positions == sorted(positions)
    assert "## Data" not in text
    assert "## What long-run risk is" not in text
    assert "## Calibrate dividends" not in text
    assert "8.56" in text and "7.53" in text
    assert "expected_growth_proxy" in text
    assert "filter_expected_growth" in text
    assert "simulate_cashflow_moments" in text
    assert "compute_asset_pricing_moments" in text
    assert "import polars as pl" in text
    assert "import plotnine as p9" in text
    assert "p9.ggplot" in text
    assert "import lrrcs as lrr" in text
    assert "```python" in text
    assert "from lrrcs.model import" not in text
    assert "kiku_value_premium" not in text
    assert "Melin" not in text
    assert "other-risk-premia" not in text
    assert "cross-section" in text
    assert "figures/consumption_ma.svg" in text
    assert "figures/xt_proxy_filter.svg" in text
    assert "figures/market_log_pd.svg" in text
    assert "figures/market_dd_vs_ma.svg" in text
    assert "figures/sim_xt.svg" in text
    assert "figures/sim_dd.svg" in text
    assert "figures/sim_log_pd.svg" in text
    assert "0.722" in text
    assert "1.82" in text
    assert "Lambda_eps" in text
    assert "kalman_filter" in text
    assert "one_path" in text
    assert "# ... Kalman" not in text
    assert "## Key takeaways" in text
    assert "## Exercises" in text


TUTORIAL_FIGURES = (
    "consumption_growth.svg",
    "market_dd_vs_dc.svg",
    "market_log_pd.svg",
    "market_dd_vs_ma.svg",
    "consumption_ma.svg",
    "xt_proxy_filter.svg",
    "sim_xt.svg",
    "sim_dd.svg",
    "sim_log_pd.svg",
    "lrr_sml.svg",
    "lrr_state.svg",
    "lrr_consumption_paths.svg",
    "vg_spread.svg",
    "vg_log_pd.svg",
    "vg_dd_vs_ma.svg",
)


def test_tutorial_figures_exist():
    fig = ROOT / "figures"
    for name in TUTORIAL_FIGURES:
        path = fig / name
        assert path.is_file(), name
        assert path.stat().st_size > 500, name


CROSS_H2S = (
    "## Preparing the sample",
    "## Two cash-flow exposures",
    "## Elasticity of price–dividend to x_t",
    "## Solve and check rankings",
)


def test_value_versus_growth_chapter():
    text = _text("cross-section.md")
    assert "title: The Cross Section" in text
    assert "# The Cross Section" in text
    assert _parent("cross-section.md") is None
    assert _front_nav_order("cross-section.md") == 6
    positions = [text.index(h) for h in CROSS_H2S]
    assert positions == sorted(positions)
    assert "## Data" not in text
    assert "7.81" in text and "13.88" in text
    assert "5.3" in text
    assert "calibrate_from_data" in text
    assert "expected_growth_proxy" in text
    assert "compute_asset_pricing_moments" in text
    assert "```python" in text
    assert "import lrrcs as lrr" in text
    assert "import polars as pl" in text
    assert "import plotnine as p9" in text
    assert "p9.ggplot" in text
    assert "phi_hat" in text
    assert "capm_beta" in text
    assert "## Key takeaways" in text
    assert "## Exercises" in text
    assert "figures/vg_spread.svg" in text
    assert "figures/vg_log_pd.svg" in text
    assert "figures/vg_dd_vs_ma.svg" in text
    assert "figures/figure1.svg" not in text
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
    "cash-flows-then-prices.md",
)


def test_deleted_pages_gone():
    for name in DELETED:
        assert not (ROOT / name).exists(), name


def test_package_page_points_at_the_book():
    text = _text("package.md")
    assert "generalization" not in text
    assert "getting-started" in text or "time-series" in text or "long-run-risks-model" in text
    assert "financial-data" in text


def test_readme_matches_landing():
    text = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    assert text.startswith("# Long-run risks\n")
    assert "and the cross section" not in text.splitlines()[0]
    assert "six-step" not in text.lower() and "6-step" not in text.lower()
    assert "getting-started" in text
    assert "financial-data" in text
    assert "long-run-risks-model" in text
    assert "time-series" in text
    assert "cross-section" in text
    assert "other-risk-premia" not in text
    assert "climate.html" not in text
    assert "import lrrcs as lrr" in text


# Distinctive cores of Kiku (2006) introduction, used throughout the book.
C1 = "small but highly persistent component that governs consumption growth"
C2A = "time-variation in the conditional volatility"
C2B = "news about future economic uncertainty"
C3_VARIANTS = ("low- versus high-frequency", "low- and high-frequency")
C4A = "break the link"
C4B = "over time"
C4C = "across states"
C5 = "forward-looking return on the aggregate wealth"
C6A = "far into the future"
C6B = "sizable risk compensations"
C7 = "low-frequency risks embodied"
C8A = "highly exposed to long-run consumption shocks"
C8B = "short-lived fluctuations"
C9A = "higher elasticity of their price–dividend"
C9B = "high ex-ante compensation"


def _has_c3(text: str) -> bool:
    return any(v in text for v in C3_VARIANTS)


def _has_c4(text: str) -> bool:
    return C4A in text and C4B in text and C4C in text


def test_kiku_introduction_spine():
    home = _text("index.md")
    gs = _text("getting-started.md")
    fd = _text("financial-data.md")
    model = _text("long-run-risks-model.md")
    market = _text("time-series.md")
    vvg = _text("cross-section.md")
    readme = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    pkg = _text("package.md")
    api = _text("api.md")
    cfg = (ROOT / "_config.yml").read_text(encoding="utf-8")

    for page, text in (("index.md", home), ("long-run-risks-model.md", model)):
        assert C1 in text, page
        assert C2A in text, page
        assert C2B in text, page
        assert _has_c3(text), page
        assert _has_c4(text), page
        assert C5 in text, page
        assert C6A in text, page
        assert C6B in text, page
        assert C7 in text, page
        assert C8A in text, page
        assert C8B in text, page
        assert C9A in text, page
        assert C9B in text, page

    assert "## Introduction" not in home

    assert C1 in gs
    assert C2A in gs
    assert C2B in gs
    assert _has_c3(gs)
    assert _has_c4(gs)
    assert C5 in gs
    assert C6A in gs
    assert C6B in gs
    assert C8A in gs
    assert C9A in gs
    assert C9B in gs

    assert C1 in fd
    assert C2A in fd
    assert C2B in fd
    assert _has_c3(fd)
    assert C7 in fd
    assert C8A in fd
    assert C8B in fd
    assert C5 in fd

    assert C1 in market
    assert C2A in market
    assert C2B in market
    assert C5 in market
    assert C6A in market
    assert C6B in market
    assert C7 in market

    assert C7 in vvg
    assert C8A in vvg
    assert C8B in vvg
    assert C9A in vvg
    assert C9B in vvg
    assert C5 in vvg

    assert "small but highly persistent" in readme
    assert C2A in readme
    assert C2B in readme
    assert _has_c4(readme)
    assert C5 in readme
    assert C7 in readme
    assert C8A in readme
    assert C8B in readme
    assert C9A in readme
    assert C9B in readme

    assert C1 in pkg
    assert C7 in pkg
    assert C8A in pkg

    assert C7 in api
    assert C7 in cfg
    assert "calibrate cash flows" in cfg.lower()
