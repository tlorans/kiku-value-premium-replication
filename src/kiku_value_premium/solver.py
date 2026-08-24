"""
Numerical solution of the long-run risks model by successive approximation
of the Euler equation on the discretized state grid (Kiku 2006).

Solves first for the consumption claim (wealth portfolio), then for each
equity claim. Returns the log price-dividend (price-consumption) ratios on
the grid together with the implied risk-free rate and risk prices.
"""
from __future__ import annotations
import numpy as np
from .params import ModelParams, get_default_params
from .preferences import EpsteinZinPreferences
from .discretization import StateGrid


class ModelSolver:
    def __init__(self, params: ModelParams | None = None,
                 n_x: int = 15, n_s: int = 4):
        self.p = params or get_default_params()
        self.pref = EpsteinZinPreferences(self.p.prefs)
        self.grid = StateGrid(self.p, n_x=n_x, n_s=n_s)
        self.theta = self.pref.theta
        self.delta = self.p.prefs.delta
        self.psi = self.p.prefs.psi
        self.gamma = self.p.prefs.gamma

        # Will be filled by solve()
        self.z_c = None          # log P/C on grid
        self.z = {}              # log P/D for each asset
        self.rf = None           # risk-free rate on grid
        self.converged = False

    def _dc_on_grid(self):
        """Possible next Δc for every (current, next) pair (vectorized later)."""
        c = self.p.cons
        # For simplicity we evaluate expectations by summing over next states
        # Δc = μ + x'  (the innovation is already absorbed in the transition)
        # More precisely the innovation is part of the density, so mean Δc from current is μ + x_current
        # but for the next period value we use the next x.
        return c.mu + self.grid.x_grid   # used as the expected component

    def solve_consumption_claim(self, max_iter: int = 300, tol: float = 1e-6,
                                damp: float = 0.5):
        """
        Successive approximation for z_c = log(P_c / C).

        The fixed-point relation (ignoring the innovation part for the MVP;
        a more accurate version would integrate the innovation explicitly):

        exp(z_new) = E[ M * exp(Δc) * (1 + exp(z')) ]
        where M depends on the wealth return which depends on z.
        """
        n = self.grid.n_states
        z = np.full(n, 3.5)          # initial guess
        Pi = self.grid.Pi
        c = self.p.cons
        theta = self.theta
        delta = self.delta
        psi = self.psi

        for it in range(max_iter):
            # Next period values
            z_next = z                               # on the grid
            # Approximate next Δc (mean part); the vol part is in the transition density
            dc_next = c.mu + self.grid.x_grid

            # Wealth return: R_c = exp(Δc) * (exp(z') + 1) / exp(z)
            # We compute the expectation of the SDF-weighted payoff
            # For successive approx we form the implied PD from the Euler
            # Simplified iteration that works reasonably for these models:
            # First form an approximate m using current z

            # Approximate rc for each current → next
            # rc[i,j] = dc[j] + log(exp(z[j]) + 1) - z[i]
            rc = (dc_next[None, :] + np.log(np.exp(z_next)[None, :] + 1.0)
                  - z[:, None])

            # Log IMRS
            m = (theta * np.log(delta)
                 - (theta / psi) * dc_next[None, :]
                 + (theta - 1.0) * rc)

            # Euler: E[exp(m + rc)] = 1  ⇒  the implied current PD satisfies
            # exp(z) = E[ exp(m) * exp(dc) * (1 + exp(z')) ]
            payoff = np.exp(m) * np.exp(dc_next[None, :]) * (1.0 + np.exp(z_next)[None, :])
            # Average over next states with transition probs
            exp_z_new = (Pi * payoff).sum(axis=1)
            z_new = np.log(np.maximum(exp_z_new, 1e-12))

            # Damping for stability
            z = damp * z_new + (1 - damp) * z

            if np.max(np.abs(z_new - z)) < tol:
                self.converged = True
                break

        self.z_c = z
        return z

    def solve_equity(self, name: str, max_iter: int = 200, tol: float = 1e-6,
                     damp: float = 0.5):
        """Solve for log(P/D) of a given dividend claim, given the already solved z_c."""
        if self.z_c is None:
            self.solve_consumption_claim()

        n = self.grid.n_states
        z = np.full(n, 3.3)
        Pi = self.grid.Pi
        c = self.p.cons
        dpar = self.p.dividends[name]
        theta = self.theta
        delta = self.delta
        psi = self.psi

        # Pre-compute the IMRS using the consumption claim (approximate)
        dc = c.mu + self.grid.x_grid
        rc = (dc[None, :] + np.log(np.exp(self.z_c)[None, :] + 1.0)
              - self.z_c[:, None])
        m = (theta * np.log(delta)
             - (theta / psi) * dc[None, :]
             + (theta - 1.0) * rc)

        for it in range(max_iter):
            dd = dpar.mu + dpar.phi * self.grid.x_grid
            # R = exp(dd) * (exp(z') + 1) / exp(z)
            payoff = (np.exp(m) * np.exp(dd[None, :])
                      * (1.0 + np.exp(z)[None, :]))
            exp_z_new = (Pi * payoff).sum(axis=1)
            z_new = np.log(np.maximum(exp_z_new, 1e-12))
            z = damp * z_new + (1 - damp) * z
            if np.max(np.abs(z_new - z)) < tol:
                break

        self.z[name] = z
        return z

    def solve(self):
        """Solve consumption claim then all equities."""
        self.solve_consumption_claim()
        for name in ["growth", "value", "market"]:
            self.solve_equity(name)
        return self

    def mean_pd(self):
        """Approximate unconditional mean of log PD / log PC (using stationary distribution)."""
        # Simple average for now; a better version uses the stationary dist of Pi
        out = {"consumption": float(np.mean(self.z_c))}
        for name, z in self.z.items():
            out[name] = float(np.mean(z))
        return out
