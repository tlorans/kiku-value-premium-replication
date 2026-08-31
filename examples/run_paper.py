"""The whole paper, in the order Kiku (2006) presents it.

Run: uv run python examples/run_paper.py
"""
import lrrcs as lrr


def main():
    print("Kiku (2006) recipe — paper order")

    # Section 2: the empirical value premium the model has to explain.
    try:
        bm = lrr.build_annual_panel(refresh=False)
        print(lrr.table_i(bm))
    except Exception as exc:
        print(f"Section 2 skipped ({exc}). Continuing from Table II.")

    model = lrr.LongRunRisksModel()

    # Section 3.4: the log-linear reading of where the premium comes from.
    print(model.solve(method="analytical").summary())

    # Tables III–V: does the cash-flow side look like the data?
    print(model.simulate_cashflows(n_sims=20, years=74, seed=1))

    # Section 5: the quadrature solution and its population moments.
    print(model.solve().summary())

    # Table VII: statistics of 1000 artificial 74-year samples.
    print(model.simulate(n_samples=1000, years=74, seed=0).summary())


if __name__ == "__main__":
    main()
