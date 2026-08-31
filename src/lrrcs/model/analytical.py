"""
Approximate analytical solutions (Kiku 2006, Section 3.4).

Log-linear price-dividend elasticities and the long-run component of premia.
The spread between two claims is compensation for differential loading on $$x_t$$.
"""
from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Dict, Mapping
from .params import ModelParams, ConsumptionParams, DividendParams, get_default_params
from .preferences import EpsteinZinPreferences

#: Linearization points for log P/D, by claim name. A claim not listed here
#: anchors at :data:`DEFAULT_PD_ANCHOR`.
PAPER_PD_ANCHORS = {
    "growth": 3.65,
    "value": 3.10,
    "market": 3.24,
    "short": 3.65,
    "long": 3.10,
}

DEFAULT_PD_ANCHOR = 3.30


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


def _gordon_pieces(d: DividendParams, cons: ConsumptionParams,
                   anchor: float) -> tuple[float, float]:
    """Annualized expected dividend growth and the Gordon return at an anchor.

    ``g_eff`` includes the two convexity terms (short-run volatility and the
    persistent component); ``gordon_return`` adds D/P at the linearization
    point. The Gordon return sees the growth channel only and is blind to
    risk, which is the point of the counterfactual it feeds.
    """
    gamma0 = (cons.phi_x * cons.sigma) ** 2 / (1.0 - cons.rho**2)
    g_eff = (
        d.mu
        + 0.5 * d.phi_sigma**2 * cons.sigma**2
        + 0.5 * d.phi**2 * gamma0 * (1.0 + cons.rho) / (1.0 - cons.rho)
    ) * 12.0
    return g_eff, g_eff + float(np.exp(-anchor))


def solve_analytical(params: ModelParams | None = None,
                     mean_zc: float = 3.5,
                     mean_zs: Mapping[str, float] | None = None) -> AnalyticalSolution:
    """Solve the approximate analytical model of Kiku (2006, Section 3.4).

    Log-linear price-dividend elasticities and the long-run component of
    premia follow from the consumption and cash-flow parameters. The spread
    between two claims is compensation for differential loading on expected
    consumption growth.

    Parameters
    ----------
    params : ModelParams, optional
        Complete parameterisation. Defaults to the Table II calibration.
    mean_zc : float
        Linearization point for the consumption claim's log P/C.
    mean_zs : mapping of str to float, optional
        Linearization points for each claim's log P/D. Names absent from
        the mapping fall back to :data:`PAPER_PD_ANCHORS`, then to
        :data:`DEFAULT_PD_ANCHOR`.

    Notes
    -----
    Internal engine behind ``LongRunRisksModel.solve(method="analytical")``.
    """
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
    anchors = dict(PAPER_PD_ANCHORS)
    if mean_zs:
        anchors.update(mean_zs)

    A1: Dict[str, float] = {}
    A2: Dict[str, float] = {}
    premium_lr: Dict[str, float] = {}
    used_mean_z: Dict[str, float] = {}

    for name, d in params.dividends.items():
        mean_z = anchors.get(name, DEFAULT_PD_ANCHOR)
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

