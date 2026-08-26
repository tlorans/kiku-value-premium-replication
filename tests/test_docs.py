from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "docs"


def test_pages_nav_is_paper_order():
    cfg = (ROOT / "_config.yml").read_text(encoding="utf-8")
    for name in ("empirical.md", "model.md", "calibration.md", "implications.md"):
        assert name in cfg
    for gone in ("KIKU_RECIPE.md", "results.md", "examples.md"):
        assert gone not in cfg
        assert not (ROOT / gone).exists()


def test_readme_does_not_host_six_step_recipe():
    text = (ROOT.parent / "README.md").read_text(encoding="utf-8")
    assert "6-step" not in text.lower() and "six-step" not in text.lower()
