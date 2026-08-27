"""
Approximate analytical solutions (Kiku 2006, Section 3.4).

Log-linear price-dividend elasticities and the long-run component of premia.
The spread between two claims is compensation for differential loading on $$x_t$$.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict
from .params import ModelParams, get_default_params
from .legs import resolve_legs
from .preferences import EpsteinZinPreferences


@dataclass
class AnalyticalSolution:
    kappa_c1: float
    A_c1: float
    A_c2: float
    Lambda_eta: float
    Lambda_eps: float
    Lambda_w: float
    A1: Dict[str, float]
    A2: Dict[str, float]
    premium_lr: Dict[str, float]
    mean_log_pd: Dict[str, float]


def solve_analytical(params: ModelParams | None = None,
                     mean_zc: float = 3.5) -> AnalyticalSolution:
    """Solve the approximate analytical model."""
    if params is None:
        params = get_default_params()
    p = params.prefs
    c = params.cons

    kappa_c1 = np.exp(mean_zc) / (1.0 + np.exp(mean_zc))

    A_c1 = (1.0 - 1.0 / p.psi) / (1.0 - kappa_c1 * c.rho)
    ratio = kappa_c1 * c.phi_x / (1.0 - kappa_c1 * c.rho)
    term = 1.0 + ratio ** 2
    A_c2 = ((1.0 - p.gamma) * (1.0 - 1.0 / p.psi) * term
            / (2.0 * (1.0 - kappa_c1 * c.nu)))

    Lambda_eta = p.gamma
    Lambda_eps = (p.gamma - 1.0 / p.psi) * ratio
    Lambda_w = ((1.0 - p.gamma) * (p.gamma - 1.0 / p.psi)
                * (kappa_c1 * term / (2.0 * (1.0 - kappa_c1 * c.nu))))

    E_sigma2 = c.sigma ** 2
    mean_zs = {
        "growth": 3.65,
        "value": 3.10,
        "market": 3.24,
        "short": 3.65,
        "long": 3.10,
    }

    A1: Dict[str, float] = {}
    A2: Dict[str, float] = {}
    premium_lr: Dict[str, float] = {}
    used_mean_z: Dict[str, float] = {}

    for name, d in params.dividends.items():
        mean_z = mean_zs.get(name, 3.30)
        used_mean_z[name] = mean_z
        kappa1 = np.exp(mean_z) / (1.0 + np.exp(mean_z))

        A1_i = (d.phi - 1.0 / p.psi) / (1.0 - kappa1 * c.rho)
        A1[name] = A1_i

        H1 = p.gamma**2 + d.phi_sigma**2 - 2.0 * p.gamma * d.phi_sigma * d.alpha
        tmp = ((p.theta - 1.0) * kappa_c1 * A_c1 + kappa1 * A1_i)
        H2 = (tmp * c.phi_x) ** 2
        A2_i = (((1.0 - p.theta) * A_c2 * (1.0 - kappa_c1 * c.nu)
                 + 0.5 * (H1 + H2))
                / (1.0 - kappa1 * c.nu))
        A2[name] = A2_i

        beta_eps = kappa1 * A1_i * c.phi_x
        prem_m = beta_eps * Lambda_eps * E_sigma2
        premium_lr[name] = prem_m * 12.0

    return AnalyticalSolution(
        kappa_c1=kappa_c1,
        A_c1=A_c1,
        A_c2=A_c2,
        Lambda_eta=Lambda_eta,
        Lambda_eps=Lambda_eps,
        Lambda_w=Lambda_w,
        A1=A1,
        A2=A2,
        premium_lr=premium_lr,
        mean_log_pd=used_mean_z,
    )


def print_long_short_premium(
    sol: AnalyticalSolution,
    long: str | None = None,
    short: str | None = None,
) -> None:
    print("Approximate annualized long-run risk premia:")
    for name, prem in sol.premium_lr.items():
        print(f"  {name:8s}: {prem:7.2%}")
    long_key, short_key, _ = resolve_legs(sol.premium_lr, long=long, short=short)
    vp = sol.premium_lr[long_key] - sol.premium_lr[short_key]
    paper_names = {long_key, short_key} <= {"value", "growth"}
    label = "Value-growth" if paper_names else "Long-short"
    print(f"{label} spread from long-run risks: {vp:.2%}")
    print(
        f"A1 (PD elasticity to x): {short_key}={sol.A1[short_key]:.1f}, "
        f"{long_key}={sol.A1[long_key]:.1f}"
    )
    print(f"Price of long-run risk Lambda_eps = {sol.Lambda_eps:.2f}")


print_value_premium = print_long_short_premium
