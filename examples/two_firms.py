"""Two synthetic firms: identical except the loading of dividends on x_t.

Issue 5 of REWRITE_PLAN.md. Two dividend processes that differ only in
phi (1.5 vs 0.5). Nothing is estimated; nothing is re-tuned. The model
returns, for each firm, the PD elasticity to x_t, the annualized
compensation for x_t-news, expected dividend growth, and the Gordon-style
return at the default anchor.

Run: uv run python examples/two_firms.py
Every number on the Price your own claim page comes from this printout.
"""
from __future__ import annotations

import lrrcs as lrr

FIRMS = (
    ("A", 0.5),
    ("B", 1.5),
)

print("Two firms, identical except the loading of dividends on x_t")
print()
print(f"{'firm':6s} {'phi':>5s} {'A1':>7s} {'premium_lr %':>13s} {'g_eff %':>9s} {'gordon %':>9s}")
# Both firms go in one model, so a single solve prices the pair.
firms = lrr.LongRunRisksModel(
    claims={name: lrr.ClaimParams.from_loading(phi) for name, phi in FIRMS}
).solve(method="analytical")

for name, phi in FIRMS:
    print(
        f"{name:6s} {phi:5.1f} {firms.A1[name]:7.1f} "
        f"{firms.long_run_premium[name]:13.2f} "
        f"{firms.expected_growth[name]:9.2f} {firms.gordon_return[name]:9.2f}"
    )
print()
print("premium_lr is the x_t-news piece of compensation (annualized).")
print("gordon_return = g_eff + D/P at the default anchor (mean log P/D 3.30):")
print("the growth channel alone; it is blind to risk. The wedge between the")
print("firms is the loading, and nothing was re-tuned between the two rows.")
