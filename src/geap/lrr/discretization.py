"""
Tauchen-Hussey style discretization of the joint (x, σ²) state space
following the Appendix of Kiku (2006).

- σ² : 4-point approximation of the highly persistent AR(1) variance process
- x  : Gauss-Hermite nodes (default 15 for speed; paper uses 30)
- Product grid + transition matrix that respects the state-dependent volatility of x

The x transition uses genuine Tauchen–Hussey weights,

    π(x_j | x_i) ∝ w_j · f(x_j | x_i) / ω(x_j),      Σ_j π(x_j | x_i) = 1,

where f is the conditional AR(1) density, ω is the weighting density whose
Gauss–Hermite rule supplies the nodes x_j and weights w_j, and each row is
renormalised by s(x_i) = Σ_j π(x_j | x_i) as in Tauchen & Hussey (1991),
eq. (24) of the paper's appendix.

ω is scaled to the *unconditional* distribution of x (Flodén's 2008
variant), not to the one-step conditional density f(y | ȳ) of the
original Tauchen–Hussey recipe. With ρ = 0.98 the conditional scaling
truncates the 30-node grid at ±1.9 unconditional standard deviations,
which cuts the solved price elasticity to long-run news and collapses
the value premium to below 2% — it cannot reproduce Table VII. The
unconditional scaling covers the ergodic range and reproduces the
paper's premium.
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

        # --- Variance grid (equally-spaced Tauchen chain, positive nodes) ---
        # Unconditional mean and std of σ²
        mean_s2 = c.sigma ** 2
        # Var(σ²) = σ_w² / (1 - ν²)
        std_s2 = c.sigma_w / np.sqrt(1 - c.nu ** 2)
        # points covering ~ ±1.5 std, clipped to positive
        self.s2_nodes = np.linspace(max(1e-8, mean_s2 - 1.5 * std_s2),
                                    mean_s2 + 1.5 * std_s2, n_s)
        self.s2_nodes = np.maximum(self.s2_nodes, 1e-8)

        # Transition for σ² (Tauchen style)
        self.Pi_s = self._tauchen_ar1(self.s2_nodes, c.nu,
                                      c.sigma**2 * (1 - c.nu), c.sigma_w)

        # --- x grid: Gauss-Hermite nodes for ω = N(0, Var(x)) ---
        # unconditional std of x = (φx σ̄) / sqrt(1 - ρ²); see module docstring
        # for why ω is scaled unconditionally rather than to f(y | ȳ).
        s_omega = (c.phi_x * c.sigma) / np.sqrt(1 - c.rho ** 2)
        # roots_hermitenorm returns nodes/weights for the weight exp(-t²/2);
        # weights sum to sqrt(2π), i.e. w/sqrt(2π) integrates against N(0,1).
        nodes, weights = roots_hermitenorm(n_x)
        self.x_nodes = nodes * s_omega
        # Quadrature weights for ∫ p(x) dx ≈ Σ_j quad_w_j · p(x_j):
        # quad_w_j = (w_j / sqrt(2π)) / ω(x_j) with ω = N(0, s_omega²).
        self.x_quad_weights = (weights / np.sqrt(2 * np.pi)
                               / _norm_pdf(nodes) * s_omega)
        # Density weights of ω at the nodes (kept for stationary diagnostics).
        self.x_weights = weights / np.sqrt(2 * np.pi)

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
        """Product transition: independent σ² transition × conditional x transition.

        The x innovation volatility is state-dependent (φx·σ_t), so the x
        transition is built per current-σ² state with Tauchen–Hussey
        weights and row renormalisation.
        """
        c = self.p.cons
        n = self.n_states
        Pi = np.zeros((n, n))

        # Conditional x transitions, one matrix per current σ² state.
        Pi_x = np.zeros((self.n_s, self.n_x, self.n_x))
        for is_ in range(self.n_s):
            scale = c.phi_x * np.sqrt(self.s2_nodes[is_])
            for ix in range(self.n_x):
                loc = c.rho * self.x_nodes[ix]
                dens = _norm_pdf((self.x_nodes - loc) / scale) / scale
                row = self.x_quad_weights * dens
                s_i = row.sum()
                if s_i > 0:
                    Pi_x[is_, ix, :] = row / s_i
                else:  # pragma: no cover - degenerate scale
                    Pi_x[is_, ix, ix] = 1.0

        for i in range(n):
            ix = i // self.n_s
            is_ = i % self.n_s
            # next-state probability factorises: x′ ⫫ σ²′ given (x, σ²)
            block = np.outer(Pi_x[is_, ix, :], self.Pi_s[is_, :])
            Pi[i, :] = block.reshape(-1)
        return Pi


def _norm_pdf(z):
    return np.exp(-0.5 * z**2) / np.sqrt(2 * np.pi)


def _norm_cdf(z):
    from scipy.stats import norm
    return norm.cdf(z)
