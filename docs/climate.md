---
title: 7. Climate risk premia
nav_order: 10
---

# 7. Climate risk premia
{: .no_toc }

1. TOC
{:toc}

Sections 2–5 price book-to-market claims. Section 6 asks whether the same investor prices profitability, investment, and size. Melin and Zhang (2026) put climate into the long-run risks consumption process and price a single market claim. They find that chronic physical and transition risk raise the equity premium by about twenty percent at three degrees of warming, without tipping-point jumps. I record that aggregate result and state the cross-sectional restriction it implies.

The restriction is the same one I used for value. Climate states enter the investor’s consumption. Claims differ by how their dividends load on those states. Average brown–green returns are not a calibration target. Realized carbon premia change sign across samples; Donadelli, Grüning, and Hitzemann (2024) show why a transition path makes the realized spread a poor estimator of the expected one. Feeding that spread into the cash-flow step would assume the premium the model is asked to produce.

The four loadings of equation (6) remain. Two more appear. The objects to print after estimation are $$(\mu,\phi,\Omega,\Gamma)$$ on each leg, not a relabeled Table II $$\phi$$.

## 7.1 The aggregate claim

Melin and Zhang keep Epstein–Zin preferences and a persistent expected-growth factor $$x_t$$. They add a temperature anomaly $$T_t$$, a policy target $$P_t$$, and a persistent damage and transition signal $$Y_t$$. Consumption growth is

$$
\Delta c_{t+1}=\mu+x_t+\Omega Y_t+\Gamma(P_{t+1}-P_t)+\sigma_{\eta}\eta_{t+1}.
$$

Temperature loads on the policy target and on activity, $$\Theta x_t$$. Dividends are levered consumption plus the same climate terms. Closed forms for the risk-free rate and the equity premium follow. At their NGFS-aligned calibration the market equity premium is about twenty percent higher at $$3^{\circ}$$C than in a no-climate counterfactual. The risk-free rate falls and only partly recovers. In their Table 4 the share of the premium attributed to long-run consumption risk declines (about 69 percent to about 56 percent); temperature level and the policy target take the residual.

Bansal, Kiku, and Ochoa (2016, 2019) put climate into this class of model mainly as disaster or tipping risk. Melin and Zhang price chronic, calibrated physical damage and transition cost, with activity feeding temperature. That is the aggregate fact I take as given. They price one claim. The dividend process they write is already asset-specific. The cross-section is the test that remains.

## 7.2 Construction of the sorts

Two sorts correspond to the two channels in their consumption law.

**Transition.** Firms ranked on carbon emissions, emission intensity, or a brown–green characteristic. Bolton and Kacperczyk (2021, 2023) report a positive carbon premium in some samples. Pástor, Stambaugh, and Taylor (2022) report the opposite sign over 2013–2020. I do not choose among those realized spreads. I take the characteristic as defining the legs.

**Physical.** Firms ranked on location-based exposure to heat, flood, cyclone, or wildfire, or on a composite physical score. The high-exposure leg is the candidate long side only if the hypothesis is that physical damage is priced as long-horizon cash-flow risk.

A third observation is the leftover analogous to Fama and French (2015): small, high-emission, high-investment firms. That corner is not a univariate brown–green test.

Dividends are constructed as in [Section 2]({% link empirical.md %}). Consumption remains NIPA nondurables and services. Climate states $$Y_t$$ and $$P_t$$ are not in CRSP. They must be taken from the same sources Melin and Zhang use to calibrate the aggregate module — temperature anomalies and a policy or carbon-price path — and aligned to the dividend year.

## 7.3 Mapping a climate sort onto $$(\mu,\phi,\Omega,\Gamma)$$

Equation (6) is extended by the two climate terms that already sit in aggregate consumption:

$$
\Delta d_{t+1}=\mu+\phi x_t+\Omega^i Y_t+\Gamma^i(P_{t+1}-P_t)+\varphi\sigma_t u_{t+1}.
$$

$$\Omega^i$$ is the claim’s loading on the persistent damage signal. $$\Gamma^i$$ is its loading on policy tightening. Preferences, $$x_t$$, and the climate laws stay at the Melin–Zhang aggregate calibration. Only the claim-specific numbers change. Average returns do not enter.

| Loading | Estimated from | Effect on E$$[R]$$ | Effect on $$\log(P/D)$$ |
|:---|:---|:---|:---|
| $$\mu$$ | mean $$\Delta d$$ | negligible | rises with $$\mu$$ |
| $$\phi$$ | projection of $$\Delta d$$ on lagged $$\Delta c$$ | rises with $$\phi$$ | falls with $$\phi$$ |
| $$\Omega^i$$ | projection of $$\Delta d$$ on $$Y$$ | rises with $$\Omega^i$$ if $$Y$$ is bad news | falls with $$\Omega^i$$ |
| $$\Gamma^i$$ | projection of $$\Delta d$$ on $$\Delta P$$ | rises with $$\Gamma^i$$ if tightening is bad news | falls with $$\Gamma^i$$ |
| $$\varphi,\alpha$$ | residual vol and consumption-innovation correlation | short-run; not the climate mechanism | weak |

$$\phi$$ does not drop out. Temperature loads on $$x_t$$ in their law of motion. A climate sort that is only value relabeled will show a $$\phi$$ ranking and flat $$\Omega^i$$ and $$\Gamma^i$$. That null is part of the test. Shutting $$\Omega^i=\Gamma^i=0$$ and rerunning Table II on the same dividends asks how much of the sort the original long-run consumption mechanism already prices.

What the two sorts lead one to have in mind:

**Transition (brown versus green).** Brown cash flows are the claims that should fall when policy tightens. One expects $$\Gamma^{\text{brown}}>\Gamma^{\text{green}}$$. A long-run-risk account of a *positive* carbon premium also requires that the brown loading on the priced climate state exceed the green loading. Green firms can look like the robust-profitability leg of Section 6: higher mean growth, richer valuation. That ranking is a $$\mu$$ fact. If estimated $$\mu$$ is larger on green and estimated $$\Gamma$$ is flat, the model can match a high green price and will not produce a brown premium. If estimated $$\Gamma$$ is reversed, the premium is not compensation for policy risk in this IMRS. Realized green outperformance over a short window is consistent with a demand shift that does not change $$\Gamma$$ at all. The Euler equation then attributes nothing to climate states. That is a rejection of a risk interpretation, not a reason to retune $$\Gamma$$.

**Physical (exposed versus sheltered).** Exposed dividends should load more on $$Y_t$$: one expects $$\Omega^{\text{exposed}}>\Omega^{\text{sheltered}}$$. Adaptation and relocation make historical $$\Omega^i$$ a downward-biased measure of the loading the investor prices if firms have already moved. A lower $$\mu$$ on the exposed leg — damages and adaptation costs — cheapens that claim and raises the predicted premium. That is the opposite of the profitability configuration. If exposed firms sell at rich valuations, either $$\mu$$ is higher than the physical narrative allows or the model price ranking will be wrong.

**The leftover corner.** Small, brown, high-investment firms are the climate analogue of the Size-OP-Inv failure in Section 6. A low average return on that corner is a small $$\phi$$, a small $$\Omega$$ or $$\Gamma$$, or a large $$\mu$$. A large estimated climate loading on that corner would make the model predict the wrong sign.

Book-to-market in Table II is the case in which $$\phi$$ and $$\mu$$ move together and $$\phi$$ wins the valuation ranking. Profitability is the case in which they must move together and $$\mu$$ must win. Transition is the case that can look like profitability on $$\mu$$ and like value on $$\Gamma$$. Physical is the case that should look like value on $$\Omega$$, with $$\mu$$ if anything lower on the high-return leg. Those are the patterns to keep in view when the estimated loadings are on the table.

## 7.4 The restriction

I apply the analogue of equation (19) to each leg. The regressors are lagged consumption growth, as before, and the climate states:

$$
\Delta d_t = d_0 + \tilde\phi \sum_{k=1}^{2}\Delta c_{t-k} + \tilde\Omega Y_{t-1} + \tilde\Gamma \Delta P_t + \varepsilon_t.
$$

Kiku (2006) does not report these slopes. Melin and Zhang (2026) do not report them by firm sort. They are estimated from dividends, consumption, and the climate states, not copied from Table II and not taken from a brown–green return. Preferences, aggregate consumption, and the climate module remain those of Melin and Zhang. The three claims the solver prices are a naming convention.

| Sort | `short=` | `long=` |
|:---|:---|:---|
| Book-to-market | low B/M | high B/M |
| Transition | green | brown |
| Physical | sheltered | exposed |
| Climate leftover | small-green-conservative | small-brown-aggressive |

The leftover row is signed by the fact that needs explaining. Passing the low-return corner as `long=` will look like a high premium only if its estimated climate loading is large. That is the wrong ranking for that observation.

The model prices a climate sort if four implications hold together. First, the high-return leg’s estimated climate loading — $$\tilde\Gamma$$ for transition, $$\tilde\Omega$$ for physical — exceeds the low-return leg’s. Second, the estimated $$\mu$$ ranking is the ranking the valuation pattern requires: higher on green than on brown if green is to stay expensive; not higher on exposed than on sheltered if exposed is to stay cheap. Third, shutting $$\Omega^i=\Gamma^i=0$$ does not already absorb the premium through $$\phi$$ alone; otherwise the sort is value in another characteristic. Fourth, the Euler equation, given those loadings and the Melin–Zhang investor, produces a premium of the same sign as the hypothesis and a $$\log(P/D)$$ ranking that does not contradict the data. Their twenty-percent rise in the *market* premium at $$3^{\circ}$$C is a level. The cross-section asks whether the same IMRS assigns that level to the claims whose dividends actually move with $$Y_t$$ and $$P_t$$.

A reversal on $$\Omega$$ or $$\Gamma$$ means the factor is not a climate cash-flow factor in this model. A reversal on $$\mu$$, with the climate loading intact, means the model can match the premium and will miss the price. A reversal on the premium, with both rankings intact, means the Table II investor, even after climate is put into consumption, cannot be recycled. A finding that only $$\phi$$ differs is the value mechanism, not Melin and Zhang’s.

`calibrate_from_data` as shipped estimates $$(\mu,\phi,\varphi,\alpha)$$. It does not see $$Y_t$$ or $$P_t$$. The climate slopes are the additional projection above. Assign the high-exposure or high-carbon series to `long=` only when that is the hypothesis under test.

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

The four printed numbers are the no-climate map. Compare `long.phi` to `short.phi` before attributing a spread to $$Y_t$$ or $$P_t$$. The climate residuals of the projection in this section are what would identify $$\Omega^i$$ and $$\Gamma^i$$. Returns do not enter. Campbell–Shiller construction follows [Section 2]({% link empirical.md %}). The long/short roles follow [Section 6]({% link further.md %}).

{: .package }
`solve_analytical` and `compute_asset_pricing_moments` price whatever dividends they are given, under the Table II consumption process. They do not contain $$T_t$$, $$P_t$$, or $$Y_t$$. A climate premium computed from this snippet is the part of the sort already priced by $$\phi$$ and $$\mu$$. The remainder is the object Melin and Zhang’s states would have to deliver.

## References

Melin, L., and F. Zhang. 2026. “Quantifying Climate Risk Premia.” EDHEC Climate Institute.

Bansal, R., D. Kiku, and M. Ochoa. 2016. “Price of Long-Run Temperature Shifts in Capital Markets.” NBER Working Paper 22529.

Bansal, R., D. Kiku, and M. Ochoa. 2019. “Climate Change Risk.” Working paper.

Bolton, P., and M. Kacperczyk. 2021. “Do Investors Care about Carbon Risk?” *Journal of Financial Economics* 142 (2): 517–549.

Bolton, P., and M. Kacperczyk. 2023. “Global Pricing of Carbon-Transition Risk.” *Journal of Finance* 78 (6): 3677–3754.

Pástor, Ľ., R. Stambaugh, and L. Taylor. 2022. “Dissecting Green Returns.” *Journal of Financial Economics* 146 (2): 403–424.

Donadelli, M., P. Grüning, and S. Hitzemann. 2024. “Carbon Returns and Risk Premia in a Macro-Finance Model for the Climate Transition.” Working paper.

Fama, E., and K. French. 2015. “A Five-Factor Asset Pricing Model.” *Journal of Financial Economics* 116 (1): 1–22.
