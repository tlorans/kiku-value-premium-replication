"""
Usage example: how the DividendParams are calibrated
(Kiku 2006, Section 4.3 and equation 19).

Run with:
    python examples/calibration_example.py
"""
from __future__ import annotations
import numpy as np

from lrrcs.calibration import (
    print_calibration_summary,
    get_table_ii_dividends,
    estimate_long_run_leverage,
)
from lrrcs.calibration.from_data import (
    calibrate_dividend_params_from_targets,
)
from lrrcs.model import ModelParams, get_default_params


def main():
    # ------------------------------------------------------------------
    # 1. Inspect the exact Table II parameters used by the package
    # ------------------------------------------------------------------
    divs = get_table_ii_dividends()
    print_calibration_summary(divs)
    print("\nget_table_ii_dividends() returns:")
    for name, d in divs.items():
        print(f"  {name:8s}: μ={d.mu:.4f}, φ={d.phi}, φ_σ={d.phi_sigma}, α={d.alpha}")

    # ------------------------------------------------------------------
    # 2. Recover φ from a (simulated or real) annual series via eq. (19)
    #    Δd_t = d0 + φ̃ * MA_2(Δc) + ε_t
    # ------------------------------------------------------------------
    rng = np.random.default_rng(42)
    n_years = 200

    # Simple illustrative series: consumption growth with a persistent component
    x = np.zeros(n_years)
    for t in range(1, n_years):
        x[t] = 0.8 * x[t - 1] + 0.01 * rng.normal()
    dc = 0.02 + x + 0.02 * rng.normal(size=n_years)          # annual Δc

    # Value-like dividend: high loading on the persistent factor
    dd_value = 0.03 + 3.5 * x + 0.08 * rng.normal(size=n_years)
    # Growth-like dividend: low loading on the persistent factor
    dd_growth = 0.02 + 0.5 * x + 0.10 * rng.normal(size=n_years)

    phi_value = estimate_long_run_leverage(dc, dd_value, window=2)
    phi_growth = estimate_long_run_leverage(dc, dd_growth, window=2)

    print("\nEstimated long-run leverage (eq. 19) from synthetic annual data:")
    print(f"  Value-like series : φ̃ = {phi_value:.2f}")
    print(f"  Growth-like series: φ̃ = {phi_growth:.2f}")
    print("  (Value has a markedly higher loading, as in the paper.)")

    # ------------------------------------------------------------------
    # 3. Build DividendParams from economic targets
    # ------------------------------------------------------------------
    custom = calibrate_dividend_params_from_targets(
        mean_annual_growth={"growth": 0.011, "value": 0.023, "market": 0.014},
        long_run_leverage={"growth": 2.6, "value": 6.2, "market": 2.8},
        short_run_vol_loading={"growth": 8.4, "value": 7.4, "market": 7.5},
        corr_with_consumption={"growth": 0.27, "value": 0.15, "market": 0.55},
    )
    print("\ncalibrate_dividend_params_from_targets(...) produced:")
    for name, d in custom.items():
        print(f"  {name:8s}: μ={d.mu:.4f}, φ={d.phi}, φ_σ={d.phi_sigma}, α={d.alpha}")

    # You can then insert them into a ModelParams instance if desired:
    # params = get_default_params()
    # params.dividends = custom


if __name__ == "__main__":
    main()
