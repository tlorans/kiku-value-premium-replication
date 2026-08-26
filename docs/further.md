---
title: 6. Further applications
nav_order: 8
---

# 6. Further applications
{: .no_toc }

1. TOC
{:toc}

The 2006 paper stops at book-to-market. Fama and French (2015) document two further spreads that the CAPM does not price: robust-minus-weak operating profitability (RMW) and conservative-minus-aggressive investment (CMA). The question this section poses is the same question Section 2 posed for value. Do the cash flows of the high-return leg load more on the persistent component of consumption growth than those of the low-return leg? If they do, the long-run risks model is a candidate. If they do not, the premia are a different puzzle.

The six-percent value premium was not a calibration target. Neither is RMW or CMA. Average returns stay out of `calibrate_from_data`.

## 6.1 What changed after 2006

Fama and French (1993) already sat in Section 2: June sorts, NYSE breakpoints, book-to-market. Their 2015 paper keeps that construction and adds two characteristics from the dividend-discount identity. Expected return is high when, holding expected cash flows fixed, price is low. Price is also low when expected profitability is low or when expected investment (asset growth) is high. The identity therefore predicts that average returns should rise with operating profitability and fall with investment, once book-to-market is not asked to do all the work.

Novy-Marx (2013) had already shown that gross profits-to-assets ranks average returns about as strongly as book-to-market. Fama and French measure operating profitability as annual revenues minus cost of goods sold, SG&A, and interest, divided by book equity. Investment is the annual growth rate of total assets. Both sorts are independent of size. RMW is the average of the two robust size portfolios minus the average of the two weak size portfolios. CMA is the same construction on conservative versus aggressive investment.

Hou, Xue, and Zhang (2015) reach a close pair of factors from the production side (ROE and investment). I stay with Fama and French’s published 2×3 factors because the construction is the direct descendant of the sorts in Section 2.

## 6.2 The two premia in the published sample

Table 2 of Fama and French (2015), July 1963–December 2013, 606 months, 2×3 factors:

|  | Mean % / month | σ % | $$t$$ |
|:---|---:|---:|---:|
| Market minus T-bill | 0.50 | 4.49 | 2.74 |
| SMB | 0.29 | 3.07 | 2.31 |
| HML | 0.37 | 2.88 | 3.20 |
| RMW | 0.25 | 2.14 | 2.92 |
| CMA | 0.33 | 2.01 | 4.07 |

Annualized, robustness is worth about three percent a year and conservatism about four. Those are smaller than the six-percent value gap of 1930–2003, but they are not noise, and they survive in a sample that begins after the Depression.

The size-characteristic sorts in their Table 1 make the same point without forming long–short factors. Among large stocks, monthly excess return rises from 0.39 percent in the weakest operating-profitability quintile to 0.57 percent in the strongest. Among small stocks the investment sort is sharper: 1.01 percent on the most conservative quintile against 0.35 percent on the most aggressive. The high-return legs are not high-market-beta legs in a way that would let the CAPM absorb the spreads. That is the same empirical embarrassment Section 2 recorded for value.

One difference matters for prices. Value in Section 2 is the cheap claim: mean $$\log(P/D)$$ 3.25 against 3.61 for growth. Novy-Marx’s profitable firms are the opposite. They earn more and sell at *higher* valuation ratios. A mechanism that only raises $$\phi$$ lowers the model price–dividend ratio. Profitability therefore cannot be a relabeling of value inside Table II. Either expected cash-flow growth $$\mu$$ is high enough on the robust leg to offset a larger $$\phi$$, or the joint return–valuation test fails.

Investment is closer to value. Conservative firms grow assets slowly and, in the size-investment panel, look like the high-return cheap side of a sort.

## 6.3 HML is not an independent third fact

Fama and French (2015, Table 6) regress each factor on the other four. HML’s intercept is absorbed once RMW and CMA are present. In their sample the value premium is the valuation identity restated: high book-to-market firms are disproportionately the firms that are less profitable or that invest more, once the market and size are controlled.

That redundancy is not a reason to drop the value exercise in Sections 2–5. The 1930–2003 book-to-market quintiles remain the objects priced here. It is a reason not to treat RMW, CMA, and HML as three separate long-run-risk tests. Two cash-flow sorts plus the original book-to-market sort are enough. If the model prices profitability and investment through $$\phi$$ and $$\mu$$, the residual HML claim is not an extra degree of freedom.

## 6.4 The test, unchanged

Sections 3 and 4 do not mention book-to-market. They mention a consumption process and a vector of dividend claims. Any sort that produces a dividend series can be priced. The protocol is the protocol of the paper.

1. Form the characteristic portfolios on the same CRSP/Compustat universe as Section 2. Extract Campbell–Shiller dividends. Time-aggregate to calendar years. Do not touch average returns.
2. Estimate equation (19) on each leg,

   $$
   \Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2} \Delta c_{t-k} + \varepsilon_t.
   $$

   The ranking of $$\tilde\phi$$ is the cash-flow fact. Printed goldens do not exist for these sorts in Kiku (2006); the ranking is the object to be measured.
3. Map the legs onto the solver keys. The investor and the consumption process stay at Table II.

   | Sort | Low-return key | High-return key | Market |
   |:---|:---|:---|:---|
   | Book-to-market | `growth` | `value` | `market` |
   | Operating profitability | `growth` ← weak | `value` ← robust | `market` |
   | Investment | `growth` ← aggressive | `value` ← conservative | `market` |

4. Read premia and $$\log(P/D)$$ off the Euler equation. Compare to the published means. Do not retune $$\phi$$ if the premium is wrong.

A successful pricing of RMW requires two inequalities at once: the robust claim’s expected return above the weak claim’s, and a price–dividend ranking that does not contradict Novy-Marx. A successful pricing of CMA is closer to the value case: conservative above aggressive in expected return, and cheaper if the cash-flow risk is long-run.

```python
from kiku_value_premium.calibration import calibrate_from_data, estimate_long_run_leverage
from kiku_value_premium.model import get_table_ii_params, ModelSolver, solve_analytical, print_value_premium
from kiku_value_premium.implications import compute_asset_pricing_moments, print_asset_pricing_moments

# dc, dd_weak, dd_robust, dd_market are annual Δlog dividends
# and consumption growth. Returns never enter.
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

Replace `dd_weak` / `dd_robust` with `dd_aggressive` / `dd_conservative` for CMA. `[data]` and WRDS are required only to build those dividend series. The solver does not import `wrds`.

{: .package }
`solve_analytical` and `compute_asset_pricing_moments` look up the keys `growth`, `value`, and `market`. Mapping the high-return leg onto `value` is a naming convention, not a claim that profitability is book-to-market.

## 6.5 What would count as an answer

The model prices the new factor if three things hold together, as in Section 5.

- The high-return leg’s estimated $$\tilde\phi$$ exceeds the low-return leg’s. Without that gap there is no long-run-risk story.
- The Euler equation, fed only those cash-flow parameters, produces a premium of the same sign and of roughly the published magnitude (about three percent for RMW, about four for CMA, 1963–2013).
- The model price–dividend ranking is not the opposite of the data. For CMA this is the value pattern. For RMW it is the harder joint test: higher return and higher valuation, which has to come from $$\mu$$ as well as from $$\phi$$.

Failure on the first item means the factor is not a long-run cash-flow factor. Failure on the second, with the first intact, means Table II preferences or persistence cannot be recycled. Failure on the third means the mechanism that worked for value — one loading that raises the premium and cheapens the claim — is too tight for profitability.

None of those three checks is in the 2006 tables. They are the reason to run the package on the post-2015 sorts rather than to add RMW and CMA as extra targets in Section 4.

Worked templates: [`examples/calibrate_any_portfolio.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_any_portfolio.py), [`examples/calibrate_from_real_data.py`](https://github.com/tlorans/kiku-value-premium-replication/blob/main/examples/calibrate_from_real_data.py). Construction notes for a new CRSP extract remain those of [Section 2]({% link empirical.md %}).

## References

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Novy-Marx, R. 2013. “The Other Side of Value: The Gross Profitability Premium.” *Journal of Financial Economics* 108 (1): 1–28.

Hou, K., C. Xue, and L. Zhang. 2015. “Digesting Anomalies: An Investment Approach.” *Review of Financial Studies* 28 (3): 650–705.

Fama, E., and K. French. 2016. “Dissecting Anomalies with a Five-Factor Model.” *Review of Financial Studies* 29 (1): 1–52.
