"""Bansal, Kiku, and Yaron (2016), Tables 1 to 8 and Figures 1 and 2.

Every frame prints our value beside the paper's printed one. The GMM
fits are the slow part: the LRR grid, the No-Vol grid, the annual
specification, three fixed-frequency fits, the quarterly grid, and the
quarterly h = 1 fit. Allow about twenty minutes.

Run: uv run python examples/bky_jme.py
"""
from __future__ import annotations

from geap.lrr.estimation import (
    TABLE_3_LRR_MODEL,
    TABLE_3_LRR_RESIDUALS,
    TABLE_3_NOVOL_MODEL,
    TABLE_3_NOVOL_RESIDUALS,
    TABLE_5_ANNUAL_MODEL,
    TABLE_5_ANNUAL_RESIDUALS,
    estimate_bky,
    estimate_table7_claims,
    figure1_frame,
    figure2_irf,
    load_annual,
    load_cross_section,
    load_quarterly,
    long_run_variance_share,
    table1_frame,
    table2_frame,
    table3_compare,
    table4_annual_on_lrr_sims,
    table4_frame,
    table6_frame,
    table7_panel_a,
    table7_panel_b,
    table8_frame,
)


def show(title: str, frame) -> None:
    print()
    print(title)
    print(frame.to_string(index=False, float_format=lambda v: f"{v:.4g}"))


def main() -> None:
    panel = load_annual()
    print(f"annual sample n = {len(panel)}, {int(panel['year'].min())} to {int(panel['year'].max())}")
    show("Table 1", table1_frame(panel))

    fit = estimate_bky(panel)
    novol = estimate_bky(panel, stochastic_vol=False, n_starts=3)
    show("Table 2", table2_frame(fit, novol))
    show("Table 3, LRR", table3_compare(panel, fit, {**TABLE_3_LRR_MODEL, **TABLE_3_LRR_RESIDUALS}))
    show("Table 3, No-Vol", table3_compare(panel, novol, {**TABLE_3_NOVOL_MODEL, **TABLE_3_NOVOL_RESIDUALS}))
    print(f"\nlong-run share of var(dc) at the LRR estimates: {long_run_variance_share(fit.params, fit.h):.2f}")

    fig1 = figure1_frame(panel, fit.params, h=fit.h)
    print(f"\nFigure 1: mean x {fig1['x'].mean():.6f}, mean sigma2 {fig1['sigma2'].mean():.3e}")

    ann = estimate_bky(panel, h=1, n_starts=6)
    fits = {h: estimate_bky(panel, h=h, n_starts=3) for h in (26, 12, 4)}
    fits[1] = ann
    mc = table4_annual_on_lrr_sims(n_draws=20, years=86, seed=0, lrr_params=fits[12].params, lrr_h=12)
    show("Table 4", table4_frame(ann, mc))
    show("Table 5", table3_compare(panel, ann, {**TABLE_5_ANNUAL_MODEL, **TABLE_5_ANNUAL_RESIDUALS}))
    show("Table 6", table6_frame(fits))
    for h in (26, 12, 4, 1):
        print(f"h = {h:2d}  long-run share of var(dc) {long_run_variance_share(fits[h].params, h):.2f}")

    irf = figure2_irf(years=800, seed=0, lrr_params=fits[12].params, lrr_h=12, annual_params=ann.params)
    print(
        f"\nFigure 2 cumulative response at 20 years: LRR {irf.loc[20, 'dc_lrr']:.3f}, "
        f"annual {irf.loc[20, 'dc_annual']:.3f}"
    )

    portfolios = load_cross_section()
    claims = estimate_table7_claims(portfolios, market_params=fit.params, h=fit.h)
    show("Table 7, Panel A", table7_panel_a(claims, portfolios, fit.params, fit.h))
    show("Table 7, Panel B", table7_panel_b(claims, fit.params, fit.h, portfolios, panel, years=2000, seed=1))

    quarterly = load_quarterly()
    print(f"\nquarterly sample n = {len(quarterly)}")
    ta = estimate_bky(quarterly, n_starts=3)
    no_ta = estimate_bky(quarterly, h=1, n_starts=6)
    show("Table 8", table8_frame(ta, no_ta))


if __name__ == "__main__":
    main()
