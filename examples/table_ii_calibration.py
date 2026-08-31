"""Table II calibration, printed from the package (Issue 7).

Every value below is read from lrr.ModelParams() at run time —
nothing is transcribed. The "target / source" column states what each
parameter is disciplined by.

Run: uv run python examples/table_ii_calibration.py
The calibration table on The long-run risks model page is this output.
"""
from __future__ import annotations

import lrrcs as lrr

p = lrr.ModelParams()
prefs, cons = p.prefs, p.cons

print("Table II calibration (monthly), printed from lrr.ModelParams()")
print()
print("Preferences (household)")
print(f"  delta = {prefs.delta}   | time preference | Kiku (2006) Table II")
print(f"  gamma = {prefs.gamma}   | risk aversion | Kiku (2006) Table II")
print(f"  psi   = {prefs.psi}   | elasticity of intertemporal substitution | Kiku (2006) Table II")
print(f"  theta = {prefs.theta:.1f}  | derived: (1-gamma)/(1-1/psi)")
print()
print("Consumption process (endowment)")
print(f"  mu    = {cons.mu}   | mean monthly growth (~1.8 %/yr) | aggregate moments")
print(f"  rho   = {cons.rho}  | persistence of x_t (half-life ~3 yrs) | aggregate moments")
print(f"  phi_x = {cons.phi_x}  | sd of x_t shocks (x barely visible) | aggregate moments")
print(f"  sigma = {cons.sigma}  | mean monthly volatility (~2.2 %/yr) | aggregate moments")
print(f"  nu    = {cons.nu}  | persistence of volatility | aggregate moments")
print(f"  sigma_w = {cons.sigma_w} | sd of volatility shocks | aggregate moments")
print()
print("Cash-flow processes (per claim)")
hdr = f"  {'claim':8s} {'mu_d':>8s} {'phi':>5s} {'phi_sigma':>10s} {'alpha':>6s}"
print(hdr)
for name, d in p.dividends.items():
    print(f"  {name:8s} {d.mu:8.4f} {d.phi:5.1f} {d.phi_sigma:10.1f} {d.alpha:6.2f}")
print()
print("phi is the long-run leverage: the loading of dividend growth on x_t.")
print("It is the only cross-sectional input. The annual ranking it must")
print("respect is estimated in Measuring leverage (eq. 19): value >> growth.")
