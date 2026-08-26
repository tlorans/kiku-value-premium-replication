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

        # Residual correlation matrix for the orthogonalised dividend shocks
        # order: growth, value, market
        self.res_corr = np.array([
            [1.0, self.p.residual_corr_gv, self.p.residual_corr_gm],
            [self.p.residual_corr_gv, 1.0, self.p.residual_corr_vm],
            [self.p.residual_corr_gm, self.p.residual_corr_vm, 1.0],
        ])
        self.chol_v = np.linalg.cholesky(self.res_corr)

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
        """
        Full joint simulation of consumption and all portfolio dividend series.

        Returns a dict with keys:
            x, sigma2, dc, dd_growth, dd_value, dd_market
        """
        c = self.p.cons
        x, s2 = self.simulate_states(T, x0, s2_0)

        eta = self.rng.standard_normal(T)
        v = self.rng.standard_normal((T, 3)) @ self.chol_v.T

        alphas = np.array([
            self.p.dividends["growth"].alpha,
            self.p.dividends["value"].alpha,
            self.p.dividends["market"].alpha,
        ])
        scale = np.sqrt(1.0 - alphas**2)
        u = alphas[None, :] * eta[:, None] + scale[None, :] * v

        dc = c.mu + x + np.sqrt(s2) * eta

        dds = {}
        names = ["growth", "value", "market"]
        for i, name in enumerate(names):
            d = self.p.dividends[name]
            dds[name] = d.mu + d.phi * x + d.phi_sigma * np.sqrt(s2) * u[:, i]

        return {
            "x": x,
            "sigma2": s2,
            "dc": dc,
            "dd_growth": dds["growth"],
            "dd_value": dds["value"],
            "dd_market": dds["market"],
        }
