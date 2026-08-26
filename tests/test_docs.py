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
)


def test_pages_nav_is_paper_order():
    cfg = (ROOT / "_config.yml").read_text(encoding="utf-8")
    assert "just-the-docs" in cfg
    assert "jekyll-theme-cayman" not in cfg
    for gone in ("KIKU_RECIPE.md", "results.md", "examples.md"):
        assert gone not in cfg
        assert not (ROOT / gone).exists()
    assert not (ROOT / "superpowers").exists()
    cfg_l = cfg.lower()
    assert "package revamp" not in cfg_l
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
    for name in SECTIONS:
        assert name in text


def test_mathjax_and_sidebar_theme():
    head = (ROOT / "_includes" / "head_custom.html").read_text(encoding="utf-8")
    assert "mathjax" in head.lower()
    js = (ROOT / "assets" / "js" / "mathjax-script-type.js").read_text(encoding="utf-8")
    assert "math/tex" in js
    assert (ROOT / "_sass" / "color_schemes" / "kiku.scss").exists()


def test_section_pages_carry_her_equations():
    model = (ROOT / "model.md").read_text(encoding="utf-8")
    assert "M_{t+1}" in model or "m_{t+1}" in model
    assert r"\phi" in model or "phi" in model
    emp = (ROOT / "empirical.md").read_text(encoding="utf-8")
    assert "7.81" in emp and "13.88" in emp
    assert "Figure 1" in emp
    assert "In a nutshell" in (ROOT / "index.md").read_text(encoding="utf-8")
    for name in (
        "empirical.md",
        "model.md",
        "calibration.md",
        "implications.md",
        "installation.md",
        "api.md",
        "generalization.md",
    ):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "**In a nutshell.**" in text
    for name in ("empirical.md", "model.md", "calibration.md", "implications.md"):
        text = (ROOT / name).read_text(encoding="utf-8")
        assert "{: .why }" in text
        assert "{: .idea }" in text
        assert "{: .here }" in text
