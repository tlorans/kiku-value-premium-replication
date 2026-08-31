"""
Step 1 & 2 of Kiku’s recipe – State and cash-flow dynamics
==========================================================

Simulates the joint process for:
- the persistent expected-growth factor x_t and stochastic volatility (Step 1)
- consumption growth and the portfolio-specific dividend growth series (Step 2)

The differential loading of each portfolio on x_t (the long-run leverage φ)
is the economic source of the value premium.
"""
from __future__ import annotations
import numpy as np
from .params import ModelParams, get_default_params


class Dynamics:
    """Simulator of the joint long-run risks processes."""

    def __init__(self, params: ModelParams | None = None, seed: int | None = None):
        self.p = params or get_default_params()
        self.rng = np.random.default_rng(seed)

        self.names = list(self.p.claims)
        n = len(self.names)
        paper = ["growth", "value", "market"]
        if self.names == paper:
            self.res_corr = np.array([
                [1.0, self.p.residual_corr_gv, self.p.residual_corr_gm],
                [self.p.residual_corr_gv, 1.0, self.p.residual_corr_vm],
                [self.p.residual_corr_gm, self.p.residual_corr_vm, 1.0],
            ])
        else:
            self.res_corr = np.eye(max(n, 1))
        if n:
            self.chol_v = np.linalg.cholesky(self.res_corr)
        else:
            self.chol_v = np.array([[1.0]])

    def simulate_states(self, T: int, x0: float = 0.0, s2_0: float | None = None):
        """Simulate the long-run risk factor x_t and variance σ²_t for T periods."""
        c = self.p.cons
        if s2_0 is None:
            s2_0 = c.sigma ** 2
        x = np.empty(T)
        s2 = np.empty(T)
        x[0] = x0
        s2[0] = max(s2_0, 1e-12)

        for t in range(T - 1):
            eps = self.rng.standard_normal()
            w = self.rng.standard_normal()
            x[t + 1] = c.rho * x[t] + c.phi_x * np.sqrt(s2[t]) * eps
            s2[t + 1] = c.sigma**2 * (1 - c.nu) + c.nu * s2[t] + c.sigma_w * w
            s2[t + 1] = max(s2[t + 1], 1e-12)
        return x, s2

    def simulate_cashflows(self, T: int, x0: float = 0.0, s2_0: float | None = None):
        """Full joint simulation of consumption and all portfolio dividend series."""
        c = self.p.cons
        x, s2 = self.simulate_states(T, x0, s2_0)

        names = self.names
        n = len(names)
        eta = self.rng.standard_normal(T)
        if n:
            v = self.rng.standard_normal((T, n)) @ self.chol_v.T
            alphas = np.array([self.p.claims[name].alpha for name in names])
            scale = np.sqrt(np.maximum(1.0 - alphas**2, 0.0))
            u = alphas[None, :] * eta[:, None] + scale[None, :] * v
        else:
            u = np.zeros((T, 0))

        dc = c.mu + x + np.sqrt(s2) * eta

        out = {"x": x, "sigma2": s2, "dc": dc}
        for i, name in enumerate(names):
            d = self.p.claims[name]
            out[f"dd_{name}"] = d.mu + d.phi * x + d.phi_sigma * np.sqrt(s2) * u[:, i]
        return out
