---
layout: default
title: Kiku (2006) Value Premium Replication
---

# Kiku (2006) – Is the Value Premium a Puzzle?

**Full replication package** of Dana Kiku’s 2006 Job Market Paper.

The paper shows that the value premium is rational compensation for differential exposure to long-run consumption risk under Epstein–Zin preferences.

This site documents the exact methodology and maps every step of Kiku’s recipe to the public API of the Python package.

---

## Quick links

- **[The Exact 6-Step Recipe → Package API](KIKU_RECIPE.html)**  
  The core documentation. Walks through each step of the paper and shows the corresponding functions and classes.

- [GitHub repository](https://github.com/tlorans/kiku-value-premium-replication)  
  Source code, examples, and installation instructions.

- [Installation](https://github.com/tlorans/kiku-value-premium-replication#installation)

---

## The 6-Step Recipe at a glance

| Step | What Kiku does | Package API |
|------|----------------|-------------|
| **1** | Aggregate LRR consumption process | `params.ConsumptionParams` + `dynamics.Dynamics` |
| **2** | Heterogeneous cash-flow processes (different long-run loadings) | `params.DividendParams` (`phi` = long-run leverage) |
| **3** | Calibrate **only** to time-series cash-flow moments | `calibration.calibrate_from_data` |
| **4** | Epstein–Zin preferences | `preferences.EpsteinZinPreferences` |
| **5** | Numerical solution (Tauchen–Hussey style) | `solver.ModelSolver` |
| **6** | Evaluate time-series **and** cross-section | `moments.compute_asset_pricing_moments` + `analytical.solve_analytical` |

→ Full walkthrough with code: **[KIKU_RECIPE.md](KIKU_RECIPE.html)**

---

## Why this package?

- Implements the **exact** calibration discipline of the paper (cash-flow moments only, never return premia).
- Exposes every step of the methodology through a clean, modular API.
- Ready to be extended to any cross-section (industries, climate-sorted portfolios, quality factors, etc.) via `calibrate_from_data`.
- Provides both a fast analytical solution that isolates the long-run risk channel and a full numerical solver that recovers the quantitative magnitudes reported in the paper.

---

## Citation

Kiku, D. (2006). *Is the Value Premium a Puzzle?* Job Market Paper, Duke University / Wharton.

Bansal, R. & Yaron, A. (2004). Risks for the Long Run. *Journal of Finance*.

---

*Package maintained at [github.com/tlorans/kiku-value-premium-replication](https://github.com/tlorans/kiku-value-premium-replication)*
