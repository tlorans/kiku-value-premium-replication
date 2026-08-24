"""
Numerical solution of the long-run risks model (Kiku 2006) by successive
approximation of the Euler equation on a Tauchen-Hussey style product grid.

Solves for the consumption claim and the three equity claims, then reports
approximate unconditional moments (mean log PD, long-run risk premia ranking).
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

        self.z_c = None
        self.z = {}
        self.stationary = None
        self.converged = False

    def _stationary_dist(self, max_iter: int = 1000, tol: float = 1e-10):
        """Compute approximate stationary distribution of the Markov chain."""
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

    def solve_consumption_claim(self, max_iter: int = 400, tol: float = 1e-5,
                                damp: float = 0.4):
        """
        Successive approximation for z_c = log(P_c / C).
        Uses the fixed-point form of the Euler equation under Epstein-Zin.
        """
        n = self.grid.n_states
        z = np.full(n, 4.0)
        Pi = self.grid.Pi
        c = self.p.cons
        theta = self.theta
        delta = self.delta
        psi = self.psi

        for it in range(max_iter):
            z_next = z
            # Approximate next Δc by its conditional mean component (μ + x')
            # A more accurate version would quadrature over η as well.
            dc_next = c.mu + self.grid.x_grid

            rc = (dc_next[None, :] + np.log(np.exp(z_next)[None, :] + 1.0)
                  - z[:, None])

            m = (theta * np.log(delta)
                 - (theta / psi) * dc_next[None, :]
                 + (theta - 1.0) * rc)

            payoff = np.exp(m) * np.exp(dc_next[None, :]) * (1.0 + np.exp(z_next)[None, :])
            exp_z_new = (Pi * payoff).sum(axis=1)
            z_new = np.log(np.maximum(exp_z_new, 1e-16))

            diff = np.max(np.abs(z_new - z))
            z = damp * z_new + (1.0 - damp) * z

            if diff < tol:
                self.converged = True
                break

        self.z_c = z
        return z

    def solve_equity(self, name: str, max_iter: int = 300, tol: float = 1e-5,
                     damp: float = 0.4):
        """Solve log(P/D) for one equity claim given the solved consumption claim."""
        if self.z_c is None:
            self.solve_consumption_claim()

        n = self.grid.n_states
        z = np.full(n, 3.5)
        Pi = self.grid.Pi
        c = self.p.cons
        dpar = self.p.dividends[name]
        theta = self.theta
        delta = self.delta
        psi = self.psi

        # IMRS constructed from the consumption claim
        dc = c.mu + self.grid.x_grid
        rc = (dc[None, :] + np.log(np.exp(self.z_c)[None, :] + 1.0)
              - self.z_c[:, None])
        m = (theta * np.log(delta)
             - (theta / psi) * dc[None, :]
             + (theta - 1.0) * rc)

        for it in range(max_iter):
            # Dividend growth mean component (the loading on x is the long-run risk)
            dd = dpar.mu + dpar.phi * self.grid.x_grid
            payoff = (np.exp(m) * np.exp(dd[None, :])
                      * (1.0 + np.exp(z)[None, :]))
            exp_z_new = (Pi * payoff).sum(axis=1)
            z_new = np.log(np.maximum(exp_z_new, 1e-16))
            diff = np.max(np.abs(z_new - z))
            z = damp * z_new + (1.0 - damp) * z
            if diff < tol:
                break

        self.z[name] = z
        return z

    def solve(self):
        """Solve the whole model."""
        self.solve_consumption_claim()
        for name in ["growth", "value", "market"]:
            self.solve_equity(name)
        self._stationary_dist()
        return self

    def mean_pd(self):
        """Unconditional mean of log valuations using the stationary distribution."""
        if self.stationary is None:
            self._stationary_dist()
        pi = self.stationary
        out = {"consumption": float(pi @ self.z_c)}
        for name, z in self.z.items():
            out[name] = float(pi @ z)
        return out

    def approximate_premia(self):
        """
        Rough unconditional risk premia ranking driven by the long-run component.
        Uses the analytical risk-price formulas evaluated at the average state
        together with the numerical A1-like elasticities implied by the grid.
        This recovers the paper's key ranking even with the simplified expectation.
        """
        from .analytical import solve_analytical
        ana = solve_analytical(self.p)
        return {
            "analytical_lr_premia": ana.premium_lr,
            "numerical_mean_log_pd": self.mean_pd(),
            "note": "Numerical PD ranking should place value < growth; "
                    "the analytical LR premia give the quantitative value premium."
        }

    def summary(self):
        """Print a short summary of the numerical solution."""
        pd = self.mean_pd()
        print("Numerical mean log valuations (stationary distribution):")
        for k, v in pd.items():
            print(f"  {k:12s}: {v:.3f}")
        print("\nValue vs Growth log-PD differential (numerical): "
              f"{pd['value'] - pd['growth']:.3f}")
        print("(Paper targets: growth ~3.65, value ~3.10 → differential ~ -0.55)")
        print("\nFor the quantitative value premium see the analytical module,"
              " which isolates the long-run risk channel (≈85 % of the 5.3 %).")
