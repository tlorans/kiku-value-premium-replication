---
title: 7. Climate risk premia
nav_order: 10
---

# 7. Climate risk premia
{: .no_toc }

1. TOC
{:toc}

Sections 2–5 price book-to-market claims. Section 6 maps profitability, investment, and size onto the same four loadings. Melin and Zhang (2026) put climate into the long-run risks consumption process and price a single market equity. Chronic physical damage and transition cost raise that claim’s premium by about twenty percent at three degrees of warming. I record their aggregate moments and state how a climate sort maps onto the cash-flow parameters of Section 3.

Those parameters are still chosen from consumption and dividends. Average brown–green returns are not used. Two further loadings appear, $$\Omega^i$$ on the persistent damage signal and $$\Gamma^i$$ on policy tightening. The objects to inspect after estimation are $$(\mu,\phi,\Omega^i,\Gamma^i)$$. A climate sort that differs only in $$\phi$$ is the value mechanism under another characteristic.

## 7.1 Construction

Melin and Zhang keep Epstein–Zin preferences and the persistent factor $$x_t$$. They add a temperature anomaly $$T_t$$, a policy target $$P_t$$, and a persistent damage and transition signal $$Y_t$$. Consumption growth is

$$
\Delta c_{t+1}=\mu+x_t+\Omega Y_t+\Gamma(P_{t+1}-P_t)+\sigma_{\eta}\eta_{t+1}.
$$

Temperature loads on the policy target and on activity, $$\Theta x_t$$. Market dividends are levered consumption plus the same climate terms. The IMRS is still equation (3). Closed forms for the risk-free rate and the equity premium follow from the same linearization as Section 3.4.

Two sorts correspond to the two climate terms. Transition ranks firms on carbon emissions or emission intensity. Physical ranks firms on location-based exposure to heat, flood, cyclone, or wildfire. Dividends are the Campbell–Shiller series of [Section 2]({% link empirical.md %}). Consumption remains NIPA nondurables and services. $$Y_t$$ and $$P_t$$ are aligned to the dividend year from the temperature and policy paths used to calibrate the aggregate module.

I do not take a stand on the sign of realized brown–green returns. Those spreads change sign across samples. The characteristic defines the legs. The Euler equation is asked to price the legs.

## 7.2 Aggregate moments

Melin and Zhang report the market claim under their NGFS-aligned path and under a no-climate counterfactual.

|  | Counterfactual | Climate calibration |
|:---|---:|---:|
| Share of ERP from short-run consumption | 31.1% | 27.9% |
| Share of ERP from long-run consumption | 68.9% | 56.3% |
| Share of ERP from temperature level | 0 | 11.6% |
| Share of ERP from temperature change | 0 | 0.6% |
| Share of ERP from the policy target | 0 | 3.6% |

At $$3^{\circ}$$C the equity premium is about twenty percent higher than in the counterfactual. The risk-free rate falls by about fifty basis points near peak warming and remains about twenty-five basis points lower at 2100. Mean $$\log(P/D)$$ on the market is about four percent lower. High-damage calibrations move the premium by twelve to twenty-five percent at the same temperature.

Those numbers are a level for one claim. They are not a ranking across firms. Bansal, Kiku, and Ochoa (2016, 2019) introduced climate into this class of model as disaster risk. Melin and Zhang price chronic, calibrated physical and transition risk, with activity feeding temperature. That is the aggregate fact I take as given. They price one claim. The dividend process they write is already asset-specific.

## 7.3 Valuations

Value in Section 2 is the cheap claim. Green firms, like the robust-profitability leg of Section 6, often sell at a higher valuation ratio. A transition premium with rich green prices is therefore a joint restriction on $$\Gamma^i$$ and $$\mu$$: policy loading larger on brown, mean growth larger on green by enough to keep that claim expensive.

Physical exposure is closer to book-to-market. Damages and adaptation costs lower expected cash flows. The exposed claim should occupy the high-return, cheaper side if $$\Omega^i$$ is the mechanism. A rich price on the exposed leg, with $$\Omega^{\text{exposed}}$$ larger, is the same contradiction Novy-Marx poses for a profitability sort that is priced only with $$\phi$$.

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

Temperature loads on $$x_t$$. A climate sort that is value relabeled will show a $$\phi$$ ranking and flat $$\Omega^i$$ and $$\Gamma^i$$. Shutting those two loadings to zero and rerunning Table II on the same dividends asks how much of the sort Section 3 already prices.

**Transition.** Brown dividends should fall when policy tightens: $$\Gamma^{\text{brown}}>\Gamma^{\text{green}}$$. That ranking is what produces a positive carbon premium. Green may have a larger $$\mu$$. If $$\mu$$ is larger on green and $$\Gamma$$ is flat, the model can match a high green price and will not produce the premium. If $$\Gamma$$ is reversed, policy risk is not the mechanism.

**Physical.** Exposed dividends should load more on the damage signal: $$\Omega^{\text{exposed}}>\Omega^{\text{sheltered}}$$. A lower $$\mu$$ on the exposed leg cheapens that claim and raises the predicted premium. That is the opposite of the profitability configuration in Section 6. Historical $$\Omega^i$$ understates the loading the investor prices if firms have already adapted.

**Short-run loadings.** $$\varphi$$ and $$\alpha$$ are not the climate mechanism. I still estimate them. I do not interpret a gap in residual dividend volatility as evidence that the model has priced transition or physical risk.

Book-to-market in Table II is the case in which $$\phi$$ and $$\mu$$ move together and $$\phi$$ wins the valuation ranking. Profitability is the case in which they must move together and $$\mu$$ must win. Transition is the case that can look like profitability on $$\mu$$ and like value on $$\Gamma$$. Physical is the case that should look like value on $$\Omega$$, with $$\mu$$ if anything lower on the exposed leg.

## 7.5 The restriction

I apply the analogue of equation (19) to each leg. The regressors are lagged consumption growth and the climate states,

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2}\Delta c_{t-k} + \tilde\Omega Y_{t-1} + \tilde\Gamma \Delta P_t + \varepsilon_t.
$$

These slopes are not in Table II and are not reported by Melin and Zhang for firm sorts. They are estimated from dividends, consumption, and the climate states. Preferences, aggregate consumption, and the climate module remain those of Melin and Zhang. The three claims the solver prices are a naming convention.

| Sort | `short=` | `long=` |
|:---|:---|:---|
| Book-to-market | low B/M | high B/M |
| Transition | green | brown |
| Physical | sheltered | exposed |

The model prices a climate sort if four implications hold together. First, the high-return leg’s estimated climate loading — $$\tilde\Gamma$$ for transition, $$\tilde\Omega$$ for physical — exceeds the low-return leg’s. Second, the estimated $$\mu$$ ranking is the ranking the valuation pattern requires: higher on green than on brown if green is to stay expensive; not higher on exposed than on sheltered if exposed is to stay cheap. Third, setting $$\Omega^i=\Gamma^i=0$$ does not already absorb the premium through $$\phi$$. Fourth, the Euler equation, given those loadings, produces a premium of the same sign as the hypothesis and a $$\log(P/D)$$ ranking that does not contradict the data.

Their twenty-percent rise in the market premium at $$3^{\circ}$$C is a level. The cross-section asks whether the same IMRS assigns that level to the claims whose dividends move with $$Y_t$$ and $$P_t$$.

A reversal on $$\Omega$$ or $$\Gamma$$ means the factor is not a climate cash-flow factor. A reversal on $$\mu$$, with the climate loading intact, means the model can match the premium and will miss the price. A reversal on the premium, with both rankings intact, means the investor of Sections 3–5, even after climate is put into consumption, cannot be recycled. A finding that only $$\phi$$ differs is Section 3, not this one.

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

The four printed numbers are the map with climate shut off. Compare `long.phi` to `short.phi` and `long.mu` to `short.mu` before attributing a spread to $$Y_t$$ or $$P_t$$. The additional slopes on $$Y$$ and $$\Delta P$$ identify $$\Omega^i$$ and $$\Gamma^i$$. Returns do not enter. Construction of the dividend series follows [Section 2]({% link empirical.md %}). The long and short roles follow [Section 6]({% link further.md %}).

{: .package }
`calibrate_from_data` estimates $$(\mu,\phi,\varphi,\alpha)$$. It does not see $$Y_t$$ or $$P_t$$. `solve_analytical` and `compute_asset_pricing_moments` price those four numbers under the Table II consumption process. The premium this snippet produces is the part of the sort already priced by Section 3. The remainder is the object the climate states would have to deliver.

## References

Melin, L., and F. Zhang. 2026. “Quantifying Climate Risk Premia.” EDHEC Climate Institute.

Bansal, R., D. Kiku, and M. Ochoa. 2016. “Price of Long-Run Temperature Shifts in Capital Markets.” NBER Working Paper 22529.

Bansal, R., D. Kiku, and M. Ochoa. 2019. “Climate Change Risk.” Working paper.

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.

Novy-Marx, R. 2013. “The Other Side of Value: The Gross Profitability Premium.” *Journal of Financial Economics* 108 (1): 1–28.
