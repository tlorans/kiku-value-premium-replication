"""Figures for the results table and the 0.4-vs-5.3 warning (Issue 11).

Fig A - dot-and-interval plot of E[R] and mean log P/D, data vs model,
      for growth/value/market (the Home table as a picture). Data points
      carry Kiku's printed Newey-West SEs; model P/D levels come from the
      analytical solution (TRACED). Model E[R] levels are the site's
      Table VII column and are plotted as printed, WITHOUT intervals:
      they are not regenerable from the package (NUMBERS.md, F1).
Fig B - one bar of the 5.3 model premium with the 0.4 x_t-news slice
      marked; caption is the warning sentence, verbatim.

Style: matplotlib defaults, no color-only encoding (print-safe: open vs
filled markers plus distinct marker shapes).

Run: uv run python figures/make_figures.py   (writes docs/figures/*.svg)
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

import lrrcs as lrr

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

CLAIMS = ("Growth", "Value", "Market")
# Kiku Table I / Table VII printed values (goldens.py / site table).
ER_DATA = {"Growth": (7.81, 1.98), "Value": (13.88, 1.74), "Market": (8.56, 1.79)}
ER_MODEL = {"Growth": 6.07, "Value": 11.36, "Market": 7.53}  # F1-open, plotted as printed
PD_DATA = {"Growth": (3.61, 0.18), "Value": (3.25, 0.12), "Market": (3.34, 0.13)}
# Model mean log P/D from the analytical solution (TRACED).
_sol = lrr.solve_analytical(lrr.get_table_ii_params())
PD_MODEL = {"Growth": _sol.mean_log_pd["growth"], "Value": _sol.mean_log_pd["value"], "Market": _sol.mean_log_pd["market"]}

MARKERS = {"Growth": "o", "Value": "s", "Market": "^"}
POS = {"Growth": 0, "Value": 1, "Market": 2}


def fig_a() -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6))
    panels = (
        (axes[0], "E[R] %", ER_DATA, ER_MODEL, "(a) Expected return"),
        (axes[1], "Mean log P/D", PD_DATA, PD_MODEL, "(b) Mean log P/D"),
    )
    for ax, ylab, data, model, title in panels:
        for claim in CLAIMS:
            x = POS[claim]
            m, se = data[claim]
            ax.errorbar(
                x - 0.12, m, yerr=se, fmt=MARKERS[claim], color="black",
                mfc="black", capsize=3, label=f"{claim} data" if ylab == "E[R] %" else None,
            )
            mv = model[claim]
            ax.plot(x + 0.12, mv, MARKERS[claim], color="black", mfc="white", mew=1.4)
        ax.set_xticks(list(POS.values()))
        ax.set_xticklabels(CLAIMS)
        ax.set_ylabel(ylab)
        ax.set_title(title, fontsize=10)
    axes[0].plot([], [], "o", color="black", mfc="black", label="data (± SE)")
    axes[0].plot([], [], "o", color="black", mfc="white", mew=1.4, label="model")
    axes[0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.suptitle("Data vs model: the pair of outputs", fontsize=11, y=1.0)
    fig.tight_layout()
    path = OUT / "results_pair.svg"
    fig.savefig(path, bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")
    print("  model E[R] dots plotted as printed (Table VII; F1-open, no intervals)")
    print("  model P/D dots from solve_analytical (TRACED)")


def fig_b() -> None:
    fig, ax = plt.subplots(figsize=(6.4, 3.0))
    ax.bar([0], [5.3], width=0.45, color="0.85", edgecolor="black", label="model value-growth premium")
    ax.bar([0], [0.4], width=0.45, color="0.55", edgecolor="black", label="compensation for $x_t$-news")
    ax.axhline(6.0, color="black", lw=1.0, ls="--")
    ax.text(-0.28, 6.0 + 0.15, "data: about 6", fontsize=9)
    ax.annotate("0.4", xy=(0.0, 0.4), xytext=(0.16, 1.6),
                arrowprops=dict(arrowstyle="->", lw=0.9), fontsize=9)
    ax.text(0.02, 5.3 + 0.12, "5.3", fontsize=10)
    ax.set_xticks([])
    ax.set_xlim(-0.5, 0.5)
    ax.set_ylabel("percent per year")
    ax.set_title("The printout is only the $x_t$-news slice of the 5.3", fontsize=10)
    ax.legend(frameon=False, fontsize=8, loc="upper right")
    fig.tight_layout()
    path = OUT / "premium_decomposition.svg"
    fig.savefig(path, bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"wrote {path.relative_to(ROOT)}")


if __name__ == "__main__":
    fig_a()
    fig_b()
