---
layout: default
title: Home
---

# Kiku (2006) – Is the Value Premium a Puzzle?

**Python package** that replicates Dana Kiku’s 2006 Job Market Paper using the Bansal–Yaron long-run risks model with Epstein–Zin preferences.

The value premium is rational compensation for differential exposure to long-run consumption risk.

This multi-page site documents the exact methodology and maps every step of Kiku’s recipe to the public API of the package.

## Site navigation

- **[The Exact 6-Step Recipe](KIKU_RECIPE.html)** – core methodology mapped to code  
- **[Installation & Quick Start](installation.html)**  
- **[API / Modules Reference](api.html)**  
- **[Examples](examples.html)**  
- **[Generalizing the Recipe](generalization.html)** (industries, climate, any portfolios)  
- **[Results – Tables & Figures](results.html)** – recovery of Kiku’s quantitative targets  
- [GitHub Repository](https://github.com/tlorans/kiku-value-premium-replication)

## The 6-Step Recipe at a glance

| Step | What Kiku does | Package API |
|------|----------------|-------------|
| **1** | Aggregate LRR consumption process | `params.ConsumptionParams` + `dynamics.Dynamics` |
| **2** | Heterogeneous cash-flow processes | `params.DividendParams` (`phi` = long-run leverage) |
| **3** | Calibrate only to time-series cash-flow moments | `calibration.calibrate_from_data` |
| **4** | Epstein–Zin preferences | `preferences.EpsteinZinPreferences` |
| **5** | Numerical solution (Tauchen–Hussey) | `solver.ModelSolver` |
| **6** | Evaluate time-series & cross-section | `moments.compute_asset_pricing_moments` + `analytical.solve_analytical` |

→ Full details: **[KIKU_RECIPE](KIKU_RECIPE.html)**  
→ Quantitative recovery of the paper: **[Results](results.html)**

## Why this package?

- Implements the **exact** calibration discipline of the paper (cash-flow moments only).
- Exposes every step through a clean, modular API.
- Ready to extend to any cross-section via `calibrate_from_data`.
- Provides both a fast analytical solution (isolates the long-run channel) and a full numerical solver.

## Citation

Kiku, D. (2006). *Is the Value Premium a Puzzle?* Job Market Paper, Duke University / Wharton.  
Bansal, R. & Yaron, A. (2004). Risks for the Long Run. *Journal of Finance*.
