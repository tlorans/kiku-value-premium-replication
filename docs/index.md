---
layout: default
title: Home
---

# Kiku (2006) – Is the Value Premium a Puzzle?

This package is a transparent replica of Dana Kiku (2006), “Is the Value Premium a Puzzle?” It implements the Bansal–Yaron long-run risks model with Epstein–Zin preferences, her 1930–2003 value/growth/market construction, her cash-flow-only calibration discipline, and her Tauchen–Hussey numerical solution.

The value premium is rational compensation for differential exposure to long-run consumption risk.

The public API and this site follow her paper order. Each section is still a recipe: what she does, what you call, what you should see.

## Recipe at a glance

| Section | Paper | Package |
|---------|-------|---------|
| **2. Empirical Evidence** | 1930–2003 BM portfolios, Table I, Figures 1–4 | `kiku_value_premium.empirical` |
| **3. Model** | Epstein–Zin IMRS, Bansal–Yaron process, Tauchen–Hussey, analytical §3.4 | `kiku_value_premium.model` |
| **4. Calibration** | Equation (19), Table II, cash-flow moments III–V | `kiku_value_premium.calibration` |
| **5. Asset Pricing Implications** | Tables VII–X, mechanism figures, Figure 5 | `kiku_value_premium.implications` |

Start here: **[Installation & Quick Start](installation.html)**.

Without WRDS you can still solve Table II. Section 2 needs the `[data]` extra and a repo-root `.env`.

[GitHub repository](https://github.com/tlorans/kiku-value-premium-replication)

## Citation

Kiku, D. (2006). *Is the Value Premium a Puzzle?* Job Market Paper, Duke University / Wharton.

Bansal, R. & Yaron, A. (2004). Risks for the Long Run. *Journal of Finance*.
