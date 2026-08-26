---
title: 6. Further applications
nav_order: 8
---

# 6. Further applications
{: .no_toc }

1. TOC
{:toc}

Sections 2–5 price book-to-market claims. After 2006 two further spreads entered the set of facts a consumption-based model must confront. Fama and French (2015) show that operating profitability and investment predict average returns in the same CRSP/Compustat universe I used for value, and that neither spread is a CAPM fact. I record those moments here and state how each sort maps onto the four cash-flow loadings of Section 3.

Those loadings, $$(\mu,\phi,\varphi,\alpha)$$, are chosen from consumption and dividend growth. Average returns are not used. The objects to inspect after estimation are not only $$\phi$$. For profitability the mean growth rate $$\mu$$ is the parameter that can support a high price–dividend ratio. Without it, renaming the value claim “robust” and rerunning Table II cannot reproduce Novy-Marx (2013).

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

Value in Section 2 is the cheap claim: mean $$\log(P/D)$$ of 3.25 against 3.61 for growth. Profitability does not repeat that pattern. Novy-Marx (2013) shows that the high-profitability leg earns more and sells at a *higher* valuation ratio. Investment is closer to book-to-market: conservative firms grow assets slowly and occupy the high-return, typically cheaper side of the size-investment panel.

Fama and French (2015, Table 6) project each factor on the other four. The intercept of HML is absorbed once RMW and CMA are included. In that sample book-to-market is the valuation identity restated: high B/M firms are disproportionately the firms with weaker profitability or faster asset growth, after size and the market are controlled. That redundancy does not retract Sections 2–5. It does imply that profitability and investment are the two additional cash-flow sorts the model must face, not a third independent test alongside HML.

## 6.4 Mapping a sort onto $$(\mu,\phi,\varphi,\alpha)$$

Equation (6) gives each claim four numbers. Preferences and the consumption process stay at Table II. Only these four change.

$$
\Delta d_{t+1}=\mu+\phi x_t+\varphi\sigma_t u_{t+1},\qquad \alpha=\mathrm{Corr}(\eta,u).
$$

`calibrate_from_data` estimates all four from dividends and consumption. It does not see returns. What each loading does in the Euler equation is fixed by Section 3.

| Loading | Estimated from | Effect on E$$[R]$$ | Effect on $$\log(P/D)$$ |
|:---|:---|:---|:---|
| $$\mu$$ | mean $$\Delta d$$ | negligible | rises with $$\mu$$ |
| $$\phi$$ | projection (19) of $$\Delta d$$ on lagged $$\Delta c$$ | rises with $$\phi$$ | falls with $$\phi$$ |
| $$\varphi$$ | residual dividend volatility | small; mostly $$\sigma(R)$$ | weak |
| $$\alpha$$ | residual correlation with the consumption innovation | short-run premium, priced at $$\gamma$$ | weak |

The value exercise in Table II already uses both $$\mu$$ and $$\phi$$. Value’s mean monthly dividend growth is 0.0019 against growth’s 0.0009; value’s long-run leverage is 6.2 against 2.6. The premium is a $$\phi$$ fact. Value nonetheless sells cheaper, which means that in that sort $$\phi$$ dominates $$\mu$$ in the price–dividend ratio. One cannot read the premium off $$\phi$$ and ignore the estimated $$\mu$$ when the valuation ranking is part of the test.

That is the reason profitability is not a relabeling of Table II. The robust leg must be allowed to have a larger $$\mu$$. If it does not, a larger $$\phi$$ will cheapen it, and the model price ranking will contradict Novy-Marx. The objects to print after `calibrate_from_data` are therefore both `.mu` and `.phi` on each leg, not `.phi` alone.

What the two new sorts lead one to have in mind:

**Operating profitability (RMW).** Robust firms are defined by high current earnings. The cash-flow counterpart is a higher mean dividend growth rate: one expects $$\mu_{\text{robust}}>\mu_{\text{weak}}$$. That gap is what can keep the robust claim expensive. A long-run-risk account of the *premium* still requires $$\phi_{\text{robust}}>\phi_{\text{weak}}$$. The joint implication is the demanding one. $$\phi$$ must be larger on the robust leg or the Euler equation will not produce a positive RMW. $$\mu$$ must be larger by enough to offset that $$\phi$$ in the price–dividend formula, or the model will make the high-return claim the cheap claim. If estimated $$\mu$$ is flat across the sort, profitability cannot be priced by recycling Table II. If estimated $$\phi$$ is flat or reversed, the premium is not compensation for long-run consumption risk.

**Investment (CMA).** Conservative firms grow assets slowly. The sort looks like book-to-market: high return, typically lower valuation. The working hypothesis is the value hypothesis. One expects $$\phi_{\text{conservative}}>\phi_{\text{aggressive}}$$. A higher $$\mu$$ on the conservative leg is not required and would work against the cheapness of that claim. Aggressive firms may well show a higher $$\mu$$ — they are the high-investment, high-growth side — together with a smaller $$\phi$$. That pair is the growth pair of Sections 2–5.

**Short-run loadings.** $$\varphi$$ and $$\alpha$$ are not the leading suspects for either premium. They matter for return volatility and for the part of the premium that is covariance with contemporaneous consumption news. A finding that $$\alpha$$ differs across legs while $$\phi$$ does not would be a short-run consumption-CAPM story, not the mechanism of this paper. I still estimate them. I do not interpret a gap in $$\varphi$$ as evidence that the model has priced RMW or CMA.

Book-to-market in Table II is the case in which $$\phi$$ and $$\mu$$ move together and $$\phi$$ wins the valuation ranking. Profitability is the case in which they must move together and $$\mu$$ must win the valuation ranking. Investment is the case that should look like book-to-market. Those are the three patterns to keep in view when the estimated `DividendParams` are on the table.

## 6.5 The restriction

I apply equation (19) to each leg,

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2} \Delta c_{t-k} + \varepsilon_t. \tag{19}
$$

Kiku (2006) does not report these slopes for profitability or investment. They are estimated, not copied from Table II. Preferences and aggregate consumption remain those of Table II. The three claims the solver prices are a naming convention.

| Sort | Key `growth` | Key `value` |
|:---|:---|:---|
| Book-to-market | low B/M | high B/M |
| Operating profitability | weak | robust |
| Investment | aggressive | conservative |

The model prices the sort if three implications hold together. First, the high-return leg’s estimated $$\tilde\phi$$ — and therefore its monthly $$\phi$$ — exceeds the low-return leg’s. Second, the estimated $$\mu$$ ranking is the ranking the valuation identity requires: higher on robust than on weak if profitability is to stay expensive; not necessarily higher on conservative than on aggressive. Third, the Euler equation, given only those four loadings, produces a premium of the same sign and of approximately the published magnitude (about three percent for RMW and about four percent for CMA over 1963–2013) and a $$\log(P/D)$$ ranking that does not contradict the data.

A reversal on $$\phi$$ means the factor is not a long-run cash-flow factor. A reversal on $$\mu$$, with $$\phi$$ intact, means the model can match the premium and will miss the price. A reversal on the premium, with both cash-flow rankings intact, means the Table II investor cannot be recycled.

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
for name in ("growth", "value", "market"):
    d = dividends[name]
    print(name, d.mu, d.phi, d.phi_sigma, d.alpha)

params = get_table_ii_params()
params.dividends = dividends
print_value_premium(solve_analytical(params))

solver = ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))
```

The four printed numbers on each leg are the whole mapping. Compare `value.mu` to `growth.mu` before reading the premium. For investment replace `dd_weak` and `dd_robust` with the aggressive and conservative series. Returns do not enter. Campbell–Shiller construction follows [Section 2]({% link empirical.md %}).

{: .package }
`solve_analytical` and `compute_asset_pricing_moments` index claims by `growth`, `value`, and `market`. Assigning the high-return leg to `value` does not impose Table II’s $$(\mu,\phi)$$. Those come from the dividends just estimated.

## References

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Novy-Marx, R. 2013. “The Other Side of Value: The Gross Profitability Premium.” *Journal of Financial Economics* 108 (1): 1–28.

Hou, K., C. Xue, and L. Zhang. 2015. “Digesting Anomalies: An Investment Approach.” *Review of Financial Studies* 28 (3): 650–705.

Fama, E., and K. French. 2016. “Dissecting Anomalies with a Five-Factor Model.” *Review of Financial Studies* 29 (1): 1–52.
