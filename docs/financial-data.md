---
title: Financial data
nav_order: 3
---

# Financial data
{: .no_toc }

1. TOC
{:toc}

The later chapters need three annual series, 1930–2003: consumption growth, a claims panel (returns, dividend growth, price–dividend), and a real T-bill. This page shows how to retrieve them. It is not a WRDS tutorial.

Tidy Finance already covers Fama–French files, q-factors, and how to store downloads in [Accessing and managing financial data](https://www.tidy-finance.org/chapters/accessing-and-managing-financial-data.html), and credentials plus CRSP / Compustat / CCM in [WRDS, CRSP, and Compustat](https://www.tidy-finance.org/chapters/wrds-crsp-and-compustat.html). Set credentials with `tf.set_wrds_credentials()`; see [Installation]({{ '/installation.html' | relative_url }}).

What is new here is NIPA consumption, the PCE deflator, Campbell–Shiller dividends from `ret` versus `retx`, the real T-bill, and the annual claims panel. Live FRED or WRDS would not be the replica sample. After each retrieval sketch we read the files in `data/`.

```python
import polars as pl
import plotnine as p9
import tidyfinance as tf
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv")
panel = pl.read_csv("data/annual_panel.csv")
rf = pl.read_csv("data/rf_annual.csv")
```

`panel` columns are `year`, `claim` (`Growth`, `Value`, `Market`), `ret`, `dgrowth`, `pd`.

## Consumption

Long-run risk lives in consumption, not in average returns. The series is log growth of real per-capita nondurables plus services (NIPA, via FRED).

```python
import polars as pl
import numpy as np

nd = pl.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DNDGRA3A086NBEA")
sv = pl.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=DSERRA3A086NBEA")
pop = pl.read_csv("https://fred.stlouisfed.org/graph/fredgraph.csv?id=B230RC0A052NBEA")
# DATE plus one value column on each file. Align on year, then:
# level = (ND + SV) / pop
# dc = log(level).diff()
```

You do not need to run that download. The package does it:

```python
import lrrcs as lrr

dc_live = lrr.load_consumption()
```

`dc_live` continues past 2003. This book uses 1930–2003:

```python
import polars as pl
import plotnine as p9

dc = pl.read_csv("data/consumption_annual.csv")
(
    p9.ggplot(dc.to_pandas(), p9.aes("year", "dc"))
    + p9.geom_line()
    + p9.labs(x="Year", y="Δc", title="Real per-capita ND+S growth, 1930–2003")
)
```

![Real per-capita ND+S growth](figures/consumption_growth.svg)

<p class="caption">Annual log growth of real per-capita nondurables plus services, 1930–2003.</p>

The PCE deflator (`DPCERD3A086NBEA`) turns nominal CRSP dividends into reals. `lrr.load_deflator()` is the wrapper. The shipped panel is already deflated.

## CRSP, then Campbell–Shiller dividends

One `tf.download_data` call is enough to see the companion pattern. Filters, delisting, and CCM are in the Tidy Finance WRDS chapter.

```python
import tidyfinance as tf
import lrrcs as lrr

tf.set_wrds_credentials()
crsp = tf.download_data(
    domain="WRDS",
    dataset="crsp_monthly",
    start_date="1925-12-01",
    end_date="2003-12-31",
    version="v1",
    additional_columns=["retx"],
)
```

Tidy Finance gives you returns. It does not build dividends. Campbell and Shiller infer them from the gap between the return with dividends (`ret`) and the capital-gain return (`retx`):

$$
D_t = (r_t - r_t^{x})\, V_{t-1}.
$$

```python
# toy month: r = 0.02, r^x = 0.01, V = 100 → D = 1
d = (0.02 - 0.01) * 100
```

Then `lrr.campbell_shiller_annual(ret, retx, deflator)` compounds to annual real dividend growth and year-end \(P/D\). You do not need WRDS to finish this page: the Market rows of `data/annual_panel.csv` already store `dgrowth` and `pd`.

```python
import polars as pl
import plotnine as p9

dc = pl.read_csv("data/consumption_annual.csv")
panel = pl.read_csv("data/annual_panel.csv")
mkt = panel.filter(pl.col("claim") == "Market").join(dc, on="year")

(
    p9.ggplot(mkt.to_pandas(), p9.aes("dc", "dgrowth"))
    + p9.geom_point()
    + p9.labs(x="Δc", y="Market Δd", title="Cash flows, not returns")
)

(
    p9.ggplot(
        mkt.with_columns(pl.col("pd").log().alias("log_pd")).to_pandas(),
        p9.aes("year", "log_pd"),
    )
    + p9.geom_line()
    + p9.labs(x="Year", y="log(P/D)", title="Market price–dividend, 1930–2003")
)
```

![Market dividend growth against consumption growth](figures/market_dd_vs_dc.svg)

<p class="caption">Market dividend growth against consumption growth. The objects are cash flows, not average returns.</p>

![Market log price–dividend](figures/market_log_pd.svg)

<p class="caption">Market $$\log(P/D)$$, 1930–2003. The Euler equation has to match this later.</p>

There is no $$x_t$$ overlay on this page.

## Real T-bill and the annual panel

The real safe rate comes from CRSP index files (`mcti`: T-bill and CPI), not from Ken French’s risk-free column. The shipped file is `data/rf_annual.csv`.

The claims panel puts June book-to-market quintiles (NYSE breaks — Tidy Finance’s `assign_portfolio`) together with Campbell–Shiller dividends. Historical Davis–Fama–French book equity fills the early Compustat gap inside `lrr.build_annual_panel`. Optional rebuild:

```python
import lrrcs as lrr

bm = lrr.build_annual_panel(refresh=False)
print(lrr.table_i(bm))
```

| claim | E[R] % | σ(R) % | E[Δd] % | σ(Δd) % | E[log P/D] |
|:---|---:|---:|---:|---:|---:|
| Growth | 7.49 (1.93) | 20.02 | 0.33 (1.16) | 14.35 | 3.62 (0.17) |
| Value | 13.67 (1.63) | 29.67 | 3.53 (4.13) | 47.72 | 3.34 (0.19) |
| Market | 8.52 (1.75) | 20.10 | 0.92 (0.94) | 11.02 | 3.33 (0.13) |

Returns and dividend growth are percent per year. Numbers in parentheses are Newey–West standard errors. This is `lrr.table_i` on the shipped 1930–2003 panel.

`refresh=True` hits WRDS again. The rest of this book reads `data/annual_panel.csv`, `data/consumption_annual.csv`, and `data/rf_annual.csv`.

Next: [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}) for the recipe, or skip to [The market]({{ '/time-series.html' | relative_url }}).
