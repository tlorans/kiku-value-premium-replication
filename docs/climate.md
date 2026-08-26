---
title: Climate
nav_order: 5
---

# 7. Climate risk premia
{: .no_toc }

1. TOC
{:toc}

[Time series]({% link time-series.md %}) prices the market. [Cross section]({% link cross-section.md %}) prices value versus growth. [Other risk premia]({% link further.md %}) states the test for size, profitability, and investment. Melin and Zhang (2026) put climate into the long-run risks consumption process and price a single market equity. Chronic physical damage and transition cost raise that claim’s premium by about twenty percent at three degrees of warming. I record their aggregate moments and state the cross-sectional restriction for transition and physical sorts.

Those parameters are still chosen from consumption and dividends. Average brown–green returns are not used. Two further loadings appear, $$\Omega^i$$ on the persistent damage signal and $$\Gamma^i$$ on policy tightening. The objects to inspect after estimation are $$(\mu,\phi,\Omega^i,\Gamma^i)$$. A climate sort that differs only in $$\phi$$ is the value mechanism under another characteristic.

## 7.1 Construction

Melin and Zhang keep Epstein–Zin preferences and the persistent factor $$x_t$$. They add a temperature anomaly $$T_t$$, a policy target $$P_t$$, and a persistent damage and transition signal $$Y_t$$. Consumption growth is

$$
\Delta c_{t+1}=\mu+x_t+\Omega Y_t+\Gamma(P_{t+1}-P_t)+\sigma_{\eta}\eta_{t+1}.
$$

Temperature loads on the policy target and on activity, $$\Theta x_t$$. Market dividends are levered consumption plus the same climate terms. The IMRS is still equation (3). Closed forms for the risk-free rate and the equity premium follow from the same linearization as the time-series page.

Two sorts correspond to the two climate terms. Transition ranks firms on carbon emissions or emission intensity. Physical ranks firms on location-based exposure to heat, flood, cyclone, or wildfire. Dividends are the Campbell–Shiller series of the cross-section page. Consumption remains NIPA nondurables and services. $$Y_t$$ and $$P_t$$ are aligned to the dividend year from the temperature and policy paths used to calibrate the aggregate module.

I do not take a stand on the sign of realized brown–green returns. Those spreads change sign across samples. The characteristic defines the legs. The Euler equation is asked to price the legs.

## 7.2 Aggregate moments

Melin and Zhang report the market claim under their NGFS-aligned path and under a no-climate counterfactual. That is a time-series statement.

|  | Counterfactual | Climate calibration |
|:---|---:|---:|
| Share of ERP from short-run consumption | 31.1% | 27.9% |
| Share of ERP from long-run consumption | 68.9% | 56.3% |
| Share of ERP from temperature level | 0 | 11.6% |
| Share of ERP from temperature change | 0 | 0.6% |
| Share of ERP from the policy target | 0 | 3.6% |

At $$3^{\circ}$$C the equity premium is about twenty percent higher than in the counterfactual. The risk-free rate falls by about fifty basis points near peak warming and remains about twenty-five basis points lower at 2100. Mean $$\log(P/D)$$ on the market is about four percent lower.

Those numbers are a level for one claim. They are not a ranking across firms.

## 7.3 Valuations

Value is the cheap claim. Green firms, like the robust-profitability leg, often sell at a higher valuation ratio. A transition premium with rich green prices is a joint restriction on $$\Gamma^i$$ and $$\mu$$: policy loading larger on brown, mean growth larger on green by enough to keep that claim expensive.

Physical exposure is closer to book-to-market. The exposed claim should occupy the high-return, cheaper side if $$\Omega^i$$ is the mechanism.

## 7.4 Mapping a sort onto $$(\mu,\phi,\Omega^i,\Gamma^i)$$

Equation (6) is extended by the two climate terms already in aggregate consumption.

$$
\Delta d_{t+1}=\mu+\phi x_t+\Omega^i Y_t+\Gamma^i(P_{t+1}-P_t)+\varphi\sigma_t u_{t+1}.
$$

Preferences, $$x_t$$, and the climate laws stay at the Melin–Zhang aggregate calibration. Only the claim-specific numbers change. Average returns do not enter.

| Loading | Estimated from | Effect on E$$[R]$$ | Effect on $$\log(P/D)$$ |
|:---|:---|:---|:---|
| $$\mu$$ | mean $$\Delta d$$ | negligible | rises with $$\mu$$ |
| $$\phi$$ | projection (19) of $$\Delta d$$ on lagged $$\Delta c$$ | rises with $$\phi$$ | falls with $$\phi$$ |
| $$\Omega^i$$ | projection of $$\Delta d$$ on $$Y$$ | rises with $$\Omega^i$$ | falls with $$\Omega^i$$ |
| $$\Gamma^i$$ | projection of $$\Delta d$$ on $$\Delta P$$ | rises with $$\Gamma^i$$ | falls with $$\Gamma^i$$ |
| $$\varphi,\alpha$$ | residual vol and consumption correlation | short-run | weak |

A climate sort that is value relabeled will show a $$\phi$$ ranking and flat $$\Omega^i$$ and $$\Gamma^i$$.

**Transition.** $$\Gamma^{\text{brown}}>\Gamma^{\text{green}}$$. Green may have a larger $$\mu$$. If $$\mu$$ is larger on green and $$\Gamma$$ is flat, the model can match a high green price and will not produce the premium.

**Physical.** $$\Omega^{\text{exposed}}>\Omega^{\text{sheltered}}$$. A lower $$\mu$$ on the exposed leg cheapens that claim and raises the predicted premium.

## 7.5 The restriction

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2}\Delta c_{t-k} + \tilde\Omega Y_{t-1} + \tilde\Gamma \Delta P_t + \varepsilon_t.
$$

| Sort | `short=` | `long=` |
|:---|:---|:---|
| Book-to-market | low B/M | high B/M |
| Transition | green | brown |
| Physical | sheltered | exposed |

The model prices a climate sort if four implications hold together. First, the high-return leg’s estimated climate loading exceeds the low-return leg’s. Second, the estimated $$\mu$$ ranking is the ranking the valuation pattern requires. Third, setting $$\Omega^i=\Gamma^i=0$$ does not already absorb the premium through $$\phi$$. Fourth, the Euler equation produces a premium of the same sign and a $$\log(P/D)$$ ranking that does not contradict the data.

Their twenty-percent rise in the market premium at $$3^{\circ}$$C is a level. This page asks whether the same IMRS assigns that level to the claims whose dividends move with $$Y_t$$ and $$P_t$$.

```python
from kiku_value_premium.calibration import calibrate_from_data, estimate_long_run_leverage
from kiku_value_premium.model import get_table_ii_params, ModelSolver, solve_analytical, print_value_premium
from kiku_value_premium.implications import compute_asset_pricing_moments, print_asset_pricing_moments

print(estimate_long_run_leverage(dc, dd_brown, window=2))
print(estimate_long_run_leverage(dc, dd_green, window=2))

dividends = calibrate_from_data(
    dc,
    frequency="annual",
    window=2,
    short=dd_green,
    long=dd_brown,
    market=dd_market,
)
for name in ("short", "long", "market"):
    d = dividends[name]
    print(name, d.mu, d.phi, d.phi_sigma, d.alpha)

params = get_table_ii_params()
params.dividends = dividends
print_value_premium(solve_analytical(params))

solver = ModelSolver(params, n_x=15, n_s=4, n_quad=7)
solver.solve()
print_asset_pricing_moments(compute_asset_pricing_moments(solver))
```

{: .package }
`calibrate_from_data` estimates $$(\mu,\phi,\varphi,\alpha)$$. It does not see $$Y_t$$ or $$P_t$$. The premium this snippet produces is the part of the sort already priced by $$\phi$$ and $$\mu$$. The remainder is the object the climate states would have to deliver.

## References

Melin, L., and F. Zhang. 2026. “Quantifying Climate Risk Premia.” EDHEC Climate Institute.

Bansal, R., D. Kiku, and M. Ochoa. 2016. “Price of Long-Run Temperature Shifts in Capital Markets.” NBER Working Paper 22529.

Bansal, R., D. Kiku, and M. Ochoa. 2019. “Climate Change Risk.” Working paper.

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Novy-Marx, R. 2013. “The Other Side of Value: The Gross Profitability Premium.” *Journal of Financial Economics* 108 (1): 1–28.
