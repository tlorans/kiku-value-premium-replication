---
title: Two free numbers
nav_order: 6
---

# Two free numbers

A DCF takes a cash-flow forecast from one model and a discount rate from another. This page prices the model's own value and growth claims the DCF way and reads off what it costs. Every number below is printed by `examples/dcf_counterfactual.py` on the Table II economy.

## A. One rate for everything

Discount both claims at the market's rate: the premium prices at 0.00. The data say six points.

The step is exact, not an estimate. A price is a present value at some rate; discount both claims at the same rate and each claim's implied expected return is that rate. The premium is zero at any rate you pick. The rate has no slot for the risk in the cash flows.

The ranking fails too. Value's model dividends grow 2.80 points a year faster than growth's, so the DCF prices value richer. The data print the opposite: value is cheaper (mean log P/D 3.25 against 3.61). One rate, and both facts are gone.

## B. A rate fitted to the CAPM

Fit the rate to the CAPM instead. On the affine solution, value's beta is 0.50 against growth's 0.89 (ratio 0.56): value's beta is *lower* while its premium is higher. The CAPM-fitted spread is (0.50 − 0.89) × (E[R_m] − r_f), a negative number: the wrong sign against six points. With the Table VII premium level it prices near −2.4.

<!-- Resolved (F1, 2026-08-28): `lrr.simulate_table_vii` now traces the Table VII object. On the paper grid the simulated annual CAPM beta ratio is 0.83 (0.91 at n_x=60) vs Kiku's printed 0.92; the 0.56 here remains the level-free affine count on monthly innovations. See NUMBERS.md, F1. -->

The puzzle is not an estimate. It is structural: a DCF has no slot where the riskiness of the cash flows enters the discount rate.

## C. A forecast is not a valuation

Raise value's loading on \\(x_t\\) from 6.2 to 7.4. In the DCF world the discount rate is an input, so it does not move: expected dividend growth rises from 6.04 to 7.07 percent a year, the price rises with it, and the implied expected return is unchanged. You have a forecast.

In equilibrium the same news moves both. The price-dividend elasticity to \\(x_t\\) rises from 88.9 to 108.2 and the long-run compensation from 0.80 to 0.97 percent. The difference between the two worlds is the premium.

Shock the cash flows and hold the price of risk fixed, and you have a forecast. In equilibrium, the same news moves both. The difference is the premium.

[Value versus growth]({{ '/cross-section.html' | relative_url }}) resolves the setup. The script behind this page is `examples/dcf_counterfactual.py`.
