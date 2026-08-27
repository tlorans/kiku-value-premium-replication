---
title: The Cross Section
nav_order: 6
---

# The Cross Section
{: .no_toc }

1. TOC
{:toc}

Value stocks have out-earned growth stocks by about six percentage points a year over this sample. Why? "They're cheap" is not an answer — it restates the fact. "They have higher betas" is an answer, but a false one: their market betas sit near one. An equilibrium answer must name the *risk* the extra return pays for, measure that risk somewhere other than in the returns themselves, and then deliver both facts at once — the higher premium *and* the lower price–dividend ratio.

Here is what makes this chapter the payoff of the book: nothing about the household changes. Same preferences, same consumption process, same Euler equation as [The Time Series]({{ '/time-series.html' | relative_url }}). A model that needed a new discount rate for every asset class would just be DCF with extra steps. Instead, each claim brings only its cash-flow numbers — and value's dividends, it turns out, are levered to long-run consumption news far harder than growth's. The six-percent gap and value's cheaper valuation are facts to explain, not numbers you feed the calibrator. Average returns never enter the cash-flow step.

We use the following packages. Run the chunks **in order**: later snippets reuse `dc`, `panel`, and `y`.

```python
import numpy as np
import pandas as pd
import polars as pl
import plotnine as p9
import lrrcs as lrr

dc = pl.read_csv("data/consumption_annual.csv").sort("year")
panel = pl.read_csv("data/annual_panel.csv")
y = dc["dc"].to_numpy()
```

## Preparing the sample

[Financial data]({{ '/financial-data.html' | relative_url }}) already formed June book-to-market quintiles of ordinary shares, NYSE breakpoints (Fama and French 1993). Growth is the bottom fifth. Value is the top fifth. Dividends are Campbell–Shiller from `ret` versus `retx`. Sample: 1930–2003. We do not rebuild the sort.

```python
wide = panel.pivot(index="year", on="claim", values="ret")
wide.head()
{c: round(float(panel.filter(pl.col("claim") == c)["ret"].mean() * 100), 2)
 for c in ("Growth", "Value", "Market")}
```

```text
{'Growth': 7.49, 'Value': 13.67, 'Market': 8.52}
```

A note on vintages, once: our reconstruction prints 7.49 / 13.67 / 8.52, while Kiku's sample — a slightly different CRSP vintage — prints 7.81 / 13.88 / 8.56. Whenever a data column below shows her numbers, that is why. The gap is about six percent either way, and value is also *cheaper*: a lower valuation alongside a higher risk premium. Both facts, together, are the target.

|  | E[R] % | σ(R) % | E[log P/D] |
|:---|---:|---:|---:|
| Growth | 7.81 (1.98) | 20.2 | 3.61 (0.18) |
| Value | 13.88 (1.74) | 29.9 | 3.25 (0.12) |
| Market | 8.56 (1.79) | 20.1 | 3.34 (0.13) |

```python
print(lrr.table_i(panel.to_pandas() if hasattr(panel, "to_pandas") else panel))
```

The realized spread is positive in most years. Value's \(\log P/D\) sits below growth's throughout the sample.

```python
spread = (
    wide.with_columns((pl.col("Value") - pl.col("Growth")).alias("spread"))
    .select("year", "spread")
)
(
    p9.ggplot(spread.to_pandas(), p9.aes("year", "spread"))
    + p9.geom_col()
    + p9.geom_hline(yintercept=0, color="#888888")
    + p9.labs(x="Year", y="Value − growth return", title="Realized value minus growth")
)
vg = panel.filter(pl.col("claim").is_in(["Growth", "Value"]))
(
    p9.ggplot(
        vg.with_columns(pl.col("pd").log().alias("log_pd")).to_pandas(),
        p9.aes("year", "log_pd", color="claim"),
    )
    + p9.geom_line()
    + p9.labs(x="Year", y="log(P/D)", title="Value and growth price–dividend")
)
```

![Realized value minus growth](figures/vg_spread.svg)

<p class="caption">Realized value minus growth, 1930–2003. The bars are positive in most years.</p>

![Value and growth price–dividend](figures/vg_log_pd.svg)

<p class="caption">Value's $$\log(P/D)$$ sits below growth's. Both the premium and the cheaper valuation are facts to explain.</p>

Before reaching for anything exotic, kill the obvious story. If value simply had a much larger market beta, the CAPM would do and this book would be short. OLS of each claim's return on the market return:

```python
rm = panel.filter(pl.col("claim") == "Market").sort("year")["ret"].to_numpy()
rm_d = rm - rm.mean()

def capm_beta(claim):
    r = panel.filter(pl.col("claim") == claim).sort("year")["ret"].to_numpy()
    r_d = r - r.mean()
    return float(np.dot(rm_d, r_d) / np.dot(rm_d, rm_d))

{c: round(capm_beta(c), 2) for c in ("Growth", "Value")}
```

```text
{'Growth': 0.95, 'Value': 1.28}
```

Value's beta is a bit above one on this reconstruction — nowhere near enough to explain six percent — and the paper's vintage has both near 1.03. The premium is not a market-beta fact. So what risk is it?

## Two cash-flow exposures

The household and the consumption process stay those of [The Time Series]({{ '/time-series.html' | relative_url }}). Each claim differs only in four cash-flow numbers: mean dividend growth $$\mu$$, monthly loading $$\phi$$ on $$x_t$$, residual scale $$\varphi$$, and short-run correlation $$\alpha$$. This is the cross section's entire cash-flow model — four numbers per claim, estimated from dividends and consumption.

The two-year MA of lagged consumption is the same regressor as on The Time Series. `lrr.expected_growth_proxy` is that MA. Equation (19) is OLS of dividend growth on it. Look at the right-hand side: no return anywhere.

```python
ma = lrr.expected_growth_proxy(y, window=2)

def phi_hat(claim):
    dd = (
        panel.filter(pl.col("claim") == claim)
        .join(dc, on="year")
        .sort("year")["dgrowth"]
        .to_numpy()
    )
    mask = np.isfinite(ma) & np.isfinite(dd)
    x = ma[mask] - ma[mask].mean()
    e = dd[mask] - dd[mask].mean()
    return float(np.dot(x, e) / np.dot(x, x))

{c: round(phi_hat(c), 3) for c in ("Growth", "Value", "Market")}
```

```text
{'Growth': -0.267, 'Value': 12.129, 'Market': 0.722}
```

There is the risk, in the cash flows where the model said it would be. Value's dividend growth rises hard with the slow component of consumption; growth's barely responds — on this reconstruction it even leans the other way. The point estimates are noisy (seventy-two annual observations), so the *ranking* is the check, and the ranking matches Kiku's Table VI: $$-0.38$$ / $$2.16$$ / $$0.66$$, same order. Plot dividend growth against that MA. These are cash flows, not returns.

```python
plot_df = (
    panel.filter(pl.col("claim").is_in(["Growth", "Value"]))
    .join(dc.with_columns(pl.Series("ma", ma)).select("year", "ma"), on="year")
    .filter(pl.col("ma").is_finite() & pl.col("dgrowth").is_finite())
)
(
    p9.ggplot(plot_df.to_pandas(), p9.aes("ma", "dgrowth", color="claim"))
    + p9.geom_point()
    + p9.labs(
        x="Two-year MA of lagged Δc",
        y="Δd",
        title="Cash-flow exposure, not returns",
    )
)
```

![Dividend growth against the MA](figures/vg_dd_vs_ma.svg)

<p class="caption">Value and growth dividend growth against the two-year MA of lagged consumption. Value's slope is steeper. Average returns never entered.</p>

The solver wants monthly $$\phi$$. Table II: $$\phi_{\text{value}}=6.2$$, $$\phi_{\text{growth}}=2.6$$, $$\phi_{\text{market}}=2.8$$. Value gets the larger $$\phi$$ because its cash flows load more on the persistent growth-rate component — not because it had a larger average return. `lrr.calibrate_from_data` wraps the annual OLS; then we read off Table II.

```python
def dd(claim):
    return (
        panel.filter(pl.col("claim") == claim)
        .join(dc, on="year")
        .sort("year")["dgrowth"]
        .to_numpy()
    )

div = lrr.calibrate_from_data(
    y,
    frequency="annual",
    window=2,
    long=dd("Value"),
    short=dd("Growth"),
    market=dd("Market"),
)
lrr.print_calibration_summary(div)
params = lrr.get_table_ii_params()
params.dividends["value"].phi, params.dividends["growth"].phi
```

```text
(6.2, 2.6)
```

There is no argument for returns. The function will not take one.

## Elasticity of price–dividend to x_t

Same preferences as The Time Series — nothing re-tuned. The Euler equation and the IMRS are those of [the long-run risks model]({{ '/long-run-risks-model.html' | relative_url }}). The elasticity of log $$P/D$$ to $$x_t$$ is the expression where cash flows meet the household, $$A_1=(\phi-1/\psi)/(1-\kappa_1\rho)$$, and only $$\phi$$ differs across claims. With Table II's monthly $$\phi$$:

```python
psi, rho = 1.5, 0.98
for name, phi, zbar in (("growth", 2.6, 3.65), ("value", 6.2, 3.10)):
    kappa1 = np.exp(zbar) / (1.0 + np.exp(zbar))
    A1 = (phi - 1.0 / psi) / (1.0 - kappa1 * rho)
    print(name, round(A1, 1))
```

```text
growth 43.1
value  88.9
```

One gap in cash-flow leverage, two consequences. Value's price–dividend ratio is about twice as elastic to long-run consumption news, so its valuation is more fragile exactly when the Epstein–Zin household is most miserable — and it must therefore offer high ex-ante compensation. The premium and the cheap valuation are not two facts the model happens to fit; they are one fact seen from two sides.

## Solve and check rankings

`solve_analytical` and `ModelSolver` resolve either pair. The market key remains the time-series check that the same equilibrium still prices the aggregate claim.

```python
sol = lrr.solve_analytical(params)
lrr.print_long_short_premium(sol)
```

```text
Approximate annualized long-run risk premia:
  growth  :   0.39%
  value   :   0.80%
  market  :   0.34%
Value-growth spread from long-run risks: 0.40%
A1 (PD elasticity to x): growth=43.1, value=88.9
Price of long-run risk Lambda_eps = 5.95
```

The 0.40 percent is only the long-run *piece*. The full Euler-equation gap is larger. `lrr.compute_asset_pricing_moments` integrates that Euler equation on a grid, the same objects as on The Time Series. Kiku's Table VII (1000 samples) is the comparison we want. The standard has not changed: a match on the premium with the wrong price–dividend ranking is a fail — the equilibrium objects come as a pair.

|  | E[R] % data | E[R] % model | E[pd] data | E[pd] model |
|:---|---:|---:|---:|---:|
| Growth | 7.81 (1.98) | 6.07 (2.91) | 3.61 (0.18) | 3.65 (0.06) |
| Value | 13.88 (1.74) | 11.36 (4.30) | 3.25 (0.12) | 3.10 (0.15) |
| Market | 8.56 (1.79) | 7.53 (2.69) | 3.34 (0.13) | 3.24 (0.07) |
| Risk-free | 0.91 (0.39) | 1.58 (0.01) |  |  |

Look at the whole table, row by row. The model gap is about 5.3 percent against about 6 in the data. Mean price–dividend levels come out near 24.7 on value versus 39.8 on growth — the high-premium claim is the low-valuation claim, in the model as in the data. The market row is the time-series check: the same equilibrium still prices the aggregate claim, so the cross section came free, not at the market's expense.

And here is the result I find most satisfying. The model's ratio of value to growth CAPM betas is 0.92 — value's market beta is *lower*, as in the paper's vintage, while its premium is five points higher. The model does not merely deliver the value premium; it delivers the value premium *as a CAPM anomaly*. Inside this economy, an econometrician running CAPM regressions would find exactly the puzzle the empirical literature found, while the household sees no puzzle at all: it is paid for the low-frequency consumption risk embodied in cash flows, which market betas — dominated by transitory price fluctuations — cannot see.

What would failure have looked like? Value's risk premium below growth's; value's price–dividend ratio above growth's; or value's CAPM beta so much larger that covariance with the market would have been enough. None of those happened.

```python
print("A1 value / A1 growth", round(sol.A1["value"] / sol.A1["growth"], 2))
```

```text
A1 value / A1 growth 2.06
```

![Long-run risk premia](figures/lr_premium_decomposition.svg)

<p class="caption">Analytical long-run premia. The gap is $$\phi_V=6.2$$ versus $$\phi_G=2.6$$, scaled by $$\rho=0.98$$ and the Epstein–Zin price of long-run news.</p>

## Key takeaways

- The six-percent premium and value's cheaper valuation are facts to explain, not calibration targets. Average returns never enter the inputs.
- Nothing about the household changes across assets: one set of preferences, one consumption process, one Euler equation. The cross section costs zero new discount-rate parameters.
- The claims differ only in estimated cash-flow exposures, and the ranking is the check: value loads hard on long-run consumption news, growth barely at all.
- One gap in $$\phi$$ delivers the pair: value's higher premium and lower price–dividend ratio are the same fact seen from two sides.
- The model reproduces the CAPM *anomaly* itself — value's model beta is lower (ratio 0.92) while its premium is higher. The priced risk lives in cash flows, where market betas cannot see it.
- The market row still matches: the equilibrium prices the asset class and the cross section together.

## Exercises

1. Set $$\phi_{\text{value}}=\phi_{\text{growth}}=2.6$$ and recompute $$A_1$$ and the long-run spread from `solve_analytical`. Where did the ranking go?
2. Drop 1930–1945 from the OLS in Two cash-flow exposures. Does value still have the larger $$\tilde\phi$$?
3. Using the model's $$A_1$$ ratio 2.06, what $$\phi_{\text{value}}$$ would you need if $$\phi_{\text{growth}}$$ stayed 2.6 and you wanted the two elasticities equal?
