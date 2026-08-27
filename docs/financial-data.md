---
title: Financial data
nav_order: 3
---

# Financial data
{: .no_toc }

1. TOC
{:toc}

Long-run risks is a *cash-flow* model. Before any Euler equation you need how consumption grows, how each claim’s dividends grow, and a real safe rate. Average stock returns are a fact to explain later. They are not an input here.

Tidy Finance already shows how to pull CRSP, Compustat, and CCM, and how to store downloads: [Accessing and managing financial data](https://www.tidy-finance.org/chapters/accessing-and-managing-financial-data.html) and [WRDS, CRSP, and Compustat](https://www.tidy-finance.org/chapters/wrds-crsp-and-compustat.html). Credentials are `tf.set_wrds_credentials()`; see [Installation]({{ '/installation.html' | relative_url }}). This page does not redo those extracts. It builds the series Tidy Finance does not: NIPA consumption, Campbell–Shiller dividends, the PCE deflator, a real T-bill, and the 1930–2003 claims panel.

The pricing chapters use 1930–2003 (Kiku 2006 / Bansal and Yaron 2004). Live FRED continues past 2003. After each construction we cut to that window so everyone prices the same sample.

```python
import polars as pl
import plotnine as p9
import tidyfinance as tf
import lrrcs as lrr

start, end = 1930, 2003
```

## Consumption

The household in this book consumes real per-capita *nondurables plus services*. Durables look more like investment (Hall; Mehra and Prescott; Bansal and Yaron). We divide by population so headcount growth is not a productivity shock. The NIPA quantity indexes are on FRED; no WRDS login.

```python
import polars as pl

def fred_annual(series_id: str) -> pl.DataFrame:
    url = f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={series_id}"
    raw = pl.read_csv(url)
    return raw.with_columns(
        pl.col("observation_date").str.slice(0, 4).cast(pl.Int32).alias("year"),
        pl.col(series_id).alias("value"),
    ).select("year", "value")

nd = fred_annual("DNDGRA3A086NBEA").rename({"value": "nd"})
sv = fred_annual("DSERRA3A086NBEA").rename({"value": "sv"})
pop = fred_annual("B230RC0A052NBEA").rename({"value": "pop"})
nd.head(3)
```

```text
shape: (3, 2)
┌──────┬────────┐
│ year ┆ nd     │
│ 1929 ┆ 11.737 │
│ 1930 ┆ 11.125 │
│ 1931 ┆ 11.006 │
└──────┴────────┘
```

Quantity indexes plus population give a per-capita consumption *level*. Log difference is growth:

```python
import polars as pl
import plotnine as p9
import lrrcs as lrr

levels = (
    nd.join(sv, on="year")
    .join(pop, on="year")
    .with_columns(((pl.col("nd") + pl.col("sv")) / pl.col("pop")).alias("c"))
    .with_columns(pl.col("c").log().diff().alias("dc"))
    .drop_nulls()
)
dc = levels.filter((pl.col("year") >= start) & (pl.col("year") <= end)).select("year", "dc")
dc.head()
```

```text
 year     dc
 1930  -0.053
 1931  -0.024
 1932  -0.088
 1933  -0.021
 1934   0.062
```

1932 is the Depression trough: consumption falls almost nine percent. Mean growth 1930–2003 is 1.75 percent per year.

```python
import plotnine as p9

(
    p9.ggplot(dc.to_pandas(), p9.aes("year", "dc"))
    + p9.geom_line()
    + p9.labs(x="Year", y="Δc", title="Real per-capita ND+S growth, 1930–2003")
)
```

Same three FRED series and the same log difference, as a one-liner:

```python
dc_all = lrr.load_consumption()   # pandas Series, indexed by year
dc = dc_all.loc[start:end]
```

`lrr.consumption_growth_from_levels(nd, sv, pop)` is just the level-to-growth step if you already downloaded the indexes.

![Real per-capita ND+S growth](figures/consumption_growth.svg)

<p class="caption">Annual log growth of real per-capita nondurables plus services, 1930–2003. The 1932 drop is the Depression, not a plotting glitch.</p>

CRSP prices and dividends are nominal. The PCE implicit price deflator (`DPCERD3A086NBEA`) turns them into consumption goods:

```python
defl = lrr.load_deflator()
```

## Market dividends

CRSP stores *returns*, not a dividend file. The return with dividends is `ret`. The capital-gain return is `retx`. Campbell and Shiller recover the dividend as the gap, scaled by a cumulated price index $$V$$:

$$
D_t=(r_t-r_t^{x})\,V_{t-1},\qquad V_t=V_{t-1}(1+r_t^{x}).
$$

Tidy Finance’s CRSP extract is in [WRDS, CRSP, and Compustat](https://www.tidy-finance.org/chapters/wrds-crsp-and-compustat.html). For Campbell–Shiller you also need `retx` and the 1925–2003 file, so `version="v1"`:

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

Ordinary shares, NYSE/AMEX/NASDAQ, and delisting (Fama–French −30% on performance codes 400–599, applied to `retx` as well as `ret`) stay in `lrr.build_annual_panel`. The identity itself is easiest to see on a year of made-up months. Start $$V=100$$, every month $$r^{x}=1\%$$ and $$r=1.2\%$$:

```python
import pandas as pd
import lrrcs as lrr

dates = pd.date_range("2000-01-31", periods=12, freq="ME")
retx = pd.Series(0.01, index=dates)
ret = pd.Series(0.012, index=dates)
defl = pd.Series({2000: 1.0})
cs = lrr.campbell_shiller_annual(ret, retx, defl)
cs[["year", "div", "v", "pd"]]
```

```text
 year   div       v     pd
 2000  2.54  112.68  44.42
```

Each month the dividend is $$0.002\times V_{t-1}$$. The price index compounds at 1% per month to 112.68. Year-end $$P/D$$ is 44.4. On CRSP, pass the value-weighted `ret` / `retx` (and the deflator) the same way. `lrrcs` still has to do this step: Tidy Finance does not ship Campbell–Shiller dividends.

The market row of the claims panel *is* that procedure on CRSP ordinary shares, 1930–2003. `lrr.build_annual_panel` runs it (and writes `data/annual_panel.csv`). `refresh=False` reuses `data/raw/*.parquet` when present so you are not billed a WRDS round-trip for a chart.

```python
import numpy as np
import plotnine as p9
import lrrcs as lrr

panel = lrr.build_annual_panel(refresh=False)
dc = lrr.load_consumption().loc[start:end].rename("dc").reset_index()
mkt = panel.loc[panel["claim"] == "Market"].merge(dc, on="year")

(
    p9.ggplot(mkt, p9.aes("dc", "dgrowth"))
    + p9.geom_point()
    + p9.labs(x="Δc", y="Market Δd", title="Cash flows, not returns")
)
(
    p9.ggplot(mkt.assign(log_pd=np.log(mkt["pd"])), p9.aes("year", "log_pd"))
    + p9.geom_line()
    + p9.labs(x="Year", y="log(P/D)", title="Market price–dividend, 1930–2003")
)
```

![Market dividend growth against consumption growth](figures/market_dd_vs_dc.svg)

<p class="caption">Market dividend growth against consumption growth. Both series are constructed (NIPA; Campbell–Shiller on CRSP). Average returns never entered.</p>

![Market log price–dividend](figures/market_log_pd.svg)

<p class="caption">Market $$\log(P/D)$$ from the same Campbell–Shiller price and dividend. The Euler equation has to match this later.</p>

## Real T-bill

The model’s safe rate is a real T-bill, not Ken French’s `RF` column (that one is a nominal one-month yield). CRSP’s `mcti` file has the 90-day bill (`t90ret`) and a CPI index. Subtract a twelve-month moving average of log inflation, then average inside the calendar year:

```python
import lrrcs as lrr

# t90 and cpi are monthly Series from CRSP mcti
rf = lrr.real_rf_from_monthly(t90, cpi)
```

`lrr.build_annual_panel` writes `data/rf_annual.csv`. Mean real bill 1930–2003 is about 0.9 percent.

## Value, growth, and the panel

Value and growth are June book-to-market quintiles of ordinary shares, NYSE breakpoints (Fama and French 1993). Tidy Finance’s `assign_portfolio` / `breakpoint_options(n_portfolios=5, breakpoints_exchanges="NYSE")` is the sort. Book equity is Compustat (`seq`, `ceq`, preferred stock, deferred taxes) merged through CCM.

Compustat is thin before the 1960s. Davis, Fama, and French backfill Moody’s book equity. That file is public (Ken French’s library), not WRDS:

```python
import io
import zipfile
import urllib.request

url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Historical_BE_Data.zip"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=60) as resp:
    blob = resp.read()
with zipfile.ZipFile(io.BytesIO(blob)) as zf:
    text = zf.read(zf.namelist()[0]).decode("latin-1")
text.splitlines()[:5]
```

Each line is a `permno` and a vector of annual book-equity values starting in 1926. `lrr.build_annual_panel` parses it, splices it onto Compustat, forms the quintiles, value-weights, and runs Campbell–Shiller on growth (quintile 1), value (quintile 5), and the market.

```python
import lrrcs as lrr

tf.set_wrds_credentials()          # once; skip if the cache is already there
panel = lrr.build_annual_panel(refresh=False)
print(lrr.table_i(panel))
```

`refresh=True` hits WRDS and Ken French again. `refresh=False` rebuilds from `data/raw/*.parquet` if present, otherwise from the shipped CSVs.

| claim | E[R] % | σ(R) % | E[Δd] % | σ(Δd) % | E[log P/D] |
|:---|---:|---:|---:|---:|---:|
| Growth | 7.49 (1.93) | 20.02 | 0.33 (1.16) | 14.35 | 3.62 (0.17) |
| Value | 13.67 (1.63) | 29.67 | 3.53 (4.13) | 47.72 | 3.34 (0.19) |
| Market | 8.52 (1.75) | 20.10 | 0.92 (0.94) | 11.02 | 3.33 (0.13) |

Returns and dividend growth are percent per year. Numbers in parentheses are Newey–West standard errors. Value earned more *and* was cheaper (lower $$P/D$$). Those are the two columns the model has to match. Neither entered the cash-flow construction.

The pricing chapters read the 1930–2003 files that pipeline writes: `data/consumption_annual.csv`, `data/annual_panel.csv`, `data/rf_annual.csv`. Next: [Cash flows, then prices]({{ '/cash-flows-then-prices.html' | relative_url }}), or [The market]({{ '/time-series.html' | relative_url }}).
