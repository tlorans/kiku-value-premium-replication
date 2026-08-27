---
title: Home
nav_order: 1
permalink: /
---

# Long-run risks

A general-equilibrium model of **asset prices and risk premia**.

You already know how to price a stock: forecast the cash flows, pick a discount rate, divide. This book is about where those two numbers come from — and why they are really one number. In the economy of Bansal and Yaron (2004) and Kiku (2006), consumption growth carries a small but highly persistent component, and its volatility moves over time. Dividends load on that persistent component — this is the cash-flow model, and the loadings are estimated from data. An Epstein–Zin household, whose marginal utility responds to news about the *entire future* of consumption, prices those dividends — this is the discount-rate model. One shock moves expected cash flows for decades and marginal utility at the same instant, and that comovement is the risk premium.

The same machinery is not confined to the market. Value firms' cash flows are highly exposed to long-run consumption shocks; growth firms' are driven more by short-lived fluctuations. Feed the equilibrium those two exposures and it returns value's low price–dividend ratio and high expected return together — prices *and* premia, aggregate *and* cross section, from one household. Average returns never enter the cash-flow step; they are what the model gets graded on.

```python
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

[Start here]({{ '/getting-started.html' | relative_url }})

## How to work a page

Predict first. Then compute the toy case by hand. Then run the same numbers in `lrr`. Change one assumption and say what broke. A cell that prints without an interpretation sentence has not taught the notion.

- **Finance** — name the mechanism and the decision it changes.
- **Quanti** — keep units honest (monthly vs annual, percent vs decimal, simple vs log).
- **Python** — public names live at `lrr.`; do not import submodules in the documented form.

## The book

1. [Financial data]({{ '/financial-data.html' | relative_url }}) — consumption, dividends, the real rate, and the value and growth cash flows, built from the raw records.
2. [The long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}) — where growth comes from, where the discount rate comes from, and the one expression where they meet.
3. [The Time Series]({{ '/time-series.html' | relative_url }}) — estimate the market's cash-flow exposure, let preferences price it, and check the premium *and* the valuation level.
4. [The Cross Section]({{ '/cross-section.html' | relative_url }}) — same household, nothing re-tuned; only the cash-flow exposures differ, and the value premium falls out.

[Package]({{ '/package.html' | relative_url }}) · [Installation]({{ '/installation.html' | relative_url }}) · [API]({{ '/api.html' | relative_url }}) · [GitHub](https://github.com/tlorans/kiku-value-premium-replication)
