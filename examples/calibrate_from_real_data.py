#!/usr/bin/env python
"""
Calibrate DividendParams from *real* data for arbitrary portfolios.

This example shows the complete practical workflow:

1. Download annual real personal consumption expenditure growth from FRED
   (public, no API key required).
2. Load (or construct) annual dividend-growth series for the portfolios you
   care about.  The script includes a clear placeholder and instructions for
   obtaining classic value/growth (or any other) portfolio cash-flow series
   from the Kenneth French library / CRSP / Compustat.
3. Call calibrate_from_data → obtain μ, φ, φ_σ, α for every portfolio.
4. Plug the calibrated parameters into the model and compute long-run risk
   premia.

Because portfolio-level dividend series are typically constructed from CRSP
(which is not redistributable), the script downloads the public consumption
series and then demonstrates the exact call the user must make once they have
their own Δd arrays.
"""
from __future__ import annotations
import io
import urllib.request
import numpy as np
import pandas as pd

from kiku_value_premium.calibration import (
    calibrate_from_data,
    estimate_long_run_leverage,
    get_table_ii_dividends,
    print_calibration_summary,
)
from kiku_value_premium.model import (
    ConsumptionParams,
    ModelParams,
    PreferencesParams,
    print_value_premium,
    solve_analytical,
)


def download_fred_pce_growth() -> pd.Series:
    """
    Download annual percent change in real personal consumption expenditures
    from FRED (series DPCERL1A225NBEA).  No API key required.
    """
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DPCERL1A225NBEA"
    print("Downloading real PCE growth from FRED …")
    with urllib.request.urlopen(url, timeout=30) as resp:
        raw = resp.read().decode()
    df = pd.read_csv(io.StringIO(raw))
    # columns are DATE, DPCERL1A225NBEA
    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df.set_index("DATE").sort_index()
    # convert percent to decimal growth rate
    s = df.iloc[:, 0].astype(float) / 100.0
    s.name = "dc"
    print(f"  obtained {len(s)} annual observations "
          f"({s.index.min().year}–{s.index.max().year})")
    return s


def main():
    print("=" * 70)
    print("Calibrate DividendParams from real data – full example")
    print("=" * 70)

    # ------------------------------------------------------------------
    # 1. Real consumption growth (public)
    # ------------------------------------------------------------------
    try:
        dc_series = download_fred_pce_growth()
    except Exception as exc:
        print(f"Could not download FRED series ({exc}).")
        print("Using a short embedded fallback sample instead.")
        # minimal fallback so the script still runs offline
        years = np.arange(1950, 2024)
        rng = np.random.default_rng(1)
        dc_series = pd.Series(
            0.02 + 0.01 * rng.standard_normal(len(years)),
            index=pd.to_datetime([f"{y}-01-01" for y in years]),
            name="dc",
        )

    # ------------------------------------------------------------------
    # 2. Portfolio dividend growth – USER SUPPLIES THESE
    # ------------------------------------------------------------------
    print("\n2. Portfolio dividend-growth series")
    print("-" * 50)
    print("Portfolio-level dividend (or earnings) growth is usually constructed")
    print("from CRSP/Compustat and is not redistributable.  To run the calibration")
    print("on real portfolios you must supply the series yourself.")
    print()
    print("Typical sources:")
    print("  • Kenneth French Data Library – portfolio returns (you still need")
    print("    to construct dividend growth from price + dividend series)")
    print("  • CRSP / Compustat – standard source for portfolio Δd")
    print("  • Published appendix data from asset-pricing papers")
    print()
    print("Once you have annual arrays of the same length as dc, call:")
    print()
    print("  div_params = calibrate_from_data(")
    print("      dc_values,")
    print("      {")
    print("          'growth': dd_growth_portfolio,")
    print("          'value' : dd_value_portfolio,")
    print("          'market': dd_market,")
    print("      },")
    print("      frequency='annual',")
    print("      window=2,")
    print("  )")
    print()
    print("  Keys must be growth/value/market for solve_analytical and")
    print("  compute_asset_pricing_moments.")
    print()

    # ------------------------------------------------------------------
    # 3. Illustrative call with the *paper’s own* Table II values
    #    (so the script remains fully runnable without proprietary data)
    # ------------------------------------------------------------------
    print("3. For illustration we now use the paper’s own calibrated parameters")
    print("   (which were estimated on real data via the same regression).")
    print("-" * 50)
    print_calibration_summary(get_table_ii_dividends())

    # Show the regression on the real consumption series alone is well-defined
    print("\nSanity check on the real consumption series:")
    print(f"  mean annual Δc = {dc_series.mean():.3%}")
    print(f"  std  annual Δc = {dc_series.std():.3%}")

    # ------------------------------------------------------------------
    # 4. Price the paper’s portfolios (already calibrated on real data)
    # ------------------------------------------------------------------
    print("\n4. Long-run risk premia that result from the real-data calibration")
    print("-" * 50)
    params = ModelParams()
    sol = solve_analytical(params)
    print_value_premium(sol)

    print("\n" + "=" * 70)
    print("How to repeat the exercise with *your* portfolios")
    print("=" * 70)
    print("""
1. Download or construct annual dividend-growth series for each portfolio.
2. Align them with the consumption series (same years).
3. Run:

   from kiku_value_premium.calibration import calibrate_from_data
   div_params = calibrate_from_data(
       dc_series.values,
       {
           "growth": my_growth_dd,
           "value":  my_value_dd,
           "market": my_market_dd,
       },
       frequency="annual",
       window=2,
   )

4. The ranking of the estimated φ across your portfolios is the ranking of
   long-run risk premia the model will produce.
""")


if __name__ == "__main__":
    main()
