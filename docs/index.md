---
title: Home
nav_order: 1
permalink: /
---

# Long-run risks

A general-equilibrium model of **asset prices and risk premia**.

You already know how to price a stock: forecast the cash flows, pick a discount rate, divide. Both numbers are yours to choose, and nothing in the method ties one to the other. This book prices assets the other way around. It builds a small model economy — a *general equilibrium*, meaning prices are not assumed but must adjust until a single investor is content to hold every asset that exists — in which expected cash flows and discount rates both trace back to one measurable source: aggregate consumption. Consumption growth has a small, slow-moving component. Dividends inherit it, some firms much more than others. And an investor who dreads bad news about the distant future prices those dividends. The extra return that investor demands for holding a risky asset — the *risk premium* — is not an input. It comes out of the model, next to the price itself.

And not only for the market as a whole. Value firms — stocks that are cheap relative to their accounting net worth — turn out to have dividends that track the economy's slow component closely; growth firms' dividends barely respond to it. Hand the model those two facts about cash flows and it returns the rest: value's lower price per dollar of dividend *and* its higher expected return, together, from the same investor who prices the market. Average returns never enter the inputs. They are what the model gets graded on.

```python
import lrrcs as lrr

lrr.print_long_short_premium(lrr.solve_analytical(lrr.get_table_ii_params()))
```

[Start here]({{ '/getting-started.html' | relative_url }})

## The book

1. [Financial data]({{ '/financial-data.html' | relative_url }}) — consumption, dividends, the safe rate, and the value and growth portfolios, built from public records.
2. [The long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}) — where cash-flow growth comes from, where the discount rate comes from, and the one expression where they meet.
3. [The Time Series]({{ '/time-series.html' | relative_url }}) — measure the market's cash-flow risk, let the investor price it, and check the risk premium *and* the valuation.
4. [The Cross Section]({{ '/cross-section.html' | relative_url }}) — same investor, nothing re-tuned; only the cash flows differ, and the value premium falls out.

[Package]({{ '/package.html' | relative_url }}) · [Installation]({{ '/installation.html' | relative_url }}) · [API]({{ '/api.html' | relative_url }}) · [GitHub](https://github.com/tlorans/kiku-value-premium-replication)
