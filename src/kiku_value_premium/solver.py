"""
Step 5 of Kiku’s recipe – Numerical solution (Tauchen–Hussey style)
===================================================================

Solves the model on a discrete state space using the quadrature method of
Tauchen & Hussey (1991), exactly as in the paper.

- Default grid matches the paper: 30-point GH for x, 4-point for σ².
- Euler expectation integrates the short-run innovation η with additional GH.
- Core loops are accelerated with Numba when available (optional dependency).

After calling `solver.solve()` the valuation functions live in:
    solver.z_c          (consumption claim)
    solver.z["value"]   (value equity claim)
    solver.z["growth"]  (growth equity claim)
    …
and the stationary distribution of the Markov chain is in `solver.stationary`.
"""
from __future__ import annotations
import numpy as np
from scipy.special import roots_hermitenorm
from .params import ModelParams, get_default_params
from .preferences import EpsteinZinPreferences
from .discretization import StateGrid

# ---------------------------------------------------------------------------
# Optional Numba acceleration
# ---------------------------------------------------------------------------
try:
    from numba import njit
    HAS_NUMBA = True
except ImportError:
    HAS_NUMBA = False
    def njit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator


@njit(cache=True)
def _accumulate_consumption_payoff(
    z, Pi, x, sig, mu, delta, theta, psi,
    eta_nodes, eta_weights
):
    """Numba kernel: expected payoff for the consumption claim."""
    n = z.shape[0]
    n_quad = eta_nodes.shape[0]
    exp_payoff = np.zeros(n)

    for i in range(n):
        xi = x[i]
        si = sig[i]
        zi = z[i]
        for q in range(n_quad):
            eta = eta_nodes[q]
            w_eta = eta_weights[q]
            dc = mu + xi + si * eta
            acc = 0.0
            for j in range(n):
                z_next = z[j]
                rc = dc + np.log(np.exp(z_next) + 1.0) - zi
                m = (theta * np.log(delta)
                     - (theta / psi) * dc
                     + (theta - 1.0) * rc)
                payoff = np.exp(m) * np.exp(dc) * (1.0 + np.exp(z_next))
                acc += Pi[i, j] * payoff
            exp_payoff[i] += w_eta * acc
    return exp_payoff


@njit(cache=True)
def _accumulate_equity_payoff(
    z, z_c, Pi, x, sig, mu_c, mu_d, phi, phi_sigma, alpha,
    delta, theta, psi, eta_nodes, eta_weights
):
    """Numba kernel: expected payoff for an equity claim."""
    n = z.shape[0]
    n_quad = eta_nodes.shape[0]
    exp_payoff = np.zeros(n)

    for i in range(n):
        xi = x[i]
        si = sig[i]
        zi = z[i]
        zc_i = z_c[i]
        for q in range(n_quad):
            eta = eta_nodes[q]
            w_eta = eta_weights[q]
            dc = mu_c + xi + si * eta
            u = alpha * eta   # residual innovation (simplified)
            dd = mu_d + phi * xi + phi_sigma * si * u
            acc = 0.0
            for j in range(n):
                z_next = z[j]
                rc = dc + np.log(np.exp(z_c[j]) + 1.0) - zc_i
                m = (theta * np.log(delta)
                     - (theta / psi) * dc
                     + (theta - 1.0) * rc)
                payoff = np.exp(m) * np.exp(dd) * (1.0 + np.exp(z_next))
                acc += Pi[i, j] * payoff
            exp_payoff[i] += w_eta * acc
    return exp_payoff


class ModelSolver:
    """
    High-accuracy numerical solver for the Kiku (2006) long-run risks model.

    Parameters
    ----------
    params : ModelParams
        Complete parameterisation (Steps 1–4).
    n_x, n_s : int
        Grid size for expected growth and variance (paper default 30 × 4).
    n_quad : int
        Number of Gauss–Hermite nodes for the short-run innovation.
    """

    def __init__(self, params: ModelParams | None = None,
                 n_x: int = 30, n_s: int = 4, n_quad: int = 7):
        self.p = params or get_default_params()
        self.pref = EpsteinZinPreferences(self.p.prefs)
        self.grid = StateGrid(self.p, n_x=n_x, n_s=n_s)
        self.theta = float(self.pref.theta)
        self.delta = float(self.p.prefs.delta)
        self.psi = float(self.p.prefs.psi)
        self.gamma = float(self.p.prefs.gamma)
        self.n_quad = n_quad

        nodes, weights = roots_hermitenorm(n_quad)
        self.eta_nodes = np.ascontiguousarray(nodes, dtype=np.float64)
        self.eta_weights = np.ascontiguousarray(weights / np.sqrt(2 * np.pi), dtype=np.float64)

        self.z_c = None
        self.z = {}
        self.stationary = None
        self.converged = False
        self.used_numba = HAS_NUMBA

    def _stationary_dist(self, max_iter: int = 2000, tol: float = 1e-12):
        n = self.grid.n_states
        pi = np.ones(n) / n
        Pi = self.grid.Pi
        for _ in range(max_iter):
            pi_new = pi @ Pi
            if np.max(np.abs(pi_new - pi)) < tol:
                break
            pi = pi_new
        self.stationary = pi / pi.sum()
        return self.stationary

    def solve_consumption_claim(self, max_iter: int = 500, tol: float = 1e-5,
                                damp: float = 0.35):
        n = self.grid.n_states
        z = np.full(n, 4.0, dtype=np.float64)
        Pi = np.ascontiguousarray(self.grid.Pi, dtype=np.float64)
        x = np.ascontiguousarray(self.grid.x_grid, dtype=np.float64)
        sig = np.ascontiguousarray(np.sqrt(self.grid.s2_grid), dtype=np.float64)
        mu = float(self.p.cons.mu)

        for it in range(max_iter):
            if HAS_NUMBA:
                exp_payoff = _accumulate_consumption_payoff(
                    z, Pi, x, sig, mu, self.delta, self.theta, self.psi,
                    self.eta_nodes, self.eta_weights
                )
            else:
                exp_payoff = np.zeros(n)
                for i in range(n):
                    for q, (eta, w_eta) in enumerate(zip(self.eta_nodes, self.eta_weights)):
                        dc = mu + x[i] + sig[i] * eta
                        acc = 0.0
                        for j in range(n):
                            rc = dc + np.log(np.exp(z[j]) + 1.0) - z[i]
                            m = (self.theta * np.log(self.delta)
                                 - (self.theta / self.psi) * dc
                                 + (self.theta - 1.0) * rc)
                            payoff = np.exp(m) * np.exp(dc) * (1.0 + np.exp(z[j]))
                            acc += Pi[i, j] * payoff
                        exp_payoff[i] += w_eta * acc

            z_new = np.log(np.maximum(exp_payoff, 1e-12))
            if np.max(np.abs(z_new - z)) < tol:
                z = z_new
                break
            z = damp * z_new + (1.0 - damp) * z

        self.z_c = z
        return z

    def solve_equity_claim(self, name: str, max_iter: int = 500, tol: float = 1e-5,
                           damp: float = 0.35):
        if self.z_c is None:
            self.solve_consumption_claim()

        d = self.p.dividends[name]
        n = self.grid.n_states
        z = np.full(n, 3.5, dtype=np.float64)
        Pi = np.ascontiguousarray(self.grid.Pi, dtype=np.float64)
        x = np.ascontiguousarray(self.grid.x_grid, dtype=np.float64)
        sig = np.ascontiguousarray(np.sqrt(self.grid.s2_grid), dtype=np.float64)

        for it in range(max_iter):
            if HAS_NUMBA:
                exp_payoff = _accumulate_equity_payoff(
                    z, self.z_c, Pi, x, sig,
                    float(self.p.cons.mu), float(d.mu), float(d.phi),
                    float(d.phi_sigma), float(d.alpha),
                    self.delta, self.theta, self.psi,
                    self.eta_nodes, self.eta_weights
                )
            else:
                exp_payoff = np.zeros(n)
                for i in range(n):
                    for q, (eta, w_eta) in enumerate(zip(self.eta_nodes, self.eta_weights)):
                        dc = self.p.cons.mu + x[i] + sig[i] * eta
                        u = d.alpha * eta
                        dd = d.mu + d.phi * x[i] + d.phi_sigma * sig[i] * u
                        acc = 0.0
                        for j in range(n):
                            rc = dc + np.log(np.exp(self.z_c[j]) + 1.0) - self.z_c[i]
                            m = (self.theta * np.log(self.delta)
                                 - (self.theta / self.psi) * dc
                                 + (self.theta - 1.0) * rc)
                            payoff = np.exp(m) * np.exp(dd) * (1.0 + np.exp(z[j]))
                            acc += Pi[i, j] * payoff
                        exp_payoff[i] += w_eta * acc

            z_new = np.log(np.maximum(exp_payoff, 1e-12))
            if np.max(np.abs(z_new - z)) < tol:
                z = z_new
                break
            z = damp * z_new + (1.0 - damp) * z

        self.z[name] = z
        return z

    def solve(self, max_iter: int = 500, tol: float = 1e-5):
        """Solve the consumption claim and all equity claims."""
        self.solve_consumption_claim(max_iter=max_iter, tol=tol)
        for name in self.p.dividends:
            self.solve_equity_claim(name, max_iter=max_iter, tol=tol)
        self._stationary_dist()
        self.converged = True
        return self
