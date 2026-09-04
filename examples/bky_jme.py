"""Bansal, Kiku, and Yaron (2016, JME) in the paper's order.

Run: uv run python examples/bky_jme.py
"""
from __future__ import annotations

from geap.lrr.estimation import (
    COLD_START,
    TABLE_2_LRR,
    TABLE_2_LRR_H,
    TABLE_2_NOVOL,
    TABLE_2_NOVOL_H,
    TABLE_4_ANNUAL,
    TABLE_8_H,
    TABLE_8_TA,
    estimate_bky,
    figure1_frame,
    figure2_irf,
    load_annual,
    load_cross_section,
    load_quarterly,
    long_run_variance_share,
    model_moments,
    sample_moments,
    table3_frame,
    table5_frame,
    table7_capm,
    table7_premia,
)
from geap.lrr.estimation.goldens import (
    TABLE_1,
    TABLE_3_LRR_MODEL,
    TABLE_3_NOVOL_MODEL,
    TABLE_5_ANNUAL_MODEL,
    TABLE_6,
    TABLE_7_PREMIA_MODEL,
    TABLE_8_NO_TA,
)


def _print_params(title, p, h):
    print(f"{title}, h = {h}")
    for name in (
        "gamma", "psi", "delta", "mu_c", "rho", "phi_e", "sigma",
        "nu", "sigma_w", "mu_d", "phi_d", "phi_d_sigma", "rho_d",
    ):
        print(f"  {name:16s} {getattr(p, name)}")


def main():
    print("Bansal, Kiku, Yaron (2016) - annual sample 1930-2015")
    data = load_annual()
    samp = sample_moments(data)
    print("Table 1 (sample)")
    for key in (
        "dc_mean", "dc_std", "dd_mean", "dd_std", "rm_mean", "rm_std",
        "log_pd_mean", "log_pd_std", "rf_mean", "rf_std",
    ):
        print(f"  {key:16s} {samp[key]:8.4f}   paper {TABLE_1[key]:8.4f}")

    print()
    _print_params("Table 2 LRR (published)", TABLE_2_LRR, TABLE_2_LRR_H)
    print()
    _print_params("Table 2 No-Vol (published)", TABLE_2_NOVOL, TABLE_2_NOVOL_H)

    print()
    print("Table 2 LRR, GMM on the annual panel (Bansal-Yaron 2004 start)")
    print(
        f"  start  gamma={COLD_START.gamma}  psi={COLD_START.psi}  "
        f"phi_d={COLD_START.phi_d}"
    )
    fit = estimate_bky(data, start=COLD_START)
    print(fit.summary())

    print()
    print("Table 3 LRR sample, model, t(diff) at the published Table 2 vector")
    print(table3_frame(data, TABLE_2_LRR, TABLE_2_LRR_H).to_string(index=False))
    print("  paper model column", TABLE_3_LRR_MODEL)

    print()
    print("Table 3 No-Vol model column at the published Table 2 vector")
    mn = model_moments(TABLE_2_NOVOL, TABLE_2_NOVOL_H)
    for key, paper in TABLE_3_NOVOL_MODEL.items():
        print(f"  {key:16s} {mn[key]:8.4f}   paper {paper:8.4f}")

    print()
    print("Figure 1 extracted states")
    fig1 = figure1_frame(data)
    print(f"  mean x      {fig1['x'].mean(): .6f}")
    print(f"  mean sigma2 {fig1['sigma2'].mean(): .6e}")

    print()
    print("Table 4/5 annual specification (h = 1)")
    print(table5_frame(data, TABLE_4_ANNUAL, h=1).to_string(index=False))
    print("  paper model column", TABLE_5_ANNUAL_MODEL)
    print(
        "  LRR share of var(dc) "
        f"{long_run_variance_share(TABLE_2_LRR, TABLE_2_LRR_H):.2f}  "
        f"annual spec {long_run_variance_share(TABLE_4_ANNUAL, 1):.2f}"
    )

    print()
    print("Table 6 model equity premium by fixed h")
    for h, p in TABLE_6.items():
        mm = model_moments(p, h)
        print(f"  h={h:<3d}  premium {mm['mean_excess']:.3f}  rf {mm['mean_rf']:.3f}")

    print()
    print("Figure 2 IRF (horizon 20)")
    irf = figure2_irf(horizon=21, years=300, seed=0)
    print(f"  cum dc LRR     {irf.loc[20, 'dc_lrr']:.3f}")
    print(f"  cum dc annual  {irf.loc[20, 'dc_annual']:.3f}")

    print()
    print("Table 7 model premia (%)")
    prem = table7_premia()
    for name, paper in TABLE_7_PREMIA_MODEL.items():
        print(f"  {name:8s} {prem[name]:6.2f}   paper {paper:6.2f}")
    capm = table7_capm(years=400, seed=1)
    print("Table 7 CAPM")
    for spread, row in capm.items():
        print(
            f"  {spread:16s} beta {row['beta_model']:.2f}  "
            f"alpha {row['alpha_model']:.2f}%"
        )
    xs = load_cross_section().groupby("claim")["ret"].mean() * 100
    print("  sample E[R] %", {k: round(float(v), 2) for k, v in xs.items()})

    print()
    q = load_quarterly()
    print(f"Table 8 quarterly sample {q['date'].dt.year.min()}-{q['date'].dt.year.max()}  n={len(q)}")
    mq = model_moments(TABLE_8_TA, TABLE_8_H)
    mq0 = model_moments(TABLE_8_NO_TA, 1)
    print(f"  with TA     gamma={TABLE_8_TA.gamma}  h={TABLE_8_H}  rf={mq['mean_rf']:.4f}")
    print(f"  no TA       gamma={TABLE_8_NO_TA.gamma}  h=1  rf={mq0['mean_rf']:.4f}")


if __name__ == "__main__":
    main()
