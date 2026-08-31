"""Structural lint for the Quarto site (site/).

Execution correctness is enforced by `quarto render` itself (cells run
at build time), so these tests only pin what a render does not check:
sidebar completeness, legacy-URL redirect coverage, leftover Jekyll
syntax, and freeze coverage (CI renders from the committed freeze and
must never silently skip an executed chapter).
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
    # the Jekyll root permalink maps to index.qmd itself
    missing = LEGACY_URLS - covered
    assert not missing, f"legacy URLs without an alias: {sorted(missing)}"


def test_no_jekyll_residue():
    patterns = ("relative_url", "{: .", "\\\\(", "{{ site.")
    for path in _qmd_files():
        text = path.read_text(encoding="utf-8")
        for pat in patterns:
            assert pat not in text, f"Jekyll residue {pat!r} in {path.name}"


def _chapter_files():
    return [p for p in _qmd_files() if "chapters" in p.parts]


CHAPTERS = sorted((SITE / "chapters").glob("*.qmd"))
PROSE_BUDGET = 1300

_FENCE = re.compile(r"^\s*```")
_FRONT_MATTER = re.compile(r"^---\n.*?\n---\n", flags=re.S)


def _prose_words(path: Path) -> int:
    """Words a reader has to read: everything outside code fences.

    Code cells are folded, skimmable, and are the point of the page, so
    they are not part of the reading budget.
    """
    text = _FRONT_MATTER.sub("", path.read_text(encoding="utf-8"))
    in_code = False
    words = 0
    for line in text.splitlines():
        if _FENCE.match(line):
            in_code = not in_code
            continue
        if not in_code:
            words += len(line.split())
    return words


@pytest.mark.parametrize("path", CHAPTERS, ids=lambda p: p.stem)
def test_chapter_ships_check_yourself(path):
    """One collapsed self-check per chapter, replacing Recall and Exercises."""
    text = path.read_text(encoding="utf-8")
    assert 'title="Check yourself"' in text, (
        f"missing 'Check yourself' callout: {path.name}"
    )
    for dead in ('title="Recall"', "## Exercises", 'title="Check your answer"',
                 'title="Where to go next"'):
        assert dead not in text, (
            f"retired block {dead!r} still present: {path.name}"
        )


@pytest.mark.parametrize("path", CHAPTERS, ids=lambda p: p.stem)
def test_chapter_prose_within_budget(path):
    """A chapter page is at most PROSE_BUDGET words outside code fences."""
    count = _prose_words(path)
    assert count <= PROSE_BUDGET, (
        f"{path.name}: {count} prose words, budget {PROSE_BUDGET} "
        f"(over by {count - PROSE_BUDGET})"
    )


def test_chapters_link_references_page():
    """Every chapter points to the references page (primary-source pointer)."""
    for path in _chapter_files():
        text = path.read_text(encoding="utf-8")
        assert "references.qmd" in text, f"no references link: {path.name}"


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


# Names removed from the public API in 0.6.0. They must not survive
# anywhere the reader can see them, prose included: a chapter that
# still names them teaches an API that no longer exists.
REMOVED_API_NAMES = (
    # 0.7.0: roles left the model, calibration became per claim.
    # Patterns are anchored so ordinary prose survives: "the value
    # premium" is the subject of the course, `.value_premium` was an
    # attribute; ClaimParams.from_loading is the new spelling of the
    # old LongRunRisksModel.from_loading.
    r"\.value_premium",
    r"\.long_short_premium",
    r"\.legs",
    "from_cashflows",
    "LongRunRisksModel.from_loading",
    "calibrate_from_data",
    "DividendParams",
    "resolve_legs",
    "get_table_ii_dividends",
    r"\.dividends\b",
    # 0.6.0: the flat function pipeline
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
