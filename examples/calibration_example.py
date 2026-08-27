"""
Usage example: how the DividendParams are calibrated
(Kiku 2006, Section 4.3 and equation 19).

Run with:
    python examples/calibration_example.py
"""
from __future__ import annotations
import lrrcs as lrr
import numpy as np


def main():
    # ------------------------------------------------------------------
    # 1. Inspect the exact Table II parameters used by the package
    # ------------------------------------------------------------------
    divs = lrr.get_table_ii_dividends()
    lrr.print_calibration_summary(divs)
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

    phi_value = lrr.estimate_long_run_leverage(dc, dd_value, window=2)
    phi_growth = lrr.estimate_long_run_leverage(dc, dd_growth, window=2)

    print("\nEstimated long-run leverage (eq. 19) from synthetic annual data:")
    print(f"  Value-like series : φ̃ = {phi_value:.2f}")
    print(f"  Growth-like series: φ̃ = {phi_growth:.2f}")
    print("  (Value has a markedly higher loading, as in the paper.)")

    # ------------------------------------------------------------------
    # 3. Build DividendParams from the same series
    # ------------------------------------------------------------------
    custom = lrr.calibrate_from_data(
        dc, long=dd_value, short=dd_growth,
        frequency="annual", window=2,
    )
    print("\ncalibrate_from_data(...) produced:")
    for name, d in custom.items():
        print(f"  {name:8s}: μ={d.mu:.4f}, φ={d.phi}, φ_σ={d.phi_sigma}, α={d.alpha}")

    # You can then insert them into a ModelParams instance if desired:
    # params = lrr.get_default_params()
    # params.dividends = custom


if __name__ == "__main__":
    main()
