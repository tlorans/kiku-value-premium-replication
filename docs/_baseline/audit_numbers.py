"""Issue 0 audit: reproduce every numeric claim on the site via package code.

Run: uv run python .issue0/audit_numbers.py  (from repo root)
Output is captured to .issue0/audit_output.txt and summarized in NUMBERS.md.
Network-dependent chunks (FRED/WRDS downloads in financial-data.md) are
excluded here and marked chunk-traced in NUMBERS.md.
"""
from __future__ import annotations

import dataclasses
from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl

import lrrcs as lrr

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def cap(name: str) -> None:
    print(f"\n===== {name} =====")


# --- page: index.md / getting-started.md / installation.md / api.md / time-series.md / cross-section.md
cap("quickstart print_long_short_premium (index, getting-started, installation, time-series, cross-section)")
params = lrr.get_table_ii_params()
sol = lrr.solve_analytical(params)
lrr.print_long_short_premium(sol)

cap("Table II params dump (getting-started, long-run-risks-model, time-series)")
for field in ("prefs", "cons"):
    print(field, dataclasses.asdict(getattr(params, field)))
print("dividends", {k: dataclasses.asdict(v) for k, v in params.dividends.items()})

cap("solution internals: A1, A2, premium_lr, mean_log_pd, lambda")
print("A1", {k: round(v, 1) for k, v in sol.A1.items()})
print("A2", {k: round(v, 1) for k, v in sol.A2.items()})
print("premium_lr %", {k: round(100 * v, 2) for k, v in sol.premium_lr.items()})
print("mean_log_pd", {k: round(v, 2) for k, v in sol.mean_log_pd.items()})

cap("equal-phi counterfactual (getting-started, cross-section)")
p2 = lrr.get_table_ii_params()
p2.dividends["value"].phi = 2.6
p2.dividends["growth"].phi = 2.6
lrr.print_long_short_premium(lrr.solve_analytical(p2))

cap("theta arithmetic (getting-started, long-run-risks-model)")
delta, gamma, psi = 0.999, 10.0, 1.5
print(delta, gamma, psi, "->", gamma, round(1 / psi, 3), round((1.0 - gamma) / (1.0 - 1.0 / psi), 1))

# --- page: getting-started.md
cap("A1 by hand, growth/value (cross-section)")
psi, rho = 1.5, 0.98
for name, phi, zbar in (("growth", 2.6, 3.65), ("value", 6.2, 3.10)):
    kappa1 = np.exp(zbar) / (1.0 + np.exp(zbar))
    print(name, round((phi - 1.0 / psi) / (1.0 - kappa1 * rho), 1))

cap("A1 ratio (cross-section)")
print("A1 value / A1 growth", round(sol.A1["value"] / sol.A1["growth"], 2))

cap("A1 market by hand (time-series)")
phi, psi, rho, mean_z = 2.8, 1.5, 0.98, 3.24
kappa1 = np.exp(mean_z) / (1.0 + np.exp(mean_z))
print("kappa1", round(kappa1, 3), "A1", round((phi - 1.0 / psi) / (1.0 - kappa1 * rho), 1))

# --- data files
panel_pd = pd.read_csv(DATA / "annual_panel.csv")
dcp = pl.read_csv(DATA / "consumption_annual.csv").sort("year")
panelp = pl.read_csv(DATA / "annual_panel.csv")
rf = pd.read_csv(DATA / "rf_annual.csv")
y = dcp["dc"].to_numpy()

# --- page: financial-data.md / cross-section.md (reconstruction numbers)
cap("table_i on shipped reconstruction (financial-data)")
print(lrr.table_i(panel_pd).to_string(index=False))

cap("reconstruction return means (cross-section)")
print({c: round(float(panelp.filter(pl.col("claim") == c)["ret"].mean() * 100), 2)
       for c in ("Growth", "Value", "Market")})

cap("CAPM betas on reconstruction (cross-section)")
rm = panelp.filter(pl.col("claim") == "Market").sort("year")["ret"].to_numpy()
rm_d = rm - rm.mean()
def beta(claim: str) -> float:
    r = panelp.filter(pl.col("claim") == claim).sort("year")["ret"].to_numpy()
    r_d = r - r.mean()
    return float(np.dot(rm_d, r_d) / np.dot(rm_d, rm_d))
print({c: round(beta(c), 2) for c in ("Growth", "Value")})

# --- page: measuring-leverage.md
cap("consumption MA head (measuring-leverage, time-series)")
ma = lrr.expected_growth_proxy(y, window=2)
print(dcp.with_columns(pl.Series("ma", ma)).head(6))

cap("phi_tilde annual OLS (measuring-leverage, cross-section)")
def phi_hat(claim: str) -> float:
    dd = (panelp.filter(pl.col("claim") == claim).join(dcp, on="year").sort("year")["dgrowth"].to_numpy())
    mask = np.isfinite(ma) & np.isfinite(dd)
    x = ma[mask] - ma[mask].mean()
    e = dd[mask] - dd[mask].mean()
    return float(np.dot(x, e) / np.dot(x, x))
print({c: round(phi_hat(c), 3) for c in ("Growth", "Value", "Market")})

cap("print_calibration_summary market (measuring-leverage, time-series)")
def dd(claim: str) -> np.ndarray:
    return (panelp.filter(pl.col("claim") == claim).join(dcp, on="year").sort("year")["dgrowth"].to_numpy())
div = lrr.calibrate_from_data(y, frequency="annual", window=2,
                              long=dd("Value"), short=dd("Growth"), market=dd("Market"))
lrr.print_calibration_summary(div)

# --- page: time-series.md
cap("market head rows (time-series)")
mkt = panelp.filter(pl.col("claim") == "Market").join(dcp, on="year").sort("year")
print(mkt.head(6))

cap("sample stats (time-series, financial-data)")
print(len(y), round(y.mean() * 100, 2), round(y.std(ddof=1) * 100, 2))
print("AC1", round(float(np.corrcoef(y[:-1], y[1:])[0, 1]), 2))
print("rf mean %", round(float(rf["rf"].mean() * 100), 2))

cap("market describe (time-series)")
print(mkt.select("ret", "dgrowth", "pd").describe())

cap("simulate_cashflow_moments n_sims=20 seed=1 (time-series)")
print(lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1))

cap("kalman filter_expected_growth (time-series appendix)")
out = lrr.filter_expected_growth(y)
print({k: out[k] for k in ("mu", "rho", "q", "r", "loglik")})

# --- page: financial-data.md toy chunks
cap("toy Campbell-Shiller year (financial-data)")
dates = pd.date_range("2000-01-31", periods=12, freq="ME")
retx = pd.Series(0.01, index=dates)
ret = pd.Series(0.012, index=dates)
v = 100.0
year_div: dict[int, float] = {}
year_v: dict[int, float] = {}
for dt in dates:
    d = (ret.loc[dt] - retx.loc[dt]) * v
    v = v * (1.0 + retx.loc[dt])
    year_div[int(dt.year)] = year_div.get(int(dt.year), 0.0) + max(d, 0.0)
    year_v[int(dt.year)] = v
print(pd.DataFrame({"year": [2000], "div": [year_div[2000]], "v": [year_v[2000]],
                    "pd": [year_v[2000] / year_div[2000]]}))

cap("toy real T-bill (financial-data)")
idx = pd.date_range("2000-01-31", periods=24, freq="ME")
t90 = pd.Series(0.004, index=idx)
cpi = pd.Series(100.0 * (1.002 ** np.arange(24)), index=idx)
inflation = np.log(cpi / cpi.shift(1))
real_m = t90 - inflation.rolling(12).mean()
print(real_m.resample("YE").mean())

# --- Table VII model moments (the model columns of the Home/results tables)
cap("compute_asset_pricing_moments (model columns: E[R], sd, mean log P/D, rf, betas)")
solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
mom = lrr.compute_asset_pricing_moments(solver)
lrr.print_asset_pricing_moments(mom)
print("beta value / beta growth =", round(mom["capm_beta"]["value"] / mom["capm_beta"]["growth"], 2))
