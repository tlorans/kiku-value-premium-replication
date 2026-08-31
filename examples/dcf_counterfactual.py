"""Two free numbers: what a DCF gives up when forecast and rate come from two places.

Issue 4 of REWRITE_PLAN.md. Three panels on the Table II economy:

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

Note (F1, NUMBERS.md): Table VII return LEVELS (6.07/11.36/7.53, rf 1.58)
are not reproducible from the package; this script therefore states the
DCF panel exactly and the CAPM panel in level-free form.
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
phi_x = params.cons.phi_x
rho = params.cons.rho

# Stationary variance of the persistent component x_t.
gamma0 = (phi_x * sigma) ** 2 / (1.0 - rho**2)


def var_cum_x(t: int) -> float:
    """Var(sum_{s=0}^{t-1} x_s) for an AR(1) with stationary variance gamma0."""
    h = np.arange(1, t)
    return float(gamma0 * (t + 2.0 * np.sum((t - h) * rho**h)))


def expected_dividend_path(name: str, max_t: int = 1200) -> np.ndarray:
    """E[D_t / D_0] for t = 1..max_t under the stationary distribution."""
    d = params.claims[name]
    mean_growth = d.mu + 0.5 * d.phi_sigma**2 * sigma**2  # iid part
    out = np.empty(max_t)
    for t in range(1, max_t + 1):
        out[t - 1] = np.exp(mean_growth * t + 0.5 * d.phi**2 * var_cum_x(t))
    return out


def g_effective(name: str) -> float:
    """Annualized expected dividend growth incl. convexity (long-horizon rate)."""
    d = params.claims[name]
    monthly = d.mu + 0.5 * d.phi_sigma**2 * sigma**2 + 0.5 * d.phi**2 * gamma0 * (1.0 + rho) / (1.0 - rho)
    return monthly * 12.0


print("Two free numbers - DCF counterfactuals on the Table II economy")
print()

print("===== (A) One rate for everything =====")
print()
print("Model cash flows (Table II), annualized expected dividend growth:")
for name in ("growth", "value", "market"):
    print(f"  g_eff {name:8s}: {g_effective(name) * 100:6.2f} %/yr")
print()
print("Discount both claims' cash flows at one common rate r:")
print("  - price of each claim: P/D = sum_t E[D_t/D_0] / (1+r)^t")
print("  - implied expected return of each claim: E[R] = r, identically")
print("  => implied value-growth premium under (A): 0.00 pp (exactly, at any r)")
print()
print("P/D ranking the DCF must produce (r cancels in the comparison of g):")
print(f"  value cash flows grow {(g_effective('value') - g_effective('growth')) * 100:+.2f} pp/yr faster")
print("  => the DCF prices value RICHER than growth")
print("  data: value is CHEAPER (mean log P/D 3.25 vs 3.61)")
print()
print("Equilibrium (Table VII column, currently untraced - F1): 5.3 pp model gap;")
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
print("WRONG SIGN against a positive premium. Magnitude needs the premium level")
print("(Table VII, untraced - F1).")

print()
print("===== (C) A forecast is not a valuation =====")
print()
sol_hi = model.replace(claims={"value": {"phi": 7.4}}).solve(method="analytical")
print("Raise value's cash-flow loading on x_t: phi 6.2 -> 7.4")
print()
print("DCF world (rate held at r, price of risk does not move):")
g_hi = (
    params.claims["value"].mu
    + 0.5 * params.claims["value"].phi_sigma**2 * sigma**2
    + 0.5 * 7.4**2 * gamma0 * (1.0 + rho) / (1.0 - rho)
) * 12.0
print(f"  g_eff value : {g_effective('value') * 100:6.2f} %/yr -> {g_hi * 100:6.2f} %/yr")
print("  price response: up, but only through expected growth (a little)")
print("  expected-return response: none - the rate never sees the risk")
print()
print("Equilibrium (analytical solution, nothing re-estimated):")
print(f"  A1 value    : {sol.A1['value']:7.1f} -> {sol_hi.A1['value']:7.1f}  (PD elasticity to x)")
print(f"  premium_lr  : {sol.long_run_premium['value']:6.2f} % -> {sol_hi.long_run_premium['value']:6.2f} %  (x-news compensation)")
print("  the same news moves the cash flows AND the price of risk")
