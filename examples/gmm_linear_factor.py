"""Linear-factor GMM: prices of risk from average excess returns on betas.

Just-identified, one moment matches one lambda exactly. Two assets and
one factor cannot both be zeroed; identity-weighted GMM is OLS of the
means on the betas. Changing the second mean so the points lie on a
line makes both pricing errors zero.

Run: uv run python examples/gmm_linear_factor.py
"""
from __future__ import annotations

import numpy as np

import geap


def main():
    print("Just-identified: E[R^e] = lambda")
    one = geap.gmm.linear_factor(np.array([0.08]), np.array([1.0]))
    print(one.summary())

    print()
    print("Over-identified: two assets, one factor, identity weights")
    mean_ret = np.array([0.08, 0.15])
    beta = np.array([1.0, 1.5])
    over = geap.gmm.linear_factor(mean_ret, beta, W="identity")
    print(over.summary())

    print()
    print("Same betas, second mean moved onto the line at 0.12")
    exact = geap.gmm.linear_factor(np.array([0.08, 0.12]), beta)
    print(exact.summary())


if __name__ == "__main__":
    main()
