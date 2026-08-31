"""Two free numbers: what a DCF gives up when forecast and rate come from two places.

Three panels on the Table II economy:

(A) One rate for everything — value each claim's model cash flows at one
    common discount rate (the DCF move). Exact, no simulation of return
    levels: the implied expected return of every claim equals the common
    rate, so the implied value-growth premium is exactly zero, and value
    (whose model dividends grow faster) is priced RICHER - the opposite of
    the data ranking.
(B) A rate fitted to the CAPM — model CAPM betas from log-return
    innovations of the affine solution (levels cancel; only loadings enter).
(C) A forecast is not a valuation — raise value's cash-flow loading phi
    (6.2 -> 7.4) and compare the DCF response (price up a little through
    expected growth, expected return unchanged) with the equilibrium
    response (compensation and PD elasticity both move).

Run: uv run python examples/dcf_counterfactual.py
Every number on the Two free numbers page comes from this printout.

Note: Kiku's printed Table VII return levels (6.07/11.36/7.53, rf 1.58) do
not reproduce exactly from the package, for the grid-resolution reason
recorded in NUMBERS.md. This script therefore states the DCF panel exactly
and the CAPM panel in level-free form, so neither depends on those levels.
"""
from __future__ import annotations

import numpy as np

import lrrcs as lrr
from lrrcs.model import Dynamics

N_PATHS = 200
N_YEARS = 74
SEED = 7
T = N_YEARS * 12

model = lrr.LongRunRisksModel()
params = model.params
sol = model.solve(method="analytical")
sigma = params.cons.sigma

# Annualized expected dividend growth, in percent, including the two
# convexity terms. The solution computes it, so nothing is re-derived here.
g_eff = sol.expected_growth

print("Two free numbers - DCF counterfactuals on the Table II economy")
print()

print("===== (A) One rate for everything =====")
print()
print("Model cash flows (Table II), annualized expected dividend growth:")
for name in ("growth", "value", "market"):
    print(f"  g_eff {name:8s}: {g_eff[name]:6.2f} %/yr")
print()
print("Discount both claims' cash flows at one common rate r:")
print("  - price of each claim: P/D = sum_t E[D_t/D_0] / (1+r)^t")
print("  - implied expected return of each claim: E[R] = r, identically")
print("  => implied value-growth premium under (A): 0.00 pp (exactly, at any r)")
print()
print("P/D ranking the DCF must produce (r cancels in the comparison of g):")
print(f"  value cash flows grow {g_eff['value'] - g_eff['growth']:+.2f} pp/yr faster")
print("  => the DCF prices value RICHER than growth")
print("  data: value is CHEAPER (mean log P/D 3.25 vs 3.61)")
print()
print("Equilibrium: the paper's printed Table VII model gap is 5.3 pp;")
print("data: 13.88 - 7.81 = 6.07 pp.")

print()
print("===== (B) A rate fitted to the CAPM =====")
print()
# Betas from log-return innovations of the affine solution:
# log R_{t+1} = const + dd_{t+1} + kappa1 * z_{t+1} - z_t ; levels cancel.
dyn = Dynamics(params, seed=SEED)
names = ("growth", "value", "market")
kappa1 = {k: np.exp(sol.mean_log_pd[k]) / (1.0 + np.exp(sol.mean_log_pd[k])) for k in names}
lr = {k: [] for k in names}
for _ in range(N_PATHS):
    path = dyn.simulate_cashflows(T)
    s2 = path["sigma2"]
    for k in names:
        z = sol.A1[k] * path["x"] + sol.A2[k] * (s2 - sigma**2)
        lr[k].append(path[f"dd_{k}"][1:] + kappa1[k] * z[1:] - z[:-1])
lr = {k: np.concatenate(v) for k, v in lr.items()}
r_m = lr["market"]
r_m_d = r_m - r_m.mean()
var_m = float(np.dot(r_m_d, r_m_d) / r_m.size)
betas = {}
for k in ("growth", "value"):
    r_i = lr[k]
    r_i_d = r_i - r_i.mean()
    betas[k] = float(np.dot(r_i_d, r_m_d) / r_m.size / var_m)
for k in ("growth", "value"):
    print(f"CAPM beta {k:8s} (affine innovations): {betas[k]:7.3f}")
print(f"Beta ratio value/growth            : {betas['value'] / betas['growth']:7.3f}")
print()
sign = "negative" if betas["value"] < betas["growth"] else "positive"
print(f"(beta_value - beta_growth) = {betas['value'] - betas['growth']:+.3f} is {sign}:")
print("the CAPM-implied value-growth spread = (b_v - b_g) x (E[Rm] - rf) has the")
print("WRONG SIGN against a positive premium. The magnitude needs a premium")
print("level, which this panel deliberately does not depend on.")

print()
print("===== (C) A forecast is not a valuation =====")
print()
sol_hi = model.replace(claims={"value": {"phi": 7.4}}).solve(method="analytical")
print("Raise value's cash-flow loading on x_t: phi 6.2 -> 7.4")
print()
print("DCF world (rate held at r, price of risk does not move):")
print(f"  g_eff value : {g_eff['value']:6.2f} %/yr -> "
      f"{sol_hi.expected_growth['value']:6.2f} %/yr")
print("  price response: up, but only through expected growth (a little)")
print("  expected-return response: none - the rate never sees the risk")
print()
print("Equilibrium (analytical solution, nothing re-estimated):")
print(f"  A1 value    : {sol.A1['value']:7.1f} -> {sol_hi.A1['value']:7.1f}  (PD elasticity to x)")
print(f"  premium_lr  : {sol.long_run_premium['value']:6.2f} % -> {sol_hi.long_run_premium['value']:6.2f} %  (x-news compensation)")
print("  the same news moves the cash flows AND the price of risk")
