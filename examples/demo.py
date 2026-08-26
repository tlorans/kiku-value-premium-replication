#!/usr/bin/env python
"""
Quick demonstration of Kiku (2006) value-premium mechanism.

Run from the repository root after `pip install -e .`:
    python examples/demo.py
"""
from kiku_value_premium.model import solve_analytical, print_value_premium
from kiku_value_premium.calibration import simulate_cashflow_moments, print_moments

def main():
    print("=" * 60)
    print("Kiku (2006) – Is the Value Premium a Puzzle? – Demo")
    print("=" * 60)

    print("\n1. Analytical long-run risk premia (Section 3.4)")
    print("-" * 50)
    sol = solve_analytical()
    print_value_premium(sol)

    print("\n2. Monte-Carlo cash-flow moments (Tables III–IV targets)")
    print("-" * 50)
    # Fewer sims for a quick demo; increase for better precision
    mom = simulate_cashflow_moments(n_sims=50, years=74, seed=123)
    print_moments(mom)

    print("\nDone. The analytical spread already shows the paper's key result:")
    print("value firms earn a large premium because of higher exposure to")
    print("persistent (long-run) consumption risks under Epstein-Zin preferences.")

if __name__ == "__main__":
    main()
