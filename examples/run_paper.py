def main():
    print("Kiku (2006) recipe — paper order")
    try:
        from lrrcs.empirical import START, END, build_annual_panel, table_i
        bm = build_annual_panel(refresh=False)
        print(table_i(bm, START, END))
    except Exception as exc:
        print(f"Section 2 skipped ({exc}). Continuing from Table II.")
    from lrrcs.model import get_table_ii_params, solve_analytical, ModelSolver, print_long_short_premium
    from lrrcs.calibration import simulate_cashflow_moments
    from lrrcs.implications import compute_asset_pricing_moments, print_asset_pricing_moments
    params = get_table_ii_params()
    print_long_short_premium(solve_analytical(params))
    print(simulate_cashflow_moments(n_sims=20, years=74, seed=1))
    solver = ModelSolver(params, n_x=15, n_s=4, n_quad=7)
    solver.solve()
    print_asset_pricing_moments(compute_asset_pricing_moments(solver))


if __name__ == "__main__":
    main()
