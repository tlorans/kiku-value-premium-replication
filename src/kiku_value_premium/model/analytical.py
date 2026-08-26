"""
Approximate analytical solutions (Kiku 2006, Section 3.4).

Implements the log-linear solutions for price-dividend elasticities A1, A2,
risk prices Lambda, asset betas and the long-run component of risk premia.
This already demonstrates the paper's central result: the value premium is
primarily compensation for differential long-run consumption risk exposure.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict
from .params import ModelParams, get_default_params
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
    premium_lr: Dict[str, float]  # annualized long-run risk premium component
    mean_log_pd: Dict[str, float]  # Section 3.4 Campbell–Shiller linearization points


def solve_analytical(params: ModelParams | None = None,
                     mean_zc: float = 3.5) -> AnalyticalSolution:
    """Solve the approximate analytical model."""
    if params is None:
        params = get_default_params()
    p = params.prefs
    c = params.cons

    # Campbell-Shiller linearization constants for the consumption claim
    kappa_c1 = np.exp(mean_zc) / (1.0 + np.exp(mean_zc))

    # Elasticities of log P/C (paper eq. 10)
    A_c1 = (1.0 - 1.0 / p.psi) / (1.0 - kappa_c1 * c.rho)
    ratio = kappa_c1 * c.phi_x / (1.0 - kappa_c1 * c.rho)
    term = 1.0 + ratio ** 2
    A_c2 = ((1.0 - p.gamma) * (1.0 - 1.0 / p.psi) * term
            / (2.0 * (1.0 - kappa_c1 * c.nu)))

    # Risk prices (paper eq. 14)
    Lambda_eta = p.gamma
    Lambda_eps = (p.gamma - 1.0 / p.psi) * ratio
    Lambda_w = ((1.0 - p.gamma) * (p.gamma - 1.0 / p.psi)
                * (kappa_c1 * term / (2.0 * (1.0 - kappa_c1 * c.nu))))

    E_sigma2 = c.sigma ** 2
    mean_zs = {"growth": 3.65, "value": 3.10, "market": 3.24}

    A1: Dict[str, float] = {}
    A2: Dict[str, float] = {}
    premium_lr: Dict[str, float] = {}

    for name, d in params.dividends.items():
        mean_z = mean_zs[name]
        kappa1 = np.exp(mean_z) / (1.0 + np.exp(mean_z))

        # Elasticity to expected growth (paper eq. 11)
        A1_i = (d.phi - 1.0 / p.psi) / (1.0 - kappa1 * c.rho)
        A1[name] = A1_i

        # Simplified A2 (full expression in paper eq. 12)
        H1 = p.gamma**2 + d.phi_sigma**2 - 2.0 * p.gamma * d.phi_sigma * d.alpha
        tmp = ((p.theta - 1.0) * kappa_c1 * A_c1 + kappa1 * A1_i)
        H2 = (tmp * c.phi_x) ** 2
        A2_i = (((1.0 - p.theta) * A_c2 * (1.0 - kappa_c1 * c.nu)
                 + 0.5 * (H1 + H2))
                / (1.0 - kappa1 * c.nu))
        A2[name] = A2_i

        # Long-run beta and premium (dominant term)
        beta_eps = kappa1 * A1_i * c.phi_x
        prem_m = beta_eps * Lambda_eps * E_sigma2
        premium_lr[name] = prem_m * 12.0  # annualize

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
        mean_log_pd=dict(mean_zs),
    )


def print_value_premium(sol: AnalyticalSolution) -> None:
    print("Approximate annualized long-run risk premia (paper mechanism):")
    for name, prem in sol.premium_lr.items():
        print(f"  {name:8s}: {prem:7.2%}")
    vp = sol.premium_lr["value"] - sol.premium_lr["growth"]
    print(f"Value-growth spread from long-run risks: {vp:.2%}")
    print(f"A1 (PD elasticity to x): growth={sol.A1['growth']:.1f}, "
          f"value={sol.A1['value']:.1f}")
    print(f"Price of long-run risk Lambda_eps = {sol.Lambda_eps:.2f}")
