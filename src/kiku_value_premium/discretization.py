"""
Tauchen-Hussey style discretization of the joint (x, σ²) state space
following the Appendix of Kiku (2006).

- σ² : 4-point approximation of the highly persistent AR(1) variance process
- x  : Gauss-Hermite nodes (default 15 for speed; paper uses 30)
- Product grid + transition matrix that respects the state-dependent volatility of x
"""
from __future__ import annotations
import numpy as np
from scipy.special import roots_hermitenorm
from .params import ModelParams, get_default_params


class StateGrid:
    """Product grid over expected growth x and variance σ²."""

    def __init__(self, params: ModelParams | None = None,
                 n_x: int = 15, n_s: int = 4):
        self.p = params or get_default_params()
        self.n_x = n_x
        self.n_s = n_s
        self.n_states = n_x * n_s

        c = self.p.cons

        # --- Variance grid (simple equally-spaced + Rouwenhorst-like transitions) ---
        # Unconditional mean and std of σ²
        mean_s2 = c.sigma ** 2
        # Var(σ²) = σ_w² / (1 - ν²)
        std_s2 = c.sigma_w / np.sqrt(1 - c.nu ** 2)
        # 4 points covering ~ ±2 std, clipped to positive
        self.s2_nodes = np.linspace(max(1e-8, mean_s2 - 1.5 * std_s2),
                                    mean_s2 + 1.5 * std_s2, n_s)
        self.s2_nodes = np.maximum(self.s2_nodes, 1e-8)

        # Transition for σ² (Tauchen style)
        self.Pi_s = self._tauchen_ar1(self.s2_nodes, c.nu,
                                      c.sigma**2 * (1 - c.nu), c.sigma_w)

        # --- x grid: Gauss-Hermite nodes scaled to the unconditional distribution ---
        # Unconditional std of x ≈ (φx * σ) / sqrt(1-ρ²)
        std_x = (c.phi_x * c.sigma) / np.sqrt(1 - c.rho ** 2)
        # roots_hermitenorm returns nodes/weights for N(0,1)
        nodes, weights = roots_hermitenorm(n_x)
        self.x_nodes = nodes * std_x * np.sqrt(2)   # scale (GH is for exp(-x²), adjust)
        # Better standard scaling for standard normal GH:
        # scipy.special.roots_hermitenorm already gives nodes for weight exp(-x²/2)/sqrt(2π)
        self.x_nodes = nodes * std_x
        self.x_weights = weights / np.sqrt(2 * np.pi)  # approximate density weights

        # Product grid: state index k = i_x * n_s + i_s
        self.x_grid = np.repeat(self.x_nodes, n_s)
        self.s2_grid = np.tile(self.s2_nodes, n_x)

        # Full transition matrix (n_states, n_states)
        self.Pi = self._build_transition()

    def _tauchen_ar1(self, nodes, rho, mu_innov, sigma_innov):
        """Simple Tauchen transition matrix for an AR(1)."""
        n = len(nodes)
        Pi = np.zeros((n, n))
        step = nodes[1] - nodes[0] if n > 1 else 1.0
        for i in range(n):
            loc = rho * nodes[i] + mu_innov
            for j in range(n):
                if j == 0:
                    Pi[i, j] = _norm_cdf((nodes[j] + step / 2 - loc) / sigma_innov)
                elif j == n - 1:
                    Pi[i, j] = 1.0 - _norm_cdf((nodes[j] - step / 2 - loc) / sigma_innov)
                else:
                    Pi[i, j] = (_norm_cdf((nodes[j] + step / 2 - loc) / sigma_innov)
                                - _norm_cdf((nodes[j] - step / 2 - loc) / sigma_innov))
            # renormalize
            Pi[i, :] /= Pi[i, :].sum()
        return Pi

    def _build_transition(self):
        """Product transition: independent σ² transition + conditional x transition."""
        n = self.n_states
        Pi = np.zeros((n, n))
        c = self.p.cons

        for i in range(n):
            ix = i // self.n_s
            is_ = i % self.n_s
            x = self.x_grid[i]
            s2 = self.s2_grid[i]
            sig = np.sqrt(s2)

            # next σ² probabilities
            p_s = self.Pi_s[is_, :]

            # conditional x' ~ N(ρ x, (φx σ)^2)
            loc = c.rho * x
            scale = c.phi_x * sig + 1e-12

            for j in range(n):
                jx = j // self.n_s
                js = j % self.n_s
                x_next = self.x_nodes[jx]
                # density of normal at the node, times weight / spacing approximation
                # simple: use normal pdf * average spacing
                dens = _norm_pdf((x_next - loc) / scale) / scale
                # combine with σ transition
                Pi[i, j] = p_s[js] * dens * (self.x_nodes[1] - self.x_nodes[0] if self.n_x > 1 else 1.0)

            # renormalize row
            row_sum = Pi[i, :].sum()
            if row_sum > 0:
                Pi[i, :] /= row_sum
            else:
                Pi[i, i] = 1.0
        return Pi


def _norm_pdf(z):
    return np.exp(-0.5 * z**2) / np.sqrt(2 * np.pi)


def _norm_cdf(z):
    from scipy.stats import norm
    return norm.cdf(z)
