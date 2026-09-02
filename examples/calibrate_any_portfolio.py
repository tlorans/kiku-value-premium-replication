#!/usr/bin/env python
"""Calibrate any cross-section from cash flows, then price it.

The complete workflow for any set of portfolios (industry, size,
book-to-market, quality, and so on):

  1. Obtain annual series of consumption growth (dc) and dividend growth
     for each portfolio (dd).
  2. Turn each series into a ClaimParams with calibrate_claims.
  3. Put them in a model, solve it, and compare two of them.

Returns never enter step 2. That is the paper's identification
discipline: the cross-section is disciplined by cash flows alone, so the
premium the model produces is a prediction rather than a fit.

Here the series are synthetic so the script is self-contained. Replace
generate_synthetic_annual_series with your own data to analyse a real
cross-section.

Run: uv run python examples/calibrate_any_portfolio.py
"""
from __future__ import annotations

import numpy as np

import geap


def generate_synthetic_annual_series(n_years: int = 74, seed: int = 42):
    """Synthetic annual series that mimic the paper's ranking.

    Value loads heavily on the persistent component of consumption
    growth, growth barely loads on it, and the market sits in between.
    """
    rng = np.random.default_rng(seed)

    x = np.zeros(n_years)
    for t in range(1, n_years):
        x[t] = 0.6 * x[t - 1] + 0.01 * rng.standard_normal()

    dc = 0.02 + x + 0.015 * rng.standard_normal(n_years)
    dd_value = 0.025 + 3.5 * x + 0.12 * rng.standard_normal(n_years)   # high phi
    dd_growth = 0.015 + 0.4 * x + 0.18 * rng.standard_normal(n_years)  # low phi
    dd_market = 0.020 + 1.5 * x + 0.10 * rng.standard_normal(n_years)  # medium
    return dc, dd_value, dd_growth, dd_market


def main():
    print("=" * 70)
    print("Calibrate any cross-section from cash flows, then price it")
    print("=" * 70)

    # 1. Data. Replace this block with your own annual series.
    dc, dd_value, dd_growth, dd_market = generate_synthetic_annual_series()
    print("\nSynthetic annual series generated (74 years).")

    # 2. Measure the long-run leverage of each leg (equation 19).
    phi_value = geap.estimate_long_run_leverage(dc, dd_value, window=2)
    phi_growth = geap.estimate_long_run_leverage(dc, dd_growth, window=2)
    print(f"\nDirect eq.-19 estimates: value phi = {phi_value:.2f}, "
          f"growth phi = {phi_growth:.2f}")

    # 3. Build the model from those same cash flows.
    claims = geap.calibrate_claims(
        dc,
        {"value": dd_value, "growth": dd_growth, "market": dd_market},
        frequency="annual",
        window=2,          # paper uses a 2-year moving average
    )
    model = geap.LongRunRisksModel(claims=claims)

    print("\nCalibrated cash-flow parameters:")
    print(f"  {'claim':8s} {'mu':>9s} {'phi':>8s} {'phi_sigma':>10s} {'alpha':>7s}")
    for name, d in model.params.claims.items():
        print(f"  {name:8s} {d.mu:9.5f} {d.phi:8.3f} {d.phi_sigma:10.2f} {d.alpha:7.2f}")

    # 4. Price the claims, then compare two of them.
    res = model.solve(method="analytical")
    print()
    print(res.summary())
    print()
    print(res.compare("value", "growth").summary())

    print("\nThe leg with the highest estimated phi receives the largest")
    print("long-run risk premium. That is the mechanism behind the value")
    print("premium in Kiku (2006), and it transfers to any cross-section")
    print("whose cash flows differ in their exposure to persistent")
    print("consumption growth.")


if __name__ == "__main__":
    main()
