"""
High-accuracy numerical solution of Kiku (2006) long-run risks model.

- Default grid matches the paper: 30-point GH for x, 4-point for σ².
- Euler expectation integrates the short-run innovation η with additional GH.
- Core loops are accelerated with Numba when available (optional dependency).
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
            # vectorised over next states would be better, but explicit is fine
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
            # correlated residual (main effect); residual orthogonal vol averaged
            u = alpha * eta
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
                # pure-Python fallback (slow)
                exp_payoff = np.zeros(n)
                for i in range(n):
                    for q, (eta, w_eta) in enumerate(zip(self.eta_nodes, self.eta_weights)):
                        dc = mu + x[i] + sig[i] * eta
                        rc = dc + np.log(np.exp(z) + 1.0) - z[i]
                        m = (self.theta * np.log(self.delta)
                             - (self.theta / self.psi) * dc
                             + (self.theta - 1.0) * rc)
                        payoff = np.exp(m) * np.exp(dc) * (1.0 + np.exp(z))
                        exp_payoff[i] += w_eta * np.dot(Pi[i], payoff)

            z_new = np.log(np.maximum(exp_payoff, 1e-18))
            diff = np.max(np.abs(z_new - z))
            z = damp * z_new + (1.0 - damp) * z

            if it % 20 == 0 or diff < tol:
                print(f"  consumption claim iter {it}: max|Δz| = {diff:.2e}")
            if diff < tol:
                self.converged = True
                print(f"  consumption claim converged in {it} iterations"
                      f" (Numba={HAS_NUMBA})")
                break

        self.z_c = z
        return z

    def solve_equity(self, name: str, max_iter: int = 400, tol: float = 1e-5,
                     damp: float = 0.35):
        if self.z_c is None:
            self.solve_consumption_claim()

        n = self.grid.n_states
        z = np.full(n, 3.5, dtype=np.float64)
        Pi = np.ascontiguousarray(self.grid.Pi, dtype=np.float64)
        x = np.ascontiguousarray(self.grid.x_grid, dtype=np.float64)
        sig = np.ascontiguousarray(np.sqrt(self.grid.s2_grid), dtype=np.float64)
        dpar = self.p.dividends[name]
        mu_c = float(self.p.cons.mu)
        mu_d = float(dpar.mu)
        phi = float(dpar.phi)
        phi_sigma = float(getattr(dpar, "phi_sigma", 0.0))
        alpha = float(getattr(dpar, "alpha", 0.0))

        for it in range(max_iter):
            if HAS_NUMBA:
                exp_payoff = _accumulate_equity_payoff(
                    z, self.z_c, Pi, x, sig,
                    mu_c, mu_d, phi, phi_sigma, alpha,
                    self.delta, self.theta, self.psi,
                    self.eta_nodes, self.eta_weights
                )
            else:
                exp_payoff = np.zeros(n)
                for i in range(n):
                    for eta, w_eta in zip(self.eta_nodes, self.eta_weights):
                        dc = mu_c + x[i] + sig[i] * eta
                        u = alpha * eta
                        dd = mu_d + phi * x[i] + phi_sigma * sig[i] * u
                        rc = dc + np.log(np.exp(self.z_c) + 1.0) - self.z_c[i]
                        m = (self.theta * np.log(self.delta)
                             - (self.theta / self.psi) * dc
                             + (self.theta - 1.0) * rc)
                        payoff = np.exp(m) * np.exp(dd) * (1.0 + np.exp(z))
                        exp_payoff[i] += w_eta * np.dot(Pi[i], payoff)

            z_new = np.log(np.maximum(exp_payoff, 1e-18))
            diff = np.max(np.abs(z_new - z))
            z = damp * z_new + (1.0 - damp) * z

            if it % 20 == 0 or diff < tol:
                print(f"  {name} claim iter {it}: max|Δz| = {diff:.2e}")
            if diff < tol:
                print(f"  {name} claim converged in {it} iterations"
                      f" (Numba={HAS_NUMBA})")
                break

        self.z[name] = z
        return z

    def solve(self):
        print(f"Solving at paper resolution (30×4 + short-run GH) "
              f"[Numba acceleration: {HAS_NUMBA}]")
        self.solve_consumption_claim()
        for name in ["growth", "value", "market"]:
            print(f"Solving {name} claim...")
            self.solve_equity(name)
        self._stationary_dist()
        return self

    def mean_pd(self):
        if self.stationary is None:
            self._stationary_dist()
        pi = self.stationary
        out = {"consumption": float(pi @ self.z_c)}
        for name, zval in self.z.items():
            out[name] = float(pi @ zval)
        return out

    def summary(self):
        pd = self.mean_pd()
        print("\n=== Numerical solution summary (stationary distribution) ===")
        print(f"Numba used: {self.used_numba}")
        print("Mean log valuations:")
        for k, v in pd.items():
            print(f"  {k:12s}: {v:.4f}")
        print(f"\nValue – Growth log-PD differential: {pd['value'] - pd['growth']:.4f}")
        print("(Paper Table VII targets ≈ 3.10 – 3.65 = –0.55)")
