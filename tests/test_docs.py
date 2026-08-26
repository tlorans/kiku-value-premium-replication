from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs"
SECTIONS = (
    "empirical.md",
    "model.md",
    "calibration.md",
    "implications.md",
    "installation.md",
    "api.md",
    "generalization.md",
    "further.md",
    "climate.md",
    "cross-section.md",
    "package.md",
    "time-series.md",
    "value.md",
    "other-risk-premia.md",
)


def test_pages_nav_is_paper_order():
    cfg = (ROOT / "_config.yml").read_text(encoding="utf-8")
    assert "just-the-docs" in cfg
    for gone in ("KIKU_RECIPE.md", "results.md", "examples.md"):
        assert gone not in cfg
        assert not (ROOT / gone).exists()
    orders = []
    for name in ("empirical.md", "model.md", "calibration.md", "implications.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "nav_order:" in text
        for line in text.splitlines()[:8]:
            if line.startswith("nav_order:"):
                orders.append(int(line.split(":")[1].strip()))
    assert orders == sorted(orders)


def test_readme_does_not_host_six_step_recipe():
    text = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    assert "6-step" not in text.lower() and "six-step" not in text.lower()


def test_index_links_recipe_pages():
    text = (ROOT / "index.md").read_text(encoding="utf-8")
    stems = [name.replace(".md", "") for name in SECTIONS]
    for stem in stems:
        assert stem in text
    assert "replica.md" not in text


def test_introduction_is_macro_finance():
    index = (ROOT / "index.md").read_text(encoding="utf-8")
    assert "Cochrane" in index
    assert "Mehra" in index or "Prescott" in index
    assert "Bansal" in index and "Yaron" in index
    assert "overlooked" in index.lower()
    assert "I consider" in index or "I show" in index or "I introduce" in index


def test_other_risk_premia_nav_page():
    text = (ROOT / "other-risk-premia.md").read_text(encoding="utf-8")
    assert "title: Other risk premia" in text
    assert "nav_order: 4" in text
    assert "RMW" in text and "CMA" in text and "SMB" in text
    assert "```python" in text


def test_time_series_page_is_the_market():
    text = (ROOT / "time-series.md").read_text(encoding="utf-8")
    assert "# Time series" in text
    assert "8.56" in text and "7.53" in text
    assert "M_{t+1}" in text or "m_{t+1}" in text
    assert "```python" in text


def test_cross_section_page_is_value():
    text = (ROOT / "cross-section.md").read_text(encoding="utf-8")
    assert "# Cross section" in text
    assert "7.81" in text and "13.88" in text
    assert "5.3" in text
    assert "```python" in text
    assert "calibrate_from_data" in text


def test_nav_is_by_object():
    def parent_of(name):
        for line in (ROOT / name).read_text(encoding="utf-8").splitlines()[:8]:
            if line.startswith("parent:"):
                return line.split(":", 1)[1].strip()
        return None
    assert parent_of("time-series.md") is None
    assert parent_of("cross-section.md") is None
    assert parent_of("other-risk-premia.md") is None
    assert parent_of("installation.md") == "Package"


def test_mathjax_and_sidebar_theme():
    head = (ROOT / "_includes" / "head_custom.html").read_text(encoding="utf-8")
    assert "mathjax" in head.lower()
    js = (ROOT / "assets" / "js" / "mathjax-script-type.js").read_text(encoding="utf-8")
    assert "math/tex" in js
    assert (ROOT / "_sass" / "color_schemes" / "kiku.scss").exists()


def test_site_is_the_paper_not_a_tutorial():
    index = (ROOT / "index.md").read_text(encoding="utf-8")
    assert "# Is the Value Premium a Puzzle?" in index
    assert "## Abstract" in index
    assert "## 1. Introduction" in index
    banned = (
        "landlord",
        "shiny new building",
        "rainy Tuesday",
        "weather model",
        "**Check.**",
        "If you are lost, start here",
    )
    blob = "\n".join((ROOT / name).read_text(encoding="utf-8") for name in ("index.md",) + SECTIONS[:4])
    for phrase in banned:
        assert phrase.lower() not in blob.lower()


def test_section_pages_carry_her_equations():
    model = (ROOT / "model.md").read_text(encoding="utf-8")
    assert "M_{t+1}" in model or "m_{t+1}" in model
    emp = (ROOT / "empirical.md").read_text(encoding="utf-8")
    assert "7.81" in emp and "13.88" in emp
    cal = (ROOT / "calibration.md").read_text(encoding="utf-8")
    assert "6.2" in cal and "2.6" in cal
    impl = (ROOT / "implications.md").read_text(encoding="utf-8")
    assert "5.3" in impl
    for name in ("empirical.md", "model.md", "calibration.md", "implications.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "```python" in text


def test_further_applications_page():
    text = (ROOT / "further.md").read_text(encoding="utf-8")
    assert "RMW" in text and "CMA" in text
    assert "calibrate_from_data" in text


def test_climate_risk_premia_page():
    text = (ROOT / "climate.md").read_text(encoding="utf-8")
    assert "Melin" in text and "Zhang" in text
    assert "long=" in text and "short=" in text
    assert "calibrate_from_data" in text
