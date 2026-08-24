#!/usr/bin/env python
"""
Full example: calibrate DividendParams for arbitrary portfolios and price them.

This script shows the complete workflow a user would follow for any set of
portfolios (industry, size, book-to-market, quality, …):

  1. Obtain annual (or monthly) series of consumption growth (dc) and
     dividend growth for each portfolio (dd).
  2. Call calibrate_from_data → gets μ, φ, φ_σ, α for every portfolio.
  3. Insert the resulting DividendParams into ModelParams.
  4. Run the analytical (or numerical) solution to see the risk premia.

Here we use synthetic series so the example is fully self-contained.
Replace the synthetic generation with your own data to analyse real portfolios.
"""
from __future__ import annotations
import numpy as np

from kiku_value_premium.calibration import (
    calibrate_from_data,
    estimate_long_run_leverage,
    print_calibration_summary,
)
from kiku_value_premium.params import ModelParams, PreferencesParams, ConsumptionParams
from kiku_value_premium.analytical import solve_analytical, print_value_premium


def generate_synthetic_annual_series(n_years: int = 74, seed: int = 42):
    """
    Create synthetic annual consumption and dividend growth series that mimic
    the paper’s ranking:
      - Value-like portfolio has high loading on the persistent component of Δc
      - Growth-like portfolio has low loading
      - A third “Quality” portfolio sits in between
    """
    rng = np.random.default_rng(seed)

    # Simple persistent component for expected growth (annual)
    x = np.zeros(n_years)
    for t in range(1, n_years):
        x[t] = 0.6 * x[t - 1] + 0.01 * rng.standard_normal()

    # Consumption growth
    dc = 0.02 + x + 0.015 * rng.standard_normal(n_years)

    # Portfolio dividend growth = mean + φ * x + short-run shock
    # Higher φ → stronger long-run risk exposure
    dd_value = 0.025 + 3.5 * x + 0.12 * rng.standard_normal(n_years)   # high φ
    dd_growth = 0.015 + 0.4 * x + 0.18 * rng.standard_normal(n_years)  # low φ
    dd_quality = 0.020 + 1.5 * x + 0.10 * rng.standard_normal(n_years) # medium

    return dc, {
        "ValueLike": dd_value,
        "GrowthLike": dd_growth,
        "Quality": dd_quality,
    }


def main():
    print("=" * 70)
    print("Calibrate DividendParams for arbitrary portfolios – full example")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Data (replace this block with your own annual series)
    # ------------------------------------------------------------------
    dc, dd_dict = generate_synthetic_annual_series(n_years=74)
    print("\nSynthetic annual series generated (74 years).")
    print("Replace generate_synthetic_annual_series() with your real data.")

    # ------------------------------------------------------------------
    # 2. Calibrate from data (paper’s procedure applied to any portfolios)
    # ------------------------------------------------------------------
    print("\n2. Running calibrate_from_data …")
    div_params = calibrate_from_data(
        dc,
        dd_dict,
        frequency="annual",
        window=2,                 # paper uses a 2-year MA
        default_phi_sigma=7.5,
    )

    print("\nEstimated DividendParams:")
    print(f"{'Portfolio':12s} {'μ (mo)':>8s} {'φ (LR)':>8s} {'φ_σ':>8s} {'α':>8s}")
    print("-" * 50)
    for name, d in div_params.items():
        print(f"{name:12s} {d.mu:8.4f} {d.phi:8.2f} {d.phi_sigma:8.1f} {d.alpha:8.2f}")

    # Also show the pure regression for one portfolio
    phi_value = estimate_long_run_leverage(dc, dd_dict["ValueLike"], window=2)
    phi_growth = estimate_long_run_leverage(dc, dd_dict["GrowthLike"], window=2)
    print(f"\nDirect eq.-19 estimates:  ValueLike φ̃ = {phi_value:.2f},  "
          f"GrowthLike φ̃ = {phi_growth:.2f}")

    # ------------------------------------------------------------------
    # 3. Plug into the model
    # ------------------------------------------------------------------
    print("\n3. Building ModelParams with the calibrated dividends …")
    params = ModelParams(
        prefs=PreferencesParams(),          # paper defaults (δ,γ,ψ)
        cons=ConsumptionParams(),           # paper defaults
        dividends=div_params,
    )

    # ------------------------------------------------------------------
    # 4. Price the claims – analytical long-run risk premia
    # ------------------------------------------------------------------
    print("\n4. Analytical long-run risk premia for the calibrated portfolios")
    print("-" * 60)
    sol = solve_analytical(params)
    print_value_premium(sol)

    print("\nInterpretation:")
    print("  The portfolio with the highest estimated φ (ValueLike) receives")
    print("  the largest long-run risk premium.  That is exactly the mechanism")
    print("  that generates the value premium in Kiku (2006).")
    print("\nDone.  Swap the synthetic series for real portfolio data to analyse")
    print("any cross-section you care about.")


if __name__ == "__main__":
    main()
