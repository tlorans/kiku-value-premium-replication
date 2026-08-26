---
title: 6. Further applications
nav_order: 8
---

# 6. Further applications
{: .no_toc }

1. TOC
{:toc}

Sections 2–5 price book-to-market claims. After 2006 two further spreads entered the set of facts a consumption-based model must confront. Fama and French (2015) show that operating profitability and investment predict average returns in the same CRSP/Compustat universe I used for value, and that neither spread is a CAPM fact. I record those moments here and state the cash-flow restriction the long-run risks model imposes on them.

The restriction is the restriction of Section 4. Loadings $$(\mu,\phi,\varphi,\alpha)$$ are chosen from consumption and dividend growth. Average returns are not used. If the Euler equation then reproduces the published premia, the model prices the sort. If it does not, profitability and investment are a different puzzle from value.

## 6.1 Construction

Fama and French (2015) keep the June timing and NYSE breakpoints of Fama and French (1993). They add two characteristics implied by the dividend-discount identity. Holding expected cash flows fixed, a lower price requires a higher expected return. A lower price is also implied by lower expected profitability or higher expected investment. Average returns should therefore rise with profitability and fall with asset growth.

Operating profitability for the June-$$t$$ sort is revenues minus cost of goods sold, selling, general and administrative expense, and interest expense, divided by book equity, all for the fiscal year ending in $$t-1$$. Investment is the growth rate of total assets from $$t-2$$ to $$t-1$$. Independent sorts on size and each characteristic produce six value-weighted portfolios. RMW is the average of the two robust-profitability portfolios minus the average of the two weak-profitability portfolios. CMA is the analogous difference for conservative versus aggressive investment.

Novy-Marx (2013) documents a closely related premium using gross profits-to-assets. Hou, Xue, and Zhang (2015) obtain an analogous pair from return on equity and investment. I use the published 2×3 Fama–French factors because their construction is the direct continuation of the sorts in Section 2.

## 6.2 Average returns

Table 2 of Fama and French (2015) reports monthly 2×3 factor returns for July 1963–December 2013 (606 months).

|  | Mean | σ | $$t$$ |
|:---|---:|---:|---:|
| $$R_m-R_f$$ | 0.50 | 4.49 | 2.74 |
| SMB | 0.29 | 3.07 | 2.31 |
| HML | 0.37 | 2.88 | 3.20 |
| RMW | 0.25 | 2.14 | 2.92 |
| CMA | 0.33 | 2.01 | 4.07 |

Units are percent per month. Annualized, the profitability premium is about three percent and the investment premium about four. Both are smaller than the six-percent book-to-market gap of 1930–2003. Both are estimated in a postwar sample and are not artifacts of the Depression.

The underlying size-characteristic panels (their Table 1) show the same ranking without long–short construction. Among large stocks, monthly excess return rises from 0.39 percent in the weakest operating-profitability quintile to 0.57 percent in the strongest. Among small stocks, the most conservative investment quintile earned 1.01 percent against 0.35 percent for the most aggressive. As with value, market betas do not line up with these average returns. The CAPM does not price either sort.

## 6.3 Valuations and the status of HML

Value in Section 2 is the cheap claim: mean $$\log(P/D)$$ of 3.25 against 3.61 for growth. Profitability does not repeat that pattern. Novy-Marx (2013) shows that the high-profitability leg earns more and sells at a *higher* valuation ratio. A larger $$\phi$$ in Section 3 raises expected return and lowers the model price–dividend ratio. Profitability cannot therefore be obtained from Table II by renaming growth and value. Either expected dividend growth $$\mu$$ on the robust claim is high enough to offset a larger long-run loading, or the model fails the joint restriction on returns and prices.

Investment is closer to book-to-market. Conservative firms grow assets slowly. In the size-investment panel they occupy the high-return, typically cheaper side of the sort.

Fama and French (2015, Table 6) project each factor on the other four. The intercept of HML is absorbed once RMW and CMA are included. In that sample book-to-market is the valuation identity restated: high B/M firms are disproportionately the firms with weaker profitability or faster asset growth, after size and the market are controlled. That redundancy does not retract Sections 2–5. The objects priced there remain the 1930–2003 book-to-market quintiles. It does imply that profitability and investment are the two additional cash-flow sorts the model must face, not a third independent long-run-risk test alongside HML.

## 6.4 The cash-flow restriction

The model of Section 3 is a consumption process and a vector of dividend claims. Book-to-market does not appear. Any characteristic that yields a dividend series can be priced. I apply equation (19) to each leg of the new sorts,

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2} \Delta c_{t-k} + \varepsilon_t. \tag{19}
$$

The ranking of $$\tilde\phi$$ is the cash-flow fact. Kiku (2006) does not report these slopes. They are to be estimated, not taken from Table II.

Preferences and the aggregate consumption process remain those of Table II. Only `DividendParams` change. I map each sort onto the three claims the solver already prices.

| Sort | Low-return claim | High-return claim |
|:---|:---|:---|
| Book-to-market | growth | value |
| Operating profitability | weak | robust |
| Investment | aggressive | conservative |

The model prices the sort if three implications hold together, as they do for value in Section 5. First, the high-return leg’s estimated $$\tilde\phi$$ exceeds the low-return leg’s. Absent that gap there is no long-run cash-flow story. Second, the Euler equation, given only those cash-flow parameters, produces a premium of the same sign and of approximately the published magnitude — about three percent for RMW and about four percent for CMA over 1963–2013. Third, the model ranking of $$\log(P/D)$$ does not contradict the data. For investment that ranking is the value ranking. For profitability it is the joint restriction of a higher return and a higher valuation, which must come from $$\mu$$ as well as from $$\phi$$.

A reversal on the first implication means the factor is not a long-run cash-flow factor. A reversal on the second, with the first intact, means the Table II investor cannot be recycled. A reversal on the third means the single-loading mechanism that cheapens value while raising its premium is too tight for profitability.

```python
from kiku_value_premium.calibration import calibrate_from_data, estimate_long_run_leverage
from kiku_value_premium.model import get_table_ii_params, ModelSolver, solve_analytical, print_value_premium
from kiku_value_premium.implications import compute_asset_pricing_moments, print_asset_pricing_moments

print(estimate_long_run_leverage(dc, dd_robust, window=2))
print(estimate_long_run_leverage(dc, dd_weak, window=2))

dividends = calibrate_from_data(
    dc,
    {"growth": dd_weak, "value": dd_robust, "market": dd_market},
    frequency="annual",
    window=2,
)
params = get_table_ii_params()
params.dividends = dividends
print_value_premium(solve_analytical(params))

solver = ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))
```

`dd_weak` and `dd_robust` are annual $$\Delta\log$$ dividends on the profitability legs. For investment replace them with the aggressive and conservative series. Returns do not enter. Campbell–Shiller construction of those series follows [Section 2]({% link empirical.md %}).

{: .package }
`solve_analytical` and `compute_asset_pricing_moments` index claims by `growth`, `value`, and `market`. Assigning the high-return leg to `value` is a key convention. It is not a statement that profitability is book-to-market.

## References

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Novy-Marx, R. 2013. “The Other Side of Value: The Gross Profitability Premium.” *Journal of Financial Economics* 108 (1): 1–28.

Hou, K., C. Xue, and L. Zhang. 2015. “Digesting Anomalies: An Investment Approach.” *Review of Financial Studies* 28 (3): 650–705.

Fama, E., and K. French. 2016. “Dissecting Anomalies with a Five-Factor Model.” *Review of Financial Studies* 29 (1): 1–52.
