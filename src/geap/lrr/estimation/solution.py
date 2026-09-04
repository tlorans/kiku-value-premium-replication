"""Log-linear solution of the LRR model (Bansal, Kiku, Yaron 2016, appendix A).

Evaluated at the agent's decision frequency. Time aggregation of these
objects is a separate step.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.optimize import root_scalar


@dataclass
class BKYParams:
    """High-frequency LRR parameters, JME Table 2 notation.

    ``sigma`` is σ₀, the unconditional standard deviation of consumption
    innovations. ``phi_d_sigma`` is ϕ_d, dividend exposure to short-run
    volatility. ``rho_d`` is corr(u_{d}, η).
    """

    gamma: float
    psi: float
    delta: float
    mu_c: float
    rho: float
    phi_e: float
    sigma: float
    nu: float
    sigma_w: float
    mu_d: float
    phi_d: float
    phi_d_sigma: float
    rho_d: float

    @property
    def theta(self) -> float:
        if abs(self.psi - 1.0) < 1e-12:
            raise ZeroDivisionError("theta is undefined at psi = 1")
        return (1.0 - self.gamma) / (1.0 - 1.0 / self.psi)

    @property
    def ies_one(self) -> bool:
        return abs(self.psi - 1.0) < 1e-12


@dataclass
class LogLinearSolution:
    """Affine coefficients for z_c, z_d, m, and r_f."""

    mean_zc: float
    kappa_c0: float
    kappa_c1: float
    A_c0: float
    A_c1: float
    A_c2: float
    mean_zd: float
    kappa_d0: float
    kappa_d1: float
    A_d0: float
    A_d1: float
    A_d2: float
    Gamma: np.ndarray  # (Γ0, Γ1, Γ2)
    Lambda: np.ndarray  # (λ_η, λ_e, λ_w)
    F: np.ndarray  # (F0, F1, F2)
    B_d: np.ndarray  # (B0, B1, B2) for r_{d,t+1}
    beta_d: np.ndarray  # (β_u, β_e, β_w)


def _kappas(zbar: float) -> tuple[float, float]:
    ez = np.exp(zbar)
    k1 = ez / (1.0 + ez)
    k0 = np.log(1.0 + ez) - k1 * zbar
    return float(k0), float(k1)


def _consumption_coefficients(
    k0: float, k1: float, p: BKYParams, theta: float
) -> tuple[float, float, float]:
    den_rho = 1.0 - k1 * p.rho
    den_nu = 1.0 - k1 * p.nu
    A1 = (1.0 - 1.0 / p.psi) / den_rho
    term = 1.0 + (k1 * p.phi_e / den_rho) ** 2
    A2 = -(p.gamma - 1.0) * (1.0 - 1.0 / p.psi) / (2.0 * den_nu) * term
    A0 = (1.0 / (1.0 - k1)) * (
        np.log(p.delta)
        + k0
        + (1.0 - 1.0 / p.psi) * p.mu_c
        + k1 * A2 * (1.0 - p.nu) * p.sigma**2
        + 0.5 * theta * (k1 * A2 * p.sigma_w) ** 2
    )
    return float(A0), float(A1), float(A2)


def _solve_mean_zc(p: BKYParams, theta: float) -> tuple[float, float, float, float, float]:
    def resid(z: float) -> float:
        k0, k1 = _kappas(z)
        A0, _, A2 = _consumption_coefficients(k0, k1, p, theta)
        return A0 + A2 * p.sigma**2 - z

    bracket = None
    lo, hi = -2.0, 12.0
    r_lo, r_hi = resid(lo), resid(hi)
    if np.sign(r_lo) != np.sign(r_hi) and np.isfinite(r_lo) and np.isfinite(r_hi):
        bracket = (lo, hi)
    else:
        grid = np.linspace(-1.0, 10.0, 50)
        vals = [resid(float(z)) for z in grid]
        for a, b, fa, fb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
            if np.isfinite(fa) and np.isfinite(fb) and np.sign(fa) != np.sign(fb):
                bracket = (float(a), float(b))
                break
    if bracket is None:
        raise RuntimeError("Could not bracket the mean log P/C fixed point.")
    root = root_scalar(resid, bracket=bracket, method="brentq")
    zbar = float(root.root)
    k0, k1 = _kappas(zbar)
    A0, A1, A2 = _consumption_coefficients(k0, k1, p, theta)
    return zbar, k0, k1, A0, A1, A2


def _kernel_and_rf(
    p: BKYParams,
    *,
    k1: float,
    A1: float,
    A2: float,
    theta: float | None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if p.ies_one:
        d_rho = 1.0 - p.delta * p.rho
        d_nu = 1.0 - p.delta * p.nu
        A2_vc = (
            -(p.gamma - 1.0)
            * 0.5
            * p.delta
            / d_nu
            * (1.0 + (p.delta * p.phi_e / d_rho) ** 2)
        )
        Gamma = np.array(
            [
                np.log(p.delta)
                - p.mu_c
                - 0.5 * (1.0 - p.gamma) ** 2 * (A2_vc * p.sigma_w) ** 2,
                -1.0,
                -0.5
                * (p.gamma - 1.0) ** 2
                * (1.0 + (p.delta * p.phi_e / d_rho) ** 2),
            ]
        )
        Lam = np.array(
            [
                p.gamma,
                (p.gamma - 1.0) * p.delta * p.phi_e / d_rho,
                -(p.gamma - 1.0) ** 2
                * 0.5
                * p.delta
                / d_nu
                * (1.0 + (p.delta * p.phi_e / d_rho) ** 2),
            ]
        )
    else:
        assert theta is not None
        Gamma = np.array(
            [
                np.log(p.delta)
                - (1.0 / p.psi) * p.mu_c
                - 0.5 * theta * (theta - 1.0) * (k1 * A2 * p.sigma_w) ** 2,
                -1.0 / p.psi,
                (theta - 1.0) * (k1 * p.nu - 1.0) * A2,
            ]
        )
        Lam = np.array(
            [
                p.gamma,
                (p.gamma - 1.0 / p.psi) * k1 * p.phi_e / (1.0 - k1 * p.rho),
                (1.0 - theta) * k1 * A2,
            ]
        )
    F = np.array(
        [
            -Gamma[0] - 0.5 * (Lam[2] * p.sigma_w) ** 2,
            -Gamma[1],
            -Gamma[2] - 0.5 * (Lam[0] ** 2 + Lam[1] ** 2),
        ]
    )
    return Gamma, Lam, F


def _dividend_coefficients(
    p: BKYParams,
    Gamma: np.ndarray,
    Lam: np.ndarray,
) -> tuple[float, float, float, float, float, float]:
    ies_term = 1.0 if p.ies_one else 1.0 / p.psi

    def pack(k0: float, k1: float) -> tuple[float, float, float]:
        A1 = (p.phi_d - ies_term) / (1.0 - k1 * p.rho)
        A2 = (1.0 / (1.0 - k1 * p.nu)) * (
            Gamma[2]
            + 0.5
            * (
                p.phi_d_sigma**2
                + Lam[0] ** 2
                - 2.0 * p.rho_d * p.phi_d_sigma * Lam[0]
                + (k1 * A1 * p.phi_e - Lam[1]) ** 2
            )
        )
        A0 = (1.0 / (1.0 - k1)) * (
            Gamma[0]
            + k0
            + p.mu_d
            + k1 * A2 * (1.0 - p.nu) * p.sigma**2
            + 0.5 * (k1 * A2 - Lam[2]) ** 2 * p.sigma_w**2
        )
        return float(A0), float(A1), float(A2)

    def resid(z: float) -> float:
        k0, k1 = _kappas(z)
        A0, _, A2 = pack(k0, k1)
        return A0 + A2 * p.sigma**2 - z

    bracket = None
    grid = np.linspace(0.5, 8.0, 40)
    vals = [resid(float(z)) for z in grid]
    for a, b, fa, fb in zip(grid[:-1], grid[1:], vals[:-1], vals[1:]):
        if np.isfinite(fa) and np.isfinite(fb) and np.sign(fa) != np.sign(fb):
            bracket = (float(a), float(b))
            break
    if bracket is None:
        raise RuntimeError("Could not bracket the mean log P/D fixed point.")
    root = root_scalar(resid, bracket=bracket, method="brentq")
    zbar = float(root.root)
    k0, k1 = _kappas(zbar)
    A0, A1, A2 = pack(k0, k1)
    return zbar, k0, k1, A0, A1, A2


def _return_loadings(
    p: BKYParams,
    k0: float,
    k1: float,
    A0: float,
    A1: float,
    A2: float,
) -> tuple[np.ndarray, np.ndarray]:
    B0 = (
        k0
        + (k1 - 1.0) * A0
        + k1 * A2 * (1.0 - p.nu) * p.sigma**2
        + p.mu_d
    )
    B1 = k1 * A1 * p.rho - A1 + p.phi_d
    B2 = k1 * A2 * p.nu - A2
    beta = np.array(
        [
            p.phi_d_sigma,
            k1 * A1 * p.phi_e,
            k1 * A2,
        ]
    )
    return np.array([B0, B1, B2]), beta


def solve_loglinear(params: BKYParams) -> LogLinearSolution:
    """Solve appendix A at the decision frequency."""
    p = params
    if p.ies_one:
        zbar = float(np.log(p.delta / (1.0 - p.delta)))
        k0, k1 = _kappas(zbar)
        # P/C is constant: A1 = A2 = 0, A0 = zbar.
        A0, A1, A2 = zbar, 0.0, 0.0
        # Campbell–Shiller κ1 equals δ at IES = 1.
        k1 = p.delta
        k0 = np.log(1.0 + np.exp(zbar)) - k1 * zbar
        theta = None
    else:
        theta = p.theta
        zbar, k0, k1, A0, A1, A2 = _solve_mean_zc(p, theta)

    Gamma, Lam, F = _kernel_and_rf(p, k1=k1, A1=A1, A2=A2, theta=theta)
    zd, kd0, kd1, Ad0, Ad1, Ad2 = _dividend_coefficients(p, Gamma, Lam)
    B_d, beta_d = _return_loadings(p, kd0, kd1, Ad0, Ad1, Ad2)
    return LogLinearSolution(
        mean_zc=zbar,
        kappa_c0=k0,
        kappa_c1=k1,
        A_c0=A0,
        A_c1=A1,
        A_c2=A2,
        mean_zd=zd,
        kappa_d0=kd0,
        kappa_d1=kd1,
        A_d0=Ad0,
        A_d1=Ad1,
        A_d2=Ad2,
        Gamma=Gamma,
        Lambda=Lam,
        F=F,
        B_d=B_d,
        beta_d=beta_d,
    )
