---
title: Home
nav_order: 1
permalink: /
---

# Long-run risks

Kiku (2006) in code: cash-flow leverage on long-run consumption risk prices the value premium. Average returns never enter.

Value earned about six extra points a year over 1930–2003 and was cheaper. Market betas sit near one, so the CAPM does not explain the spread. In this economy the two facts are one fact. Value dividends load harder on the persistent piece of consumption growth than growth dividends do. One Epstein–Zin household prices both claims. The outputs are a high premium *and* a low price–dividend ratio. The same household still prices the market.

|  | E[R] % data | E[R] % model | Mean log P/D data | Mean log P/D model |
|:---|---:|---:|---:|---:|
| Growth | 7.81 (1.98) | 6.07 (2.91) | 3.61 (0.18) | 3.65 (0.06) |
| Value | 13.88 (1.74) | 11.36 (4.30) | 3.25 (0.12) | 3.10 (0.15) |
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |

The model gap is about 5.3 percent against about 6 in the data. Value's model CAPM beta is *lower* than growth's (ratio 0.92) while its premium is higher — the puzzle an econometrician would print, and not a puzzle inside the household. Cash flows and the discount rate are not two free numbers; they come from one process. A DCF treats the cash flow forecast and the discount rate as independent inputs.

```python
import lrrcs as lrr

sol = lrr.solve_analytical(lrr.get_table_ii_params())
lrr.print_long_short_premium(sol)
```

That printout is only compensation for news about \(x_t\) — about 0.4 percent on the value–growth spread. The table above is the Euler equation on the whole claim (short-run shocks and volatility news included). Do not subtract 0.4 from 5.3 and call it a miss.

![Long-run premium versus leverage](figures/lrr_sml.svg)

<p class="caption">Compensation against cash-flow leverage on long-run consumption news, not CAPM \(\beta\). Value sits to the right of growth because its dividends load harder on \(x_t\).</p>

[Run the experiment]({{ '/getting-started.html' | relative_url }})

## The argument

1. [The result]({{ '/getting-started.html' | relative_url }}) — Gordon, Table II, the pair of outputs, one what-if.
2. [The long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}) — where cash-flow growth comes from, where the discount rate comes from, and the fraction where they meet.
3. [Measuring leverage]({{ '/measuring-leverage.html' | relative_url }}) — equation (19): dividend growth on a two-year MA of consumption. No returns.
4. [Does the market still fit?]({{ '/time-series.html' | relative_url }}) — the same household still prices the market.
5. [Value versus growth]({{ '/cross-section.html' | relative_url }}) — two legs, nothing re-tuned; the value premium and the CAPM anomaly.

[Package]({{ '/package.html' | relative_url }}) · [Installation]({{ '/installation.html' | relative_url }}) · [Financial data]({{ '/financial-data.html' | relative_url }}) · [API]({{ '/api.html' | relative_url }}) · [GitHub](https://github.com/tlorans/kiku-value-premium-replication)
