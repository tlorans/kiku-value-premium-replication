---
title: Climate
nav_order: 5
---

# Climate
{: .no_toc }

1. TOC
{:toc}

**Question, time series.** If climate damage and climate policy enter *aggregate consumption*, what happens to the market — the single claim on all stocks?

**Question, cross section.** Do firms whose dividends move with those climate states earn more, and do they sell cheaper, in the same household?

The first question has a published answer. The second is the test this page states.

Melin and Zhang (2026) put climate into the consumption process of the time-series page. Two kinds of cost. *Physical* cost: heat, flood, storm, wildfire damage that lowers output. *Transition* cost: policy that tightens on carbon and makes dirty production more expensive. At three degrees of warming the *market* equity premium — stocks minus the safe bond — is about twenty percent higher than in a run with no climate. The safe rate falls. The market’s log price–dividend ratio falls. That is one claim through time. It does not rank brown against green, or coastal against inland.

## States that get added

Keep the household of the time-series page and the persistent growth factor $$x_t$$. Add three climate objects.

- $$T_t$$ — temperature anomaly, degrees above a pre-industrial baseline.
- $$P_t$$ — a policy target (how tight carbon policy is).
- $$Y_t$$ — a persistent signal of damage and transition cost already in the pipeline.

Consumption growth becomes

$$
\Delta c_{t+1}=\mu+x_t+\Omega Y_t+\Gamma(P_{t+1}-P_t)+\sigma_{\eta}\eta_{t+1}.
$$

- $$\Omega$$ — how much aggregate consumption falls when the damage signal $$Y$$ is high.
- $$\Gamma$$ — how much aggregate consumption falls when policy tightens ($$P$$ rises).
- $$\eta$$ — the usual short-run consumption shock.

Temperature also moves with economic activity. The discount factor is still the IMRS of the time-series page — the random variable $$M_{t+1}$$ that turns a future payoff into a present value. Closed forms for the safe rate and the equity premium are the same linearization, with two extra states.

Two sorts of *firms* match the two extra terms.

- *Transition sort.* Rank firms on carbon emissions, or emissions over sales. Brown is high. Green is low.
- *Physical sort.* Rank firms on location: heat, flood, cyclone, wildfire exposure. Exposed is high. Sheltered is low.

Dividends are still inferred from returns with and without dividends. Consumption is still NIPA nondurables and services. Line $$Y_t$$ and $$P_t$$ up with the dividend year.

Do not take a stand on the sign of realized brown-minus-green returns. Those gaps change sign across samples. The characteristic defines the legs. The Euler equation — expected $$M$$ times return equals one — is asked to price the legs.

## The market, with climate in consumption

**Test.** Compare the market under the published climate path with a counterfactual that shuts climate off.

| Share of the equity premium from | No climate | Climate path |
|:---|---:|---:|
| This year’s consumption surprise | 31.1% | 27.9% |
| The persistent growth factor $$x_t$$ | 68.9% | 56.3% |
| The level of temperature | 0 | 11.6% |
| The change in temperature | 0 | 0.6% |
| The policy target | 0 | 3.6% |

**Result.** At three degrees the equity premium is about twenty percent higher. The safe rate is about fifty basis points lower near peak warming, about twenty-five at 2100. Mean market $$\log(P/D)$$ is about four percent lower.

A *level* for one claim. Not a ranking of firms.

## Prices, not just returns

Value was cheap. Green firms, like high-profitability firms, often are not. A transition premium with rich green prices is then a joint restriction: policy loading $$\Gamma$$ larger on brown, mean dividend growth $$\mu$$ larger on green by enough to keep green expensive.

Physical exposure looks more like book-to-market. If the damage loading $$\Omega$$ is the mechanism, the exposed claim should be the high-return, cheaper side.

## Four old numbers, two new ones

Each firm’s dividends can load on $$x_t$$ *and* on the climate states.

$$
\Delta d_{t+1}=\mu+\phi x_t+\Omega^i Y_t+\Gamma^i(P_{t+1}-P_t)+\varphi\sigma_t u_{t+1}.
$$

The superscript $$i$$ means the loading is firm-specific. The household, $$x_t$$, and the climate laws stay at the Melin–Zhang aggregate. Only the claim-specific numbers change. Average returns do not enter.

| Loading | Measured from | Average return | $$\log(P/D)$$ |
|:---|:---|:---|:---|
| $$\mu$$ | mean dividend growth | almost nothing | rises |
| $$\phi$$ | slope of dividends on lagged consumption | rises | falls |
| $$\Omega^i$$ | slope of dividends on the damage signal $$Y$$ | rises | falls |
| $$\Gamma^i$$ | slope of dividends on the policy change $$\Delta P$$ | rises | falls |

If only $$\phi$$ differs across brown and green, you have relabeled value. That is the cross-section page, not this one.

**Transition test.** Need $$\Gamma^{\text{brown}}>\Gamma^{\text{green}}$$. If $$\mu$$ is larger on green and $$\Gamma$$ is flat, you can match the green price and you will not get the premium.

**Physical test.** Need $$\Omega^{\text{exposed}}>\Omega^{\text{sheltered}}$$. A lower $$\mu$$ on the exposed leg cheapens it and raises the predicted premium.

## The restriction, in one regression

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2}\Delta c_{t-k} + \tilde\Omega Y_{t-1} + \tilde\Gamma \Delta P_t + \varepsilon_t.
$$

The tildes are annual slopes, as in equation (19) on the cross-section page. They are not passed to the solver as numbers. Their ranking is.

| Sort | `short=` | `long=` |
|:---|:---|:---|
| Transition | green | brown |
| Physical | sheltered | exposed |

**What would count as success.** Four things at once. The high-return leg has the larger climate loading. The $$\mu$$ ranking matches the price–dividend pattern. Setting $$\Omega^i=\Gamma^i=0$$ does not already absorb the premium through $$\phi$$. The Euler equation then produces a premium of the right sign and a $$\log(P/D)$$ ranking that does not fight the data.

```python
import lrrcs as lrr

print(lrr.estimate_long_run_leverage(dc, dd_brown, window=2))
print(lrr.estimate_long_run_leverage(dc, dd_green, window=2))

dividends = lrr.calibrate_from_data(
    dc, frequency="annual", window=2,
    short=dd_green, long=dd_brown, market=dd_market,
)
for name, d in dividends.items():
    print(name, d.mu, d.phi, d.phi_sigma, d.alpha)

params = lrr.get_table_ii_params()
params.dividends = dividends
lrr.print_long_short_premium(lrr.solve_analytical(params))
```

{: .package }
This snippet does not see $$Y_t$$ or $$P_t$$. The spread it prints is the part already priced by $$\phi$$ and $$\mu$$. The rest is what the climate states would have to do.

## References

Melin, L., and F. Zhang. 2026. “Quantifying Climate Risk Premia.” EDHEC Climate Institute.

Bansal, R., D. Kiku, and M. Ochoa. 2016. “Price of Long-Run Temperature Shifts in Capital Markets.” NBER Working Paper 22529.

Bansal, R., D. Kiku, and M. Ochoa. 2019. “Climate Change Risk.” Working paper.

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Novy-Marx, R. 2013. “The Other Side of Value: The Gross Profitability Premium.” *Journal of Financial Economics* 108 (1): 1–28.
