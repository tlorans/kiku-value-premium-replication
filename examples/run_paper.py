import lrrcs as lrr


def main():
    print("Kiku (2006) recipe — paper order")
    try:
        bm = lrr.build_annual_panel(refresh=False)
        print(lrr.table_i(bm))
    except Exception as exc:
        print(f"Section 2 skipped ({exc}). Continuing from Table II.")
    params = lrr.get_table_ii_params()
    lrr.print_long_short_premium(lrr.solve_analytical(params))
    print(lrr.simulate_cashflow_moments(n_sims=20, years=74, seed=1))
    solver = lrr.ModelSolver(params, n_x=30, n_s=4)
    solver.solve()
    lrr.print_asset_pricing_moments(lrr.compute_asset_pricing_moments(solver))
    tab = lrr.simulate_table_vii(solver, n_samples=1000, years=74, seed=0)
    lrr.print_table_vii(tab)


if __name__ == "__main__":
    main()
