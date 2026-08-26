---
title: Climate
nav_order: 5
---

# Climate
{: .no_toc }

1. TOC
{:toc}

Put climate into consumption and the market premium moves. That is still one claim.

Melin and Zhang (2026) do that. Chronic physical damage and transition cost raise the *market* equity premium by about twenty percent at $$3^{\circ}$$C. The risk-free rate falls. Mean $$\log(P/D)$$ on the market falls. Useful. Not a ranking of firms.

The question this page asks is the cross-sectional one. Brown versus green. Exposed versus sheltered. Same investor. Loadings from dividends, not from returns.

## Construction

Keep Epstein–Zin and $$x_t$$. Add a temperature anomaly $$T_t$$, a policy target $$P_t$$, and a persistent damage and transition signal $$Y_t$$.

$$
\Delta c_{t+1}=\mu+x_t+\Omega Y_t+\Gamma(P_{t+1}-P_t)+\sigma_{\eta}\eta_{t+1}.
$$

Temperature also loads on activity. The IMRS is still equation (3). Closed forms for the risk-free rate and the equity premium are the same linearization as the time-series page.

Two sorts. Transition: carbon emissions or intensity. Physical: location — heat, flood, cyclone, wildfire. Dividends are Campbell–Shiller. Consumption is NIPA nondurables and services. Align $$Y_t$$ and $$P_t$$ to the dividend year.

Do not take a stand on the sign of realized brown–green returns. Those spreads change sign across samples. The characteristic defines the legs. The Euler equation prices the legs.

## The market, with climate

|  | Counterfactual | Climate calibration |
|:---|---:|---:|
| Share of ERP from short-run consumption | 31.1% | 27.9% |
| Share of ERP from long-run consumption | 68.9% | 56.3% |
| Share of ERP from temperature level | 0 | 11.6% |
| Share of ERP from temperature change | 0 | 0.6% |
| Share of ERP from the policy target | 0 | 3.6% |

At $$3^{\circ}$$C the equity premium is about twenty percent higher. The risk-free rate is about fifty basis points lower near peak warming, about twenty-five at 2100. Mean market $$\log(P/D)$$ is about four percent lower.

A level. Not a cross section.

## Prices, not just returns

Value is cheap. Green firms, like high-profitability firms, often are not. A transition premium with rich green prices is a joint restriction: $$\Gamma$$ larger on brown, $$\mu$$ larger on green by enough to keep green expensive.

Physical exposure looks more like book-to-market. If $$\Omega$$ is the mechanism, the exposed claim should be the high-return, cheaper side.

## Mapping

$$
\Delta d_{t+1}=\mu+\phi x_t+\Omega^i Y_t+\Gamma^i(P_{t+1}-P_t)+\varphi\sigma_t u_{t+1}.
$$

Preferences, $$x_t$$, and the climate laws stay at the Melin–Zhang aggregate. Only the claim-specific numbers change. Average returns do not enter.

| Loading | From | Premium | $$\log(P/D)$$ |
|:---|:---|:---|:---|
| $$\mu$$ | mean $$\Delta d$$ | almost nothing | rises |
| $$\phi$$ | slope (19) on lagged $$\Delta c$$ | rises | falls |
| $$\Omega^i$$ | slope of $$\Delta d$$ on $$Y$$ | rises | falls |
| $$\Gamma^i$$ | slope of $$\Delta d$$ on $$\Delta P$$ | rises | falls |

If only $$\phi$$ differs, you have relabeled value. That is the last page, not this one.

**Transition.** $$\Gamma^{\text{brown}}>\Gamma^{\text{green}}$$. If $$\mu$$ is larger on green and $$\Gamma$$ is flat, you can match the green price and you will not get the premium.

**Physical.** $$\Omega^{\text{exposed}}>\Omega^{\text{sheltered}}$$. A lower $$\mu$$ on the exposed leg cheapens it and raises the predicted premium.

## The restriction

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2}\Delta c_{t-k} + \tilde\Omega Y_{t-1} + \tilde\Gamma \Delta P_t + \varepsilon_t.
$$

| Sort | `short=` | `long=` |
|:---|:---|:---|
| Transition | green | brown |
| Physical | sheltered | exposed |

Four things have to hold at once. The high-return leg has the larger climate loading. The $$\mu$$ ranking matches the valuation pattern. Setting $$\Omega^i=\Gamma^i=0$$ does not already absorb the premium through $$\phi$$. The Euler equation then produces a premium of the right sign and a $$\log(P/D)$$ ranking that does not fight the data.

```python
from kiku_value_premium.calibration import calibrate_from_data, estimate_long_run_leverage
from kiku_value_premium.model import get_table_ii_params, solve_analytical, print_value_premium

print(estimate_long_run_leverage(dc, dd_brown, window=2))
print(estimate_long_run_leverage(dc, dd_green, window=2))

dividends = calibrate_from_data(
    dc, frequency="annual", window=2,
    short=dd_green, long=dd_brown, market=dd_market,
)
for name, d in dividends.items():
    print(name, d.mu, d.phi, d.phi_sigma, d.alpha)

params = get_table_ii_params()
params.dividends = dividends
print_value_premium(solve_analytical(params))
```

{: .package }
This snippet does not see $$Y_t$$ or $$P_t$$. The premium it prints is the part already priced by $$\phi$$ and $$\mu$$. The rest is what the climate states would have to do.

## References

Melin, L., and F. Zhang. 2026. “Quantifying Climate Risk Premia.” EDHEC Climate Institute.

Bansal, R., D. Kiku, and M. Ochoa. 2016. “Price of Long-Run Temperature Shifts in Capital Markets.” NBER Working Paper 22529.

Bansal, R., D. Kiku, and M. Ochoa. 2019. “Climate Change Risk.” Working paper.

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Novy-Marx, R. 2013. “The Other Side of Value: The Gross Profitability Premium.” *Journal of Financial Economics* 108 (1): 1–28.
