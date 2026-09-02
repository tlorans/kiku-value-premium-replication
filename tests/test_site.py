"""Structural lint for the Quarto site (site/).

Execution correctness is enforced by `quarto render` itself (cells run
at build time), so these tests only pin what a render does not check:
sidebar completeness, legacy-URL redirect coverage, leftover Jekyll
syntax, course furniture, and freeze coverage (CI renders from the
committed freeze and must never silently skip an executed page).
"""
from pathlib import Path

import pytest
import re
import yaml

SITE = Path(__file__).resolve().parents[1] / "site"

# Every page of the legacy Jekyll site must remain reachable.
LEGACY_URLS = {
    "/getting-started.html",
    "/long-run-risks-model.html",
    "/measuring-leverage.html",
    "/time-series.html",
    "/two-free-numbers.html",
    "/cross-section.html",
    "/price-your-own-claim.html",
    "/package.html",
    "/installation.html",
    "/api.html",
    "/financial-data.html",
    "/objections.html",
    "/background.html",
    "/references.html",
}


def _sidebar_entries():
    config = yaml.safe_load((SITE / "_quarto.yml").read_text(encoding="utf-8"))
    entries = []

    def walk(items):
        for item in items:
            if isinstance(item, str):
                entries.append(item)
            elif isinstance(item, dict) and "contents" in item:
                walk(item["contents"])

    walk(config["website"]["sidebar"]["contents"])
    return entries


def _qmd_files():
    return [p for p in SITE.rglob("*.qmd") if "_site" not in p.parts]


def _front_matter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.S)
    return yaml.safe_load(match.group(1)) if match else {}


def test_sidebar_entries_exist():
    for entry in _sidebar_entries():
        assert (SITE / entry).exists(), f"sidebar entry missing on disk: {entry}"


def test_every_page_in_sidebar():
    listed = set(_sidebar_entries())
    for path in _qmd_files():
        rel = path.relative_to(SITE).as_posix()
        assert rel in listed, f"page not in sidebar: {rel}"


def test_every_page_has_title():
    for path in _qmd_files():
        assert _front_matter(path).get("title"), f"missing title: {path.name}"


def test_legacy_urls_covered_by_aliases():
    covered = set()
    for path in _qmd_files():
        for alias in _front_matter(path).get("aliases", []) or []:
            covered.add(alias)
    missing = LEGACY_URLS - covered
    assert not missing, f"legacy URLs without an alias: {sorted(missing)}"


def test_no_jekyll_residue():
    patterns = ("relative_url", "{: .", "\\\\(", "{{ site.")
    for path in _qmd_files():
        text = path.read_text(encoding="utf-8")
        for pat in patterns:
            assert pat not in text, f"Jekyll residue {pat!r} in {path.name}"


def test_no_course_furniture():
    """The site is a library, not a syllabus."""
    banned = (
        "How to read this course",
        "## Takeaways",
        "Check yourself",
        "Part I —",
        "Part II —",
        "this course",
        "this chapter",
    )
    offenders = {}
    for path in _qmd_files():
        text = path.read_text(encoding="utf-8")
        hits = [s for s in banned if s in text]
        if hits:
            offenders[path.relative_to(SITE).as_posix()] = hits
    assert not offenders, f"course furniture still on the site: {offenders}"


def test_no_chapters_directory():
    assert not (SITE / "chapters").exists()
    assert not (SITE / "how-to-read.qmd").exists()


def test_freeze_covers_every_executed_page():
    freeze = SITE / "_freeze"
    for path in _qmd_files():
        if "```{python}" not in path.read_text(encoding="utf-8"):
            continue
        rel = path.relative_to(SITE).with_suffix("")
        entry = freeze / rel / "execute-results"
        assert entry.exists(), (
            f"executed page has no freeze entry (CI would fail or skip): "
            f"{rel.as_posix()}"
        )


# Names removed from the public API. They must not survive anywhere the
# reader can see them, prose included.
REMOVED_API_NAMES = (
    r"\blrrcs\b",
    r"\.value_premium",
    r"\.long_short_premium",
    r"\.legs\b",
    "from_cashflows",
    "LongRunRisksModel.from_loading",
    "calibrate_from_data",
    "DividendParams",
    "resolve_legs",
    "get_table_ii_dividends",
    r"\.dividends\b",
    "ModelSolver",
    "solve_analytical",
    "simulate_table_vii",
    "compute_asset_pricing_moments",
    "get_table_ii_params",
    "get_default_params",
    "price_from_loadings",
    "print_long_short_premium",
    "print_asset_pricing_moments",
    "print_table_vii",
    "print_calibration_summary",
    "print_moments",
)


def test_no_removed_api_names_in_site():
    pattern = re.compile("|".join(REMOVED_API_NAMES))
    offenders = {}
    for page in sorted(SITE.rglob("*.qmd")):
        if "_freeze" in page.parts:
            continue
        hits = sorted(set(pattern.findall(page.read_text(encoding="utf-8"))))
        if hits:
            offenders[page.relative_to(SITE).as_posix()] = hits
    assert not offenders, f"Removed API names still on the site: {offenders}"


def test_no_removed_api_names_in_examples_or_readme():
    root = SITE.parent
    pattern = re.compile("|".join(REMOVED_API_NAMES))
    targets = [root / "README.md", *sorted((root / "examples").glob("*.py"))]
    offenders = {}
    for path in targets:
        if not path.exists():
            continue
        hits = sorted(set(pattern.findall(path.read_text(encoding="utf-8"))))
        if hits:
            offenders[path.name] = hits
    assert not offenders, f"Removed API names still in shipped code: {offenders}"
