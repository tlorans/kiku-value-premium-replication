"""Render tutorial figures and print table outputs used in the book chapters."""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import polars as pl
import plotnine as p9
import lrrcs as lrr

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
FIG = ROOT / "docs" / "figures"
FIG.mkdir(parents=True, exist_ok=True)

W, H = 7.2, 3.4


def _save(plot, name: str) -> None:
    path = FIG / name
    plot.save(str(path), width=W, height=H, dpi=120, verbose=False)
    print(f"wrote {path.relative_to(ROOT)}")


def main() -> None:
    dc = pl.read_csv(DATA / "consumption_annual.csv").sort("year")
    panel = pl.read_csv(DATA / "annual_panel.csv")
    mkt = panel.filter(pl.col("claim") == "Market").join(dc, on="year")

    _save(
        p9.ggplot(dc.to_pandas(), p9.aes("year", "dc"))
        + p9.geom_line()
        + p9.labs(x="Year", y="Δc", title="Real per-capita ND+S growth, 1930–2003"),
        "consumption_growth.svg",
    )
    _save(
        p9.ggplot(mkt.to_pandas(), p9.aes("dc", "dgrowth"))
        + p9.geom_point()
        + p9.labs(x="Δc", y="Market Δd", title="Cash flows, not returns"),
        "market_dd_vs_dc.svg",
    )
    _save(
        p9.ggplot(
            mkt.with_columns(pl.col("pd").log().alias("log_pd")).to_pandas(),
            p9.aes("year", "log_pd"),
        )
        + p9.geom_line()
        + p9.labs(x="Year", y="log(P/D)", title="Market price–dividend, 1930–2003"),
        "market_log_pd.svg",
    )

    plot_df = dc.with_columns(
        pl.col("dc").shift(1).rolling_mean(window_size=2).alias("ma")
    ).drop_nulls()
    _save(
        p9.ggplot(plot_df.to_pandas(), p9.aes("year"))
        + p9.geom_line(p9.aes(y="dc"))
        + p9.geom_line(p9.aes(y="ma"), color="steelblue")
        + p9.labs(
            x="Year",
            y="Δc",
            title="Consumption growth and a two-year MA of lags",
        ),
        "consumption_ma.svg",
    )

    out = lrr.filter_expected_growth(dc["dc"])
    plot_xt = dc.with_columns(
        pl.Series("ma", lrr.expected_growth_proxy(dc["dc"], window=2)),
        pl.Series("x_filt", out["x"]),
    ).drop_nulls()
    _save(
        p9.ggplot(plot_xt.to_pandas(), p9.aes("year"))
        + p9.geom_line(p9.aes(y="dc"))
        + p9.geom_line(p9.aes(y="ma"), color="steelblue")
        + p9.geom_line(p9.aes(y="x_filt"), color="darkorange")
        + p9.labs(x="Year", y="Δc", title="MA proxy and filtered x̂_t"),
        "xt_proxy_filter.svg",
    )

    params = lrr.get_table_ii_params()
    path = lrr.Dynamics(params, seed=1).simulate_cashflows(T=74 * 12)
    sol = lrr.solve_analytical(params)
    x = path["x"]
    s2 = path["sigma2"]
    z = (
        sol.mean_log_pd["market"]
        + sol.A1["market"] * x
        + sol.A2["market"] * (s2 - params.cons.sigma**2)
    )
    sim = pl.DataFrame(
        {"t": np.arange(len(x)), "x": x, "dd": path["dd_market"], "log_pd": z}
    ).to_pandas()
    _save(
        p9.ggplot(sim, p9.aes("t", "x"))
        + p9.geom_line()
        + p9.labs(x="Month", y="x_t", title="Simulated long-run risk"),
        "sim_xt.svg",
    )
    _save(
        p9.ggplot(sim, p9.aes("t", "dd"))
        + p9.geom_line()
        + p9.labs(x="Month", y="Δd", title="Simulated market dividend growth"),
        "sim_dd.svg",
    )
    _save(
        p9.ggplot(sim, p9.aes("t", "log_pd"))
        + p9.geom_line()
        + p9.labs(x="Month", y="log(P/D)", title="Model price–dividend along the path"),
        "sim_log_pd.svg",
    )

    print("\n=== table_i ===")
    bm = pd.read_csv(DATA / "annual_panel.csv")
    print(lrr.table_i(bm).to_string(index=False))

    print("\n=== filter rho ===")
    print({k: out[k] for k in ("mu", "rho", "q", "r", "loglik")})

    joined = mkt.join(dc, on="year").drop_nulls()
    phi = lrr.estimate_long_run_leverage(joined["dc"], joined["dgrowth"], window=2)
    print("\n=== phi_tilde ===", phi)
    div = lrr.calibrate_from_data(
        joined["dc"].to_numpy(),
        market=joined["dgrowth"].to_numpy(),
        frequency="annual",
        window=2,
    )
    print("\n=== calibrate_from_data market ===")
    lrr.print_calibration_summary(div)

    print("\n=== simulate_cashflow_moments n_sims=20 ===")
    lrr.print_moments(
        lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1, params=params)
    )

    print("\n=== print_long_short_premium ===")
    lrr.print_long_short_premium(sol)


if __name__ == "__main__":
    main()
