"""Structural lint for the Quarto site (site/).

Execution correctness is enforced by `quarto render` itself (cells run
at build time), so these tests only pin what a render does not check:
sidebar completeness, legacy-URL redirect coverage, leftover Jekyll
syntax, and freeze coverage (CI renders from the committed freeze and
must never silently skip an executed chapter).
"""
from pathlib import Path

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
