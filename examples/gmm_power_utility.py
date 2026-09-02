"""Power-utility SDF GMM on a three-moment toy sample.

Two excess-return Euler equations and one risk-free level condition
identify (delta, gamma). The series are constructed so the true kernel
prices them, and two-step GMM recovers those parameters.

This is not the cash-flow calibration in geap.lrr.calibration. Returns
enter here because the moments are Euler equations.

Run: uv run python examples/gmm_power_utility.py
"""
from __future__ import annotations

import numpy as np

import geap


def main():
    rng = np.random.default_rng(3)
    nobs = 3000
    delta, gamma = 0.99, 4.0
    growth = np.exp(0.018 + 0.02 * rng.standard_normal(nobs))
    m = geap.gmm.power_utility_sdf(delta, gamma, growth)
    rf = 1.0 / float(np.mean(m))
    excess = np.column_stack(
        [
            0.4 * (1.0 / m - rf),
            1.1 * (1.0 / m - rf),
        ]
    )

    def moments(theta):
        sdf = geap.gmm.power_utility_sdf(theta[0], theta[1], growth)
        pricing = geap.gmm.sdf_moments(sdf, excess)
        level = sdf * rf - 1.0
        return np.column_stack([pricing, level])

    fit = geap.gmm.estimate(
        moments,
        [0.95, 2.5],
        W="identity",
        steps=2,
        bounds=((1e-6, 1.0), (0.1, 20.0)),
        names=("delta", "gamma"),
    )
    print(f"True delta = {delta}, true gamma = {gamma}")
    print(fit.summary())


if __name__ == "__main__":
    main()
