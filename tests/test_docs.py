from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs"

BOOK_PAGES = (
    "index.md",
    "getting-started.md",
    "long-run-risks-model.md",
    "measuring-leverage.md",
    "time-series.md",
    "two-free-numbers.md",
    "cross-section.md",
    "price-your-own-claim.md",
    "package.md",
    "installation.md",
    "api.md",
    "financial-data.md",
    "objections.md",
    "background.md",
    "references.md",
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
    assert "superpowers" in cfg


def test_book_pages_exist():
    for name in BOOK_PAGES:
        assert (ROOT / name).is_file(), name
    assert not (ROOT / "recipe.md").exists()


def test_argument_nav_order():
    assert _parent("getting-started.md") is None
    assert _front_nav_order("getting-started.md") == 2
    assert _parent("long-run-risks-model.md") is None
    assert _front_nav_order("long-run-risks-model.md") == 3
    assert _parent("measuring-leverage.md") is None
    assert _front_nav_order("measuring-leverage.md") == 4
    assert _parent("time-series.md") is None
    assert _front_nav_order("time-series.md") == 5
    assert _parent("two-free-numbers.md") is None
    assert _front_nav_order("two-free-numbers.md") == 6
    assert _parent("cross-section.md") is None
    assert _front_nav_order("cross-section.md") == 7
    assert _parent("price-your-own-claim.md") is None
    assert _front_nav_order("price-your-own-claim.md") == 8
    assert _front_nav_order("package.md") == 9
    assert _parent("installation.md") == "Package"
    assert _parent("api.md") == "Package"
    assert _parent("financial-data.md") == "Package"
    assert _parent("objections.md") is None
    assert _front_nav_order("objections.md") == 10
    assert _parent("background.md") is None
    assert _front_nav_order("background.md") == 11
    assert _parent("references.md") is None
    assert _front_nav_order("references.md") == 12


def test_mathjax_and_sidebar_theme():
    head = (ROOT / "_includes" / "head_custom.html").read_text(encoding="utf-8")
    assert "mathjax" in head.lower()
    js = (ROOT / "assets" / "js" / "mathjax-script-type.js").read_text(encoding="utf-8")
    assert "math/tex" in js
    assert (ROOT / "_sass" / "color_schemes" / "kiku.scss").exists()


BANNED_PROSE = (
    "Tidy Finance",
    "tidy-finance.org",
    "tidyfinance.org",
    "follow-along",
    "companion to",
)


def test_no_tidyfinance_branding():
    for name in BOOK_PAGES:
        text = _text(name)
        for banned in BANNED_PROSE:
            assert banned not in text, f"{name}: {banned}"
    readme = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    for banned in BANNED_PROSE:
        assert banned not in readme, f"README.md: {banned}"


def test_package_pages():
    for name in PACKAGE_PAGES:
        text = _text(name)
        assert "import lrrcs as lrr" in text
        assert "kiku_value_premium" not in text
        assert "connect_wrds" not in text
        assert "from lrrcs.model import" not in text
        assert "from lrrcs.empirical import" not in text
    assert "import tidyfinance as tf" in _text("installation.md")
    assert "import tidyfinance as tf" in _text("api.md")
    assert "set_wrds_credentials" in _text("installation.md")
    readme = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    assert "import lrrcs as lrr" in readme
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
    assert "Run the experiment" in text
    assert "getting-started" in text
    assert "financial-data" in text
    assert "long-run-risks-model" in text
    assert "measuring-leverage" in text
    assert "time-series" in text
    assert "cross-section" in text
    assert "```python" in text
    assert "import lrrcs as lrr" in text
    assert "print_long_short_premium" in text
    assert "5.3" in text
    assert "0.92" in text
    assert "figures/lrr_sml.svg" in text
    assert "## The argument" in text
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


def test_dcf_to_ge_arc():
    home = _text("index.md")
    gs = _text("getting-started.md")
    for text, page in ((home, "index.md"), (gs, "getting-started.md")):
        assert "discount rate" in text, page
        assert "cash flow" in text, page
    # Hero copy (REWRITE_PLAN Issue 1) carries the motto inside the verbatim
    # sentence "average returns never enter the estimation".
    assert "average returns never enter the estimation" in home.lower()
    assert "consumption" in gs


def test_home_spine():
    """Issue 1: tagline under the title, verbatim hero, scoping line after the table."""
    text = _text("index.md")
    assert "Valuations and risk premia depend on the amount of low-frequency risks embodied in cash flows." in text
    # Hero sentence; "DCF" carries the link to Two free numbers (Issue 4).
    assert "takes a cash-flow forecast from one model and a discount rate from another." in text
    assert "[DCF]({{ '/two-free-numbers.html' | relative_url }})" in text
    assert "The claim is not that this model is true." in text
    # Tagline must not appear twice (promoted from footer in Issue 1).
    assert text.count(
        "Valuations and risk premia depend on the amount of low-frequency risks embodied in cash flows."
    ) == 1
    cfg = (ROOT / "_config.yml").read_text(encoding="utf-8")
    assert "low-frequency risks" not in cfg.split("footer_content:", 1)[1].split("\n", 1)[0]
    assert "MIT License" in cfg


FIREWALL_LINES = (
    "**Where each number comes from**",
    "Table II parameters — aggregate consumption moments only",
    "Cash-flow loadings — dividends regressed on a two-year moving average of consumption; no returns",
    "Returns — validation only, never fitted",
    "Returns appear once, at the end, as the thing to be explained.",
)


def test_firewall_callout_on_home_and_measuring():
    """Issue 3: the estimation firewall renders on both pages, content verbatim."""
    for name in ("index.md", "measuring-leverage.md"):
        text = _text(name)
        assert 'class="firewall"' in text, name
        for line in FIREWALL_LINES:
            assert line in text, f"{name}: {line[:40]}"


TFN_H2S = ("## A. One rate for everything", "## B. A rate fitted to the CAPM", "## C. A forecast is not a valuation")


def test_two_free_numbers_page():
    """Issue 4: three panels; every number printed by examples/dcf_counterfactual.py."""
    text = _text("two-free-numbers.md")
    assert "# Two free numbers" in text
    positions = [text.index(h) for h in TFN_H2S]
    assert positions == sorted(positions)
    for snippet in (
        "the premium prices at 0.00",
        "The data say six points.",
        "ratio 0.56",
        "a DCF has no slot",
        "6.04 to 7.07",
        "88.9 to 108.2",
        "0.80 to 0.97",
        "The difference is the premium.",
        "dcf_counterfactual.py",
    ):
        assert snippet in text, snippet


def test_price_your_own_claim_page():
    """Issue 5: recipe, exact script table, runnable snippet, forward link."""
    text = _text("price-your-own-claim.md")
    assert "# Price your own claim" in text
    # Recipe, verbatim (plan Issue 5).
    assert "Bring a dividend process. The model returns the price-dividend ratio" in text
    assert "never from returns" in text
    # Table = exact examples/two_firms.py output.
    for row in (
        "A        0.5    -3.0         -0.03      3.20      6.89",
        "B        1.5    15.2          0.14      3.32      7.01",
    ):
        assert row in text, row
    assert "two_firms.py" in text
    # Snippet runs the public entry point; single forward link to Installation.
    assert "lrr.price_from_loadings(phi)" in text
    assert "installation.html" in text
    # No audience speculation (plan: synthetic firms, full stop).
    for banned in ("use this for", "use it for", "practitioners", "analysts", "CFO"):
        assert banned not in text, banned


GS_H2S = (
    "## Two numbers you made up",
    "## One process instead",
    "## An economy in five lines",
    "## What if the loadings are equal",
    "## Key takeaways",
)


def test_getting_started():
    text = _text("getting-started.md")
    assert "title: The result" in text
    assert "# The result" in text
    positions = [text.index(h) for h in GS_H2S]
    assert positions == sorted(positions)
    assert "uv pip install -e ." in text
    assert "import lrrcs as lrr" in text
    assert "solve_analytical" in text
    assert "long-run-risks-model" in text
    assert "set_wrds_credentials" not in text
    assert "What that did not" in text
    assert "r - g" in text or "r-g" in text
    assert "5.3" in text
    assert "0.92" in text
    assert 'dividends["value"].phi = 2.6' in text


def test_financial_data_chapter():
    text = _text("financial-data.md")
    assert "title: Financial data" in text
    assert "# Financial data" in text
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
    assert "cash-flow side" in text
    assert "discount-rate side" in text


MODEL_H2S = (
    "## The consumption process",
    "## The household",
    "## Compensation versus cash-flow leverage",
)


def test_long_run_risks_model_chapter():
    text = _text("long-run-risks-model.md")
    assert "title: The long-run risks model" in text
    assert "# The long-run risks model" in text
    assert _parent("long-run-risks-model.md") is None
    assert _front_nav_order("long-run-risks-model.md") == 3
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
    assert "Lambda_eps" in text or "A_1" in text
    assert "figures/lrr_sml.svg" in text
    assert "figures/lrr_state.svg" in text
    assert "figures/lrr_consumption_paths.svg" in text
    assert "## Key takeaways" in text
    assert "## Exercises" in text
    assert "measuring-leverage" in text
    assert "8.56" not in text
    assert "13.88" not in text
    assert "cash-flows-then-prices" not in text
    assert "expected_growth_proxy" not in text
    assert "kalman_filter" not in text


MEASURE_H2S = (
    "## The two-year MA",
    "## Equation (19)",
    "## Key takeaways",
    "## Exercises",
)


def test_measuring_leverage_chapter():
    text = _text("measuring-leverage.md")
    assert "title: Measuring leverage" in text
    assert "# Measuring leverage" in text
    assert _parent("measuring-leverage.md") is None
    positions = [text.index(h) for h in MEASURE_H2S]
    assert positions == sorted(positions)
    assert "expected_growth_proxy" in text
    assert "calibrate_from_data" in text
    assert "phi_hat" in text
    assert "0.722" in text
    assert "12.129" in text
    assert "import lrrcs as lrr" in text
    assert "import polars as pl" in text
    assert "p9.ggplot" in text
    assert "figures/consumption_ma.svg" in text
    assert "figures/vg_dd_vs_ma.svg" in text
    assert "figures/market_dd_vs_ma.svg" in text
    assert "kiku_value_premium" not in text
    assert "from lrrcs.model import" not in text
    assert "time-series" in text


MARKET_H2S = (
    "## Preparing the sample",
    "## The loadings are already measured",
    "## Simulate cash flows",
    "## Solve and check returns and prices",
    "## Appendix: extracting",
)


def test_market_chapter():
    text = _text("time-series.md")
    assert "title: Does the market still fit?" in text
    assert "# Does the market still fit?" in text
    assert _parent("time-series.md") is None
    assert _front_nav_order("time-series.md") == 5
    positions = [text.index(h) for h in MARKET_H2S]
    assert positions == sorted(positions)
    assert "8.56" in text and "7.53" in text
    assert "expected_growth_proxy" in text
    assert "filter_expected_growth" in text
    assert "simulate_cashflow_moments" in text
    assert "compute_asset_pricing_moments" in text
    assert "import lrrcs as lrr" in text
    assert "0.722" in text
    assert "kalman_filter" in text
    assert "one_path" in text
    assert "wrong price\u2013dividend ratio is a fail" in text
    # Issue 2 framing sentence (meaning pinned by REWRITE_PLAN).
    assert "This comes before the cross-section on purpose." in text
    assert "never re-tune it" in text
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
    "## The loadings are already measured",
    "## Elasticity of price\u2013dividend to x_t",
    "## Solve and check rankings",
)


def test_value_versus_growth_chapter():
    text = _text("cross-section.md")
    assert "title: Value versus growth" in text
    assert "# Value versus growth" in text
    positions = [text.index(h) for h in CROSS_H2S]
    assert positions == sorted(positions)
    assert "7.81" in text and "13.88" in text
    assert "5.3" in text
    assert "calibrate_from_data" in text
    assert "phi_hat" in text
    assert "capm_beta" in text
    assert "0.92" in text
    assert "nothing about the household changes" in text.lower()
    assert "figures/vg_spread.svg" in text
    assert "figures/vg_log_pd.svg" in text
    assert "figures/vg_dd_vs_ma.svg" in text


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
    assert "measuring-leverage" in text


def test_readme_matches_landing():
    text = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    assert text.startswith("# Long-run risks\n")
    assert "and the cross section" not in text.splitlines()[0]
    assert "six-step" not in text.lower() and "6-step" not in text.lower()
    assert "getting-started" in text
    assert "financial-data" in text
    assert "long-run-risks-model" in text
    assert "measuring-leverage" in text
    assert "time-series" in text
    assert "cross-section" in text
    assert "other-risk-premia" not in text
    assert "climate.html" not in text
    assert "import lrrcs as lrr" in text
    assert "discount rate" in text
    assert "Average returns never enter" in text


GLOSSARY_TERMS = (
    "loading", "persistent component", "P/D ratio", "beta", "EIS",
    "risk aversion", "Euler equation", "cash-flow news", "discount-rate news", "Table II",
)


def test_background_and_references_pages():
    """Issues 9+10: three primers with links back; glossary; canonical citations."""
    bg = _text("background.md")
    for primer in (
        "## Epstein-Zin preferences",
        "## The long-run risks model",
        "## Why the CAPM misses low-frequency risk",
    ):
        assert primer in bg, primer
    for term in GLOSSARY_TERMS:
        assert term in bg, term
    refs = _text("references.md")
    for citation in (
        "Kiku, D., 2006",
        "Bansal, R., and A. Yaron, 2004",
        "Epstein, L. G., and S. E. Zin, 1989",
        "Hansen, L. P., and R. Jagannathan, 1991",
    ):
        assert citation in refs, citation
    # No 'Bansal & Yarn' typo.
    assert "Yarn" not in refs
