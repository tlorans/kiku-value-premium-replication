---
title: Home
nav_order: 1
permalink: /
---

# Is the Value Premium a Puzzle?

This package replicates Dana Kiku’s 2006 job market paper. The model is Bansal and Yaron (2004) long-run risks with Epstein–Zin preferences. The claim is hers: the value premium is rational compensation for differential exposure to long-run consumption risk.

She writes that, in the data as in the model, cash flows of value firms are highly exposed to low-frequency fluctuations in aggregate consumption, whereas growth firms’ dividends are mainly driven by short-lived consumption news and risks related to fluctuating economic uncertainty. Dispersion in those long-run loadings, amplified by persistence in expected growth, produces a value premium of about 5.3 percent in the model against about 6 percent in the 1930–2003 sample.

The site follows her paper, not a six-step implementation checklist.

1. [Empirical evidence]({% link empirical.md %}) — Section 2: value, growth, and the market, 1930–2003
2. [The long-run risks model]({% link model.md %}) — Section 3: preferences, cash flows, solution
3. [Calibration]({% link calibration.md %}) — Section 4: cash-flow moments only
4. [Asset pricing implications]({% link implications.md %}) — Section 5: premia, valuations, CAPM failure

Install and run: [Installation]({% link installation.md %}). Names: [API]({% link api.md %}). Other portfolios: [Generalizing the recipe]({% link generalization.md %}).

Without WRDS you can still solve her Table II calibration. Section 2 needs the `[data]` extra and a repo-root `.env`.

[GitHub repository](https://github.com/tlorans/kiku-value-premium-replication)

## Citation

Kiku, D. (2006). *Is the Value Premium a Puzzle?* Job Market Paper, Duke University / Wharton.

Bansal, R., and A. Yaron. (2004). “Risks for the Long Run.” *Journal of Finance*.
