"""
Step 5 of Kiku’s recipe – Numerical solution (Tauchen–Hussey style)
===================================================================

Solves the model on a discrete state space using the quadrature method of
Tauchen & Hussey (1991), exactly as in the paper.

- Default grid matches the paper: 30-point GH for x, 4-point for σ².
- The short-run innovation η and the idiosyncratic dividend residual v are
  Gaussian and independent of the (x, σ²) transition, so their expectations
  integrate in closed form; each Euler iteration reduces to one
  matrix–vector product against the Markov transition matrix.
- The consumption-claim Euler equation is iterated in the θ-divided form

      z ← (1/θ) log E[ exp(θ ln δ + θ(1 − 1/ψ)Δc′ + θ log(1 + e^{z′})) ]

  whose modulus is ≈ κ₁ < 1. Iterating the un-divided form multiplies the
  error by |1 − θ| ≈ 28 per step and diverges — that failure mode collapsed
  every claim to a price floor in earlier versions of this module and is
  now detected and raised instead of clamped.

After calling `solver.solve()` the valuation functions live in:
    solver.z_c          (consumption claim)
    solver.z["value"]   (value equity claim)
    solver.z["growth"]  (growth equity claim)
    …
and the stationary distribution of the Markov chain is in `solver.stationary`.

This is the engine behind ``LongRunRisksModel.solve()``, which builds the
solver, runs it, and presents the same objects on a results object.
"""
from __future__ import annotations
import numpy as np
from .params import ModelParams, get_default_params
from .preferences import EpsteinZinPreferences
from .discretization import StateGrid


class SolverDivergenceError(RuntimeError):
    """The Euler fixed-point iteration left the plausible range.

    Raised instead of silently flooring prices: a claim whose log
    price ratio explodes indicates a mis-specified recursion or
    parameterisation, and clamping it would poison every downstream
    moment.
    """


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
        Deprecated and ignored. The Gaussian innovations η and v now
        integrate in closed form, so no quadrature over them is needed.
    """

    def __init__(self, params: ModelParams | None = None,
                 n_x: int = 30, n_s: int = 4, n_quad: int | None = None):
        self.p = params or get_default_params()
        self.pref = EpsteinZinPreferences(self.p.prefs)
        self.grid = StateGrid(self.p, n_x=n_x, n_s=n_s)
        self.theta = float(self.pref.theta)
        self.delta = float(self.p.prefs.delta)
        self.psi = float(self.p.prefs.psi)
        self.gamma = float(self.p.prefs.gamma)

        self.z_c = None
        self.z = {}
        self.stationary = None
        self.converged = False

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------
    @staticmethod
    def _check_finite(z: np.ndarray, what: str, bound: float = 50.0) -> None:
        if not np.all(np.isfinite(z)) or np.max(np.abs(z)) > bound:
            raise SolverDivergenceError(
                f"{what} left the plausible range (max |z| = "
                f"{np.max(np.abs(z)):.2f}); the Euler iteration is diverging."
            )

    def _sdf_pieces(self):
        """State-wise constants of the log SDF and the z_c-dependent factor.

        m′ = θ ln δ + b·Δc′ + (θ − 1)(log(1 + e^{z_c′}) − z_c),
        with b = θ − 1 − θ/ψ. Returns (const_i, q_j, shift) such that
        E_i[e^{m′} · f(j)] = exp(const_i + shift) · Σ_j Π_ij q_j f(j)
        for any f of the next state only (η already integrated out of the
        Δc′ term via its Gaussian moment-generating function).
        """
        if self.z_c is None:
            raise RuntimeError("Solve the consumption claim first.")
        b = self.theta - 1.0 - self.theta / self.psi
        x = self.grid.x_grid
        s2 = self.grid.s2_grid
        mu_c = float(self.p.cons.mu)

        g_c = np.logaddexp(0.0, self.z_c)          # log(1 + e^{z_c})
        h = (self.theta - 1.0) * g_c
        shift = float(h.max())
        q = np.exp(h - shift)

        const = (self.theta * np.log(self.delta)
                 + b * (mu_c + x)
                 + 0.5 * b * b * s2
                 - (self.theta - 1.0) * self.z_c)
        return const, q, shift

    # ------------------------------------------------------------------
    # Claims
    # ------------------------------------------------------------------
    def solve_consumption_claim(self, max_iter: int = 200_000,
                                tol: float = 1e-10):
        """Fixed point of the θ-divided consumption-claim Euler equation.

        The map contracts at rate ≈ κ₁ = e^{z̄}/(1 + e^{z̄}) ≈ 0.999, so
        thousands of cheap O(n²) iterations are expected and fast.
        """
        n = self.grid.n_states
        Pi = self.grid.Pi
        x = self.grid.x_grid
        s2 = self.grid.s2_grid
        a = self.theta * (1.0 - 1.0 / self.psi)
        mu = float(self.p.cons.mu)
        const = (self.theta * np.log(self.delta)
                 + a * (mu + x)
                 + 0.5 * a * a * s2)

        z = np.full(n, 6.0, dtype=np.float64)
        for _ in range(max_iter):
            h = self.theta * np.logaddexp(0.0, z)
            shift = float(h.max())
            s = Pi @ np.exp(h - shift)
            z_new = (const + np.log(s) + shift) / self.theta
            self._check_finite(z_new, "consumption-claim z")
            if np.max(np.abs(z_new - z)) < tol:
                z = z_new
                break
            z = z_new
        else:
            raise SolverDivergenceError(
                "Consumption claim did not converge within "
                f"{max_iter} iterations (last sup-norm step "
                f"{np.max(np.abs(z_new - z)):.2e})."
            )

        self.z_c = z
        return z

    def solve_equity_claim(self, name: str, max_iter: int = 50_000,
                           tol: float = 1e-10):
        """Fixed point of the Euler equation for one dividend claim.

        The dividend residual u′ = α η′ + √(1 − α²) v′ is integrated in
        closed form: η′ jointly with the SDF (their loadings add), v′ as
        an independent Jensen term ½ φ_σ²(1 − α²)σ².
        """
        if self.z_c is None:
            self.solve_consumption_claim()

        d = self.p.claims[name]
        n = self.grid.n_states
        Pi = self.grid.Pi
        x = self.grid.x_grid
        s2 = self.grid.s2_grid

        b = self.theta - 1.0 - self.theta / self.psi
        sdf_const, q_c, shift_c = self._sdf_pieces()
        c_eta = b + float(d.phi_sigma) * float(d.alpha)   # loading on σ·η
        const = (sdf_const
                 - 0.5 * b * b * s2                       # replace SDF-only η term
                 + 0.5 * c_eta * c_eta * s2               # …with the joint one
                 + float(d.mu) + float(d.phi) * x
                 + 0.5 * float(d.phi_sigma) ** 2 * (1.0 - float(d.alpha) ** 2) * s2)

        z = np.full(n, 3.5, dtype=np.float64)
        for _ in range(max_iter):
            payoff = q_c * (1.0 + np.exp(z))
            z_new = const + shift_c + np.log(Pi @ payoff)
            self._check_finite(z_new, f"equity claim '{name}' z")
            if np.max(np.abs(z_new - z)) < tol:
                z = z_new
                break
            z = z_new
        else:
            raise SolverDivergenceError(
                f"Equity claim '{name}' did not converge within "
                f"{max_iter} iterations."
            )

        self.z[name] = z
        return z

    # ------------------------------------------------------------------
    # Derived objects
    # ------------------------------------------------------------------
    def risk_free(self) -> np.ndarray:
        """Gross one-period risk-free rate per state, R_f = 1 / E[M′]."""
        const, q, shift = self._sdf_pieces()
        E_M = np.exp(const + shift) * (self.grid.Pi @ q)
        return 1.0 / E_M

    def _stationary_dist(self, max_iter: int = 20_000, tol: float = 1e-14):
        n = self.grid.n_states
        pi = np.ones(n) / n
        Pi = self.grid.Pi
        for _ in range(max_iter):
            pi_new = pi @ Pi
            if np.max(np.abs(pi_new - pi)) < tol:
                pi = pi_new
                break
            pi = pi_new
        self.stationary = pi / pi.sum()
        return self.stationary

    def solve(self, max_iter: int = 200_000, tol: float = 1e-10):
        """Solve the consumption claim and all equity claims."""
        self.solve_consumption_claim(max_iter=max_iter, tol=tol)
        for name in self.p.claims:
            self.solve_equity_claim(name, max_iter=max_iter, tol=tol)
        self._stationary_dist()
        self.converged = True
        return self
