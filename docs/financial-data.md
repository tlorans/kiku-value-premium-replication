---
title: Financial data
nav_order: 3
---

# Financial data
{: .no_toc }

1. TOC
{:toc}

This is a general-equilibrium model of asset prices and risk premia. Before any Euler equation you need the cash flows in which low-frequency risks are embodied: how consumption grows, how each claim’s dividends are exposed to low- and high-frequency consumption shocks, and a real safe rate.

Long-run risks are a small but highly persistent component that governs consumption growth, plus time-variation in the conditional volatility of consumption — news about future economic uncertainty. Firms are distinguished by the exposure of their dividends to low- versus high-frequency consumption shocks. Valuations and risk premia depend on the amount of low-frequency risks embodied in cash flows. Average stock returns are a fact the equilibrium has to explain. They are not an input here. Later pages price these cash flows with time-non-separable Epstein–Zin preferences, whose marginal rate of substitution depends on the forward-looking return on the aggregate wealth portfolio.

Tidy Finance already shows CRSP, Compustat, CCM, and how to store downloads: [Accessing and managing financial data](https://www.tidy-finance.org/chapters/accessing-and-managing-financial-data.html) and [WRDS, CRSP, and Compustat](https://www.tidy-finance.org/chapters/wrds-crsp-and-compustat.html). Credentials are `tf.set_wrds_credentials()`; see [Installation]({{ '/installation.html' | relative_url }}). This page does not redo those extracts. It builds the series Tidy Finance does not: NIPA consumption, Campbell–Shiller dividends, the PCE deflator, a real T-bill, and the 1930–2003 claims panel.

The pricing chapters use 1930–2003 (Kiku 2006 / Bansal and Yaron 2004). Live FRED continues past 2003; after constructing we cut to that window. Run the chunks **in order**.

```python
import io
import zipfile
import urllib.request
import numpy as np
import pandas as pd
import polars as pl
import plotnine as p9
import tidyfinance as tf
import lrrcs as lrr

start, end = 1930, 2003
```

## Consumption

The representative agent consumes real per-capita *nondurables plus services*. Durables look more like investment (Hall; Mehra and Prescott; Bansal and Yaron). We divide by population so headcount growth is not a consumption shock. Long-run risks are a small but highly persistent component that governs consumption growth in *this* series, together with time-variation in its conditional volatility. The NIPA quantity indexes are on FRED — public, no WRDS.

```python
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
 year     nd
 1929  11.737
 1930  11.125
 1931  11.006
```

Join on year, form the per-capita level, then take log differences. That *is* consumption growth.

```python
levels = (
    nd.join(sv, on="year")
    .join(pop, on="year")
    .with_columns(((pl.col("nd") + pl.col("sv")) / pl.col("pop")).alias("c"))
    .with_columns(pl.col("c").log().diff().alias("dc"))
    .drop_nulls()
)
dc = levels.filter((pl.col("year") >= start) & (pl.col("year") <= end)).select("year", "dc")
dc.head()
print(dc["dc"].mean() * 100, dc["dc"].std() * 100, dc.height)
```

```text
 year     dc
 1930  -0.053
 1931  -0.024
 1932  -0.088
 1933  -0.021
 1934   0.062

1.75  2.37  74
```

1932 is the Depression trough: consumption falls almost nine percent. Mean growth 1930–2003 is 1.75 percent, volatility 2.37 percent, 74 years.

```python
(
    p9.ggplot(dc.to_pandas(), p9.aes("year", "dc"))
    + p9.geom_line()
    + p9.labs(x="Year", y="Δc", title="Real per-capita ND+S growth, 1930–2003")
)
```

![Real per-capita ND+S growth](figures/consumption_growth.svg)

<p class="caption">Annual log growth of real per-capita nondurables plus services, 1930–2003. The 1932 drop is the Depression, not a plotting glitch.</p>

If the three FRED series are already pandas with a year index, `lrr.consumption_growth_from_levels(nd, sv, pop)` is the log-difference step.

The same three FRED series and the same log difference:

```python
dc_pkg = lrr.load_consumption().loc[start:end]
dc_pkg.mean(), float(dc["dc"].mean())
```

CRSP prices and dividends are nominal. The PCE implicit price deflator (`DPCERD3A086NBEA`) converts them into consumption units. Download it the same way as the quantity indexes, or call `lrr.load_deflator()`.

```python
defl_pl = fred_annual("DPCERD3A086NBEA").rename({"value": "defl"})
defl = pd.Series(
    defl_pl["defl"].to_numpy(),
    index=defl_pl["year"].to_numpy(),
    name="defl",
)
defl.loc[start:end].head()
```

## Market dividends

CRSP stores *returns*, not a dividend file. The return with dividends is `ret`. The capital-gain return is `retx`. Campbell and Shiller (1988) recover the dividend as the gap, scaled by a cumulated price index $$V$$:

$$
D_t=(r_t-r_t^{x})\,V_{t-1},\qquad V_t=V_{t-1}(1+r_t^{x}).
$$

Tidy Finance’s CRSP extract is in [WRDS, CRSP, and Compustat](https://www.tidy-finance.org/chapters/wrds-crsp-and-compustat.html). For this identity you also need `retx` and the 1925–2003 file (`version="v1"`):

```python
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

Ordinary shares, NYSE/AMEX/NASDAQ, and delisting (Fama–French −30% on performance codes 400–599, applied to `retx` as well as `ret`) live inside `lrr.build_annual_panel`. The identity itself does not need WRDS. Start $$V=100$$. Every month $$r^{x}=1\%$$ and $$r=1.2\%$$, so each dividend is 0.2 percent of the lagged price index. Compound for a year:

```python
dates = pd.date_range("2000-01-31", periods=12, freq="ME")
retx = pd.Series(0.01, index=dates)
ret = pd.Series(0.012, index=dates)

v = 100.0
rows = []
year_div, year_v, year_ret = {}, {}, {}
for dt in dates:
    d = (ret.loc[dt] - retx.loc[dt]) * v
    v = v * (1.0 + retx.loc[dt])
    y = int(dt.year)
    year_div[y] = year_div.get(y, 0.0) + max(d, 0.0)
    year_v[y] = v
    year_ret[y] = year_ret.get(y, 1.0) * (1.0 + ret.loc[dt])
pd.DataFrame(
    {"year": [2000], "div": [year_div[2000]], "v": [year_v[2000]],
     "pd": [year_v[2000] / year_div[2000]]}
)
```

```text
 year   div       v     pd
 2000  2.54  112.68  44.42
```

The price index compounds at 1% per month to 112.68. Year-end $$P/D$$ is 44.4. Deflate `div` and `v` by the PCE index, then take log differences of real dividends for $$\Delta d$$. `lrr.campbell_shiller_annual(ret, retx, defl)` is that loop plus deflation. Tidy Finance does not ship this.

On CRSP, pass the value-weighted `ret` / `retx` of ordinary shares the same way. `lrr.build_annual_panel` does it for growth, value, and the market, and writes `data/annual_panel.csv`. `refresh=False` reuses `data/raw/*.parquet` when present.

```python
try:
    panel = lrr.build_annual_panel(refresh=False)
except Exception:
    panel = pd.read_csv("data/annual_panel.csv")
if not isinstance(panel, pl.DataFrame):
    panel = pl.from_pandas(panel)
mkt = panel.filter(pl.col("claim") == "Market").join(dc, on="year")
mkt.select("year", "ret", "dgrowth", "pd", "dc").head()
```

```python
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

<p class="caption">Market dividend growth against consumption growth. Both series are constructed (NIPA; Campbell–Shiller on CRSP). Average returns never entered.</p>

![Market log price–dividend](figures/market_log_pd.svg)

<p class="caption">Market $$\log(P/D)$$ from the same Campbell–Shiller price and dividend. The Euler equation has to match this later.</p>

## Real T-bill

The model’s safe rate is a *real* T-bill, not Ken French’s nominal `RF`. CRSP `mcti` has the 90-day bill (`t90ret`) and a CPI index. Subtract a twelve-month moving average of log inflation, then average inside the year:

```python
idx = pd.date_range("2000-01-31", periods=24, freq="ME")
t90 = pd.Series(0.004, index=idx)
cpi = pd.Series(100.0 * (1.002 ** np.arange(24)), index=idx)
inflation = np.log(cpi / cpi.shift(1))
real_m = t90 - inflation.rolling(12).mean()
rf_toy = real_m.resample("YE").mean()
rf_toy
```

```text
2000-12-31    NaN
2001-12-31    0.002
```

The first year is missing because of the twelve-month inflation window. `lrr.real_rf_from_monthly(t90, cpi)` is that transformation. On CRSP, pass `mcti.t90ret` and `mcti.cpi`. `build_annual_panel` writes `data/rf_annual.csv`.

## Value, growth, and the panel

Value and growth are June book-to-market quintiles of ordinary shares, NYSE breakpoints (Fama and French 1993). In the data, as in the model, value firms are highly exposed to long-run consumption shocks; growth firms are driven more by short-lived fluctuations in consumption. That is the cash-flow fact the equilibrium will turn into valuations and premia. Tidy Finance’s `assign_portfolio(..., breakpoint_options=tf.breakpoint_options(n_portfolios=5, breakpoints_exchanges="NYSE"))` is the sort. Book equity is Compustat (`seq`, `ceq`, preferred stock, deferred taxes) merged through CCM.

Compustat is thin before the 1960s. Davis, Fama, and French backfill Moody’s book equity. That file is public:

```python
url = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/Historical_BE_Data.zip"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
with urllib.request.urlopen(req, timeout=60) as resp:
    blob = resp.read()
with zipfile.ZipFile(io.BytesIO(blob)) as zf:
    text = zf.read(zf.namelist()[0]).decode("latin-1")
text.splitlines()[:4]
```

Each line is a `permno` and a vector of annual book-equity values starting in 1926. `lrr.build_annual_panel` parses it, splices it onto Compustat, forms the quintiles, value-weights, and runs Campbell–Shiller on growth (quintile 1), value (quintile 5), and the market.

```python
print(lrr.table_i(panel))
```

`refresh=True` hits WRDS and Ken French again.

| claim | E[R] % | σ(R) % | E[Δd] % | σ(Δd) % | E[log P/D] |
|:---|---:|---:|---:|---:|---:|
| Growth | 7.49 (1.93) | 20.02 | 0.33 (1.16) | 14.35 | 3.62 (0.17) |
| Value | 13.67 (1.63) | 29.67 | 3.53 (4.13) | 47.72 | 3.34 (0.19) |
| Market | 8.52 (1.75) | 20.10 | 0.92 (0.94) | 11.02 | 3.33 (0.13) |

Returns and dividend growth are percent per year. Newey–West standard errors in parentheses. Value earned more *and* was cheaper: higher risk premia and lower valuations. Those are the two objects of the general equilibrium. Neither entered the cash-flow construction.

## Key takeaways

- Consumption is real per-capita ND+S from FRED. Long-run risks are a small but highly persistent component that governs this series, plus time-variation in its conditional volatility.
- CRSP stores returns. Dividends — the cash flows in which low- versus high-frequency risks are embodied — are Campbell–Shiller from `ret` minus `retx`.
- Value firms are highly exposed to long-run consumption shocks; growth firms are driven more by short-lived fluctuations. That ranking is in the dividends, not in average returns.
- Historical book equity is a public Ken French zip, because Compustat is thin before 1960.
- The 1930–2003 files that pipeline writes (`data/consumption_annual.csv`, `data/annual_panel.csv`, `data/rf_annual.csv`) are the sample whose *valuations and risk premia* [The market]({{ '/time-series.html' | relative_url }}) and [Value versus growth]({{ '/cross-section.html' | relative_url }}) have to match.

Next: [The long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}).
