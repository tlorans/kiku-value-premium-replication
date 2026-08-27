---
title: 6. Further applications
nav_order: 8
---

# 6. Further applications
{: .no_toc }

1. TOC
{:toc}

Sections 2–5 price book-to-market claims. Fama and French (1993), whom I used for the value sort, already isolated a size spread. Fama and French (2015) keep size and add operating profitability and investment. All three predict average returns in the same CRSP/Compustat universe, and none is a CAPM fact. I record the published moments and state how each sort maps onto the four cash-flow loadings of Section 3.

Those loadings, $$(\mu,\phi,\varphi,\alpha)$$, are chosen from consumption and dividend growth. Average returns are not used. The objects to inspect after estimation are not only $$\phi$$. Size, profitability, and investment do not imply the same ranking of $$\mu$$ relative to $$\phi$$.

## 6.1 Construction

Fama and French (2015) keep the June timing and NYSE breakpoints of Fama and French (1993). Size is market equity at the end of June. The dividend-discount identity does not mention size. It does mention book-to-market, expected profitability, and expected investment: holding expected cash flows fixed, a lower price requires a higher expected return, and a lower price is also implied by lower expected profitability or higher expected investment. Average returns should therefore rise with profitability and fall with asset growth. Size stays in the five-factor model because average returns still vary with market cap after those three characteristics are controlled, and because the observations the five-factor model cannot price are concentrated among small stocks.

Operating profitability for the June-$$t$$ sort is revenues minus cost of goods sold, selling, general and administrative expense, and interest expense, divided by book equity, all for the fiscal year ending in $$t-1$$. Investment is the growth rate of total assets from $$t-2$$ to $$t-1$$. Independent 2×3 sorts on size and each of B/M, operating profitability, and investment produce the factors. SMB is the average of the nine small portfolios minus the average of the nine big portfolios across those three sorts. RMW is the average of the two robust-profitability portfolios minus the average of the two weak-profitability portfolios. CMA is the analogous difference for conservative versus aggressive investment. HML is the usual high-minus-low book-to-market difference.

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

Units are percent per month. Annualized, size is about three and a half percent, profitability about three, and investment about four. All three are smaller than the six-percent book-to-market gap of 1930–2003. Size is the weakest of the four non-market factors in this sample ($$t=2.31$$). It is also the one for which the CAPM does the most work: small stocks typically have higher market betas than big stocks, which value and robust-profitability stocks do not.

The size-characteristic panels (their Table 1) show the ranking without long–short construction. In every book-to-market column, average return generally falls from small to big. Among large stocks, monthly excess return rises from 0.39 percent in the weakest operating-profitability quintile to 0.57 percent in the strongest. Among small stocks, the most conservative investment quintile earned 1.01 percent against 0.35 percent for the most aggressive. The profitability and investment gaps survive among large stocks. The size gap is largest in the microcaps.

## 6.3 Valuations, HML, and the size leftover

Value in Section 2 is the cheap claim: mean $$\log(P/D)$$ of 3.25 against 3.61 for growth. Profitability does not repeat that pattern. Novy-Marx (2013) shows that the high-profitability leg earns more and sells at a *higher* valuation ratio. Investment is closer to book-to-market: conservative firms grow assets slowly and occupy the high-return, typically cheaper side of the size-investment panel. Size has no such uniform valuation signature. Small stocks are not, as a group, the cheap claim or the expensive claim. Their distinguishing cash-flow feature in the data is volatility, not a stable gap in mean $$\log(P/D)$$.

Fama and French (2015, Table 6) project each factor on the other four. HML’s intercept is absorbed once RMW and CMA are included. SMB’s intercept is not: 0.39 percent per month ($$t=3.23$$) in the 2×3 spanning regression. Book-to-market is the valuation identity restated. Size is a remaining cross-sectional fact.

The same paper isolates where that fact bites. The five-factor model’s failure is the low average return on small stocks whose returns behave like those of firms that invest a great deal despite low profitability. The 32-portfolio Size-OP-Inv sort puts the worst intercept on that corner, $$-0.47$$ percent per month ($$t=-5.89$$). A univariate SMB test is therefore incomplete. The observation that needs a cash-flow explanation is the small-weak-aggressive claim, not small stocks on average.

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

What the three additional sorts lead one to have in mind:

**Size (SMB).** A long-run-risk account of the size premium requires $$\phi_{\text{small}}>\phi_{\text{big}}$$. That is the same ranking Bansal, Dittmar, and Lundblad (2005) found for cash-flow betas on size portfolios, and it is the ranking the Euler equation needs for a positive SMB. The identity does not sign $$\mu$$. Small firms need not have higher mean dividend growth, and a higher $$\mu_{\text{small}}$$ would cheapen the model’s account of why small stocks are not uniformly expensive. What the data do lead one to expect is a larger short-run scale $$\varphi$$ on the small claim: small-firm dividends are noisier. That loading helps match $$\sigma(R)$$. It is not the mechanism of Section 3. If estimated $$\phi$$ is flat across size and only $$\varphi$$ differs, size is a volatility fact, not a long-run consumption-risk fact.

The tighter size test is the corner Fama and French cannot price. Map the small-weak-aggressive portfolio and the small-robust-conservative portfolio as two claims, leaving the market as the third. The five-factor leftover is a *low* average return on the first of those two. In this model a low return is a small $$\phi$$, a large $$\mu$$, or both. If that corner’s estimated $$\phi$$ is *larger* than the rest of the small universe, the long-run risks model will raise its premium and will miss the fact that needs explaining.

**Operating profitability (RMW).** Robust firms are defined by high current earnings. The cash-flow counterpart is a higher mean dividend growth rate: one expects $$\mu_{\text{robust}}>\mu_{\text{weak}}$$. That gap is what can keep the robust claim expensive. A long-run-risk account of the premium still requires $$\phi_{\text{robust}}>\phi_{\text{weak}}$$. The joint implication is the demanding one. $$\phi$$ must be larger on the robust leg or the Euler equation will not produce a positive RMW. $$\mu$$ must be larger by enough to offset that $$\phi$$ in the price–dividend formula, or the model will make the high-return claim the cheap claim. If estimated $$\mu$$ is flat across the sort, profitability cannot be priced by recycling Table II. If estimated $$\phi$$ is flat or reversed, the premium is not compensation for long-run consumption risk.

**Investment (CMA).** Conservative firms grow assets slowly. The sort looks like book-to-market: high return, typically lower valuation. The working hypothesis is the value hypothesis. One expects $$\phi_{\text{conservative}}>\phi_{\text{aggressive}}$$. A higher $$\mu$$ on the conservative leg is not required and would work against the cheapness of that claim. Aggressive firms may well show a higher $$\mu$$ — they are the high-investment, high-growth side — together with a smaller $$\phi$$. That pair is the growth pair of Sections 2–5.

**Short-run loadings.** $$\varphi$$ and $$\alpha$$ are not the leading suspects for the premia. They matter for return volatility and for covariance with contemporaneous consumption news. A finding that $$\alpha$$ differs across legs while $$\phi$$ does not would be a short-run consumption-CAPM story, not the mechanism of this paper. I still estimate them. I do not interpret a gap in $$\varphi$$ as evidence that the model has priced SMB, RMW, or CMA. Size is the sort where that warning bites first.

Book-to-market in Table II is the case in which $$\phi$$ and $$\mu$$ move together and $$\phi$$ wins the valuation ranking. Profitability is the case in which they must move together and $$\mu$$ must win the valuation ranking. Investment is the case that should look like book-to-market. Size is the case that should show a $$\phi$$ ranking if the premium is long-run risk, a $$\varphi$$ ranking if it is only noise, and a *low* $$\phi$$ on the small-weak-aggressive corner if the model is to speak to the five-factor leftover. Those are the patterns to keep in view when the estimated `DividendParams` are on the table.

## 6.5 The restriction

I apply equation (19) to each leg,

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2} \Delta c_{t-k} + \varepsilon_t. \tag{19}
$$

Kiku (2006) does not report these slopes for size, profitability, or investment. They are estimated, not copied from Table II. Preferences and aggregate consumption remain those of Table II. The three claims the solver prices are a naming convention.

| Sort | Key `growth` | Key `value` |
|:---|:---|:---|
| Book-to-market | low B/M | high B/M |
| Size | big | small |
| Operating profitability | weak | robust |
| Investment | aggressive | conservative |
| Five-factor leftover | small-robust-conservative | small-weak-aggressive |

The leftover row is signed by the fact that needs explaining, not by average return. The small-weak-aggressive claim is the *low*-return corner. Assigning it to `value` will look like a high premium only if its estimated $$\phi$$ is large. That is the wrong cash-flow ranking for that observation.

The model prices a high-return sort if three implications hold together. First, the high-return leg’s estimated $$\tilde\phi$$ — and therefore its monthly $$\phi$$ — exceeds the low-return leg’s. Second, the estimated $$\mu$$ ranking is the ranking the valuation pattern requires: higher on robust than on weak if profitability is to stay expensive; not signed a priori for size; not necessarily higher on conservative than on aggressive. Third, the Euler equation, given only those four loadings, produces a premium of the same sign and of approximately the published magnitude (about three and a half percent for SMB, three for RMW, four for CMA over 1963–2013) and a $$\log(P/D)$$ ranking that does not contradict the data.

A reversal on $$\phi$$ means the factor is not a long-run cash-flow factor. A reversal on $$\mu$$, with $$\phi$$ intact, means the model can match the premium and will miss the price. A reversal on the premium, with both cash-flow rankings intact, means the Table II investor cannot be recycled. For the leftover corner, a *large* estimated $$\phi$$ is already a reversal: the model would then predict a high return where the five-factor residual is negative.

```python
import lrrcs as lrr

print(lrr.estimate_long_run_leverage(dc, dd_small, window=2))
print(lrr.estimate_long_run_leverage(dc, dd_big, window=2))

dividends = lrr.calibrate_from_data(
    dc, long=dd_small, short=dd_big, market=dd_market,
    frequency="annual", window=2,
)
for name, d in dividends.items():
    print(name, d.mu, d.phi, d.phi_sigma, d.alpha)

params = lrr.get_table_ii_params()
params.dividends = dividends
lrr.print_long_short_premium(lrr.solve_analytical(params))

solver = lrr.ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
lrr.print_asset_pricing_moments(lrr.compute_asset_pricing_moments(solver))
```

The four printed numbers on each leg are the whole mapping. Compare `value.mu` to `growth.mu` and `value.phi` to `growth.phi` before reading the premium. Replace the size series with weak/robust for RMW, aggressive/conservative for CMA, or the two small corner portfolios for the five-factor leftover. Returns do not enter. Campbell–Shiller construction follows [Section 2]({% link empirical.md %}).

{: .package }
`solve_analytical` and `compute_asset_pricing_moments` index claims by `growth`, `value`, and `market`. Assigning a leg to `value` does not impose Table II’s $$(\mu,\phi)$$. Those come from the dividends just estimated.

## References

Fama, E., and K. French. 1993. “Common Risk Factors in the Returns on Stocks and Bonds.” *Journal of Financial Economics* 33 (1): 3–56.

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Novy-Marx, R. 2013. “The Other Side of Value: The Gross Profitability Premium.” *Journal of Financial Economics* 108 (1): 1–28.

Hou, K., C. Xue, and L. Zhang. 2015. “Digesting Anomalies: An Investment Approach.” *Review of Financial Studies* 28 (3): 650–705.

Fama, E., and K. French. 2016. “Dissecting Anomalies with a Five-Factor Model.” *Review of Financial Studies* 29 (1): 1–52.

Bansal, R., R. Dittmar, and C. Lundblad. 2005. “Consumption, Dividends, and the Cross Section of Equity Returns.” *Journal of Finance* 60 (4): 1639–1672.
