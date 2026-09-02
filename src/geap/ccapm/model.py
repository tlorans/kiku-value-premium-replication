"""Power-utility CCAPM on a two-state consumption chain."""
from __future__ import annotations

from dataclasses import replace as _replace
from typing import Mapping

import numpy as np

from ..base import AssetPricingModel
from .params import PowerUtilityParams
from .results import PowerUtilityResults

_CLAIM_FIELDS = ("phi",)


def _as_phi(value, name: str) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    if not isinstance(value, Mapping):
        raise TypeError(
            f"Claim {name!r} must be a mapping with 'phi' or a number, "
            f"got {type(value).__name__}."
        )
    unknown = set(value) - set(_CLAIM_FIELDS)
    if unknown:
        raise TypeError(
            f"Claim {name!r} got unknown field(s) {sorted(unknown)}; "
            f"expected 'phi'."
        )
    if "phi" not in value:
        raise TypeError(f"Claim {name!r} needs a 'phi'.")
    return float(value["phi"])


def _two_state(params: PowerUtilityParams):
    """Gross consumption growth, transition, stationary distribution."""
    g = np.array(
        [1.0 + params.mu + params.sigma, 1.0 + params.mu - params.sigma],
        dtype=float,
    )
    stay = (1.0 + params.rho) / 2.0
    P = np.array([[stay, 1.0 - stay], [1.0 - stay, stay]], dtype=float)
    pi = np.array([0.5, 0.5], dtype=float)
    return g, P, pi


def _price_claim(g_cons, P, delta, gamma, g_div):
    """Price-dividend ratios of a claim with gross dividend growth ``g_div``."""
    sdf = delta * g_cons ** (-gamma)
    A = P * (sdf * g_div)[None, :]
    eye = np.eye(2)
    rhs = A @ np.ones(2)
    q = np.linalg.solve(eye - A, rhs)
    return q, sdf


def _return_moments(g_div, q, P, pi):
    """Unconditional mean and volatility of the gross return."""
    R = (g_div[None, :] * (q[None, :] + 1.0)) / q[:, None]
    mean_by_state = (P * R).sum(axis=1)
    mean = float(pi @ mean_by_state)
    second = float(pi @ (P * R**2).sum(axis=1))
    vol = float(np.sqrt(max(second - mean**2, 0.0)))
    log_pd = float(pi @ np.log(q))
    return mean, vol, log_pd, R


class PowerUtilityModel(AssetPricingModel):
    """Mehra and Prescott (1985) power-utility endowment economy.

    The default endowment is their two-state Markov chain for annual
    per-capita consumption growth. Preferences are power utility. The
    model always prices the consumption claim (``equity``) and the
    one-period bill. Extra claims are levered consumption,
    ``g_div = g_cons ** phi``.

    Parameters
    ----------
    params : PowerUtilityParams, optional
        Complete parameterisation. Defaults to Mehra and Prescott.
    delta, gamma : float, optional
        Preference overrides.
    mu, sigma, rho : float, optional
        Consumption-process overrides.
    claims : mapping, optional
        Extra (or replacement) levered claims, as ``{"name": {"phi": 3}}``.
        ``bill`` cannot be a levered claim. ``equity`` defaults to
        ``phi = 1`` (the Lucas tree).
    """

    def __init__(
        self,
        params: PowerUtilityParams | None = None,
        *,
        delta: float | None = None,
        gamma: float | None = None,
        mu: float | None = None,
        sigma: float | None = None,
        rho: float | None = None,
        claims: Mapping | None = None,
    ):
        base = params if params is not None else PowerUtilityParams()
        over = {
            k: v
            for k, v in (
                ("delta", delta),
                ("gamma", gamma),
                ("mu", mu),
                ("sigma", sigma),
                ("rho", rho),
            )
            if v is not None
        }
        self.params = _replace(base, **over)
        self._kwargs = {
            "delta": delta,
            "gamma": gamma,
            "mu": mu,
            "sigma": sigma,
            "rho": rho,
        }
        extras: dict[str, float] = {}
        equity_phi = 1.0
        if claims:
            for name, spec in claims.items():
                if name == "bill":
                    raise ValueError(
                        "bill is the one-period risk-free claim; it has no phi."
                    )
                phi = _as_phi(spec, name)
                if name == "equity":
                    equity_phi = phi
                else:
                    extras[name] = phi
        self._equity_phi = equity_phi
        self._extras = extras
        g, P, pi = _two_state(self.params)
        self._g = g
        self._P = P
        self._pi = pi

    @property
    def delta(self) -> float:
        return self.params.delta

    @property
    def gamma(self) -> float:
        return self.params.gamma

    @property
    def consumption_growth(self) -> np.ndarray:
        return self._g.copy()

    @property
    def transition(self) -> np.ndarray:
        return self._P.copy()

    @property
    def stationary(self) -> np.ndarray:
        return self._pi.copy()

    @property
    def claims(self) -> tuple[str, ...]:
        return ("equity", "bill") + tuple(self._extras)

    def replace(self, **kwargs) -> "PowerUtilityModel":
        merged = {k: v for k, v in self._kwargs.items() if v is not None}
        merged.update(kwargs)
        claims = merged.pop("claims", None)
        if claims is None and self._extras:
            claims = {name: {"phi": phi} for name, phi in self._extras.items()}
            if self._equity_phi != 1.0:
                claims = {"equity": {"phi": self._equity_phi}, **claims}
        return type(self)(self.params, claims=claims, **merged)

    def _leverages(self) -> dict[str, float]:
        out = {"equity": self._equity_phi}
        out.update(self._extras)
        return out

    def solve(self, method: str = "grid", **kwargs) -> PowerUtilityResults:
        if method not in ("grid", "analytical"):
            raise ValueError(
                f"method must be 'grid' or 'analytical', got {method!r}."
            )
        g, P, pi = self._g, self._P, self._pi
        delta, gamma = self.delta, self.gamma
        expected = {}
        vol = {}
        log_pd = {}
        for name, phi in self._leverages().items():
            g_div = g**phi
            q, _ = _price_claim(g, P, delta, gamma, g_div)
            mean, sigma, z, _ = _return_moments(g_div, q, P, pi)
            expected[name] = (mean - 1.0) * 100.0
            vol[name] = sigma * 100.0
            log_pd[name] = z
        sdf = delta * g ** (-gamma)
        rf_state = 1.0 / (P @ sdf)
        rf = float(pi @ rf_state)
        expected["bill"] = (rf - 1.0) * 100.0
        vol["bill"] = float(np.sqrt(max(pi @ rf_state**2 - rf**2, 0.0))) * 100.0
        log_pd["bill"] = float("nan")
        return PowerUtilityResults(self, expected, vol, log_pd)

    def simulate(
        self,
        n_samples: int = 200,
        years: int = 100,
        *,
        seed: int = 0,
        burn_in: int = 20,
    ) -> PowerUtilityResults:
        g, P, pi = self._g, self._P, self._pi
        delta, gamma = self.delta, self.gamma
        sdf = delta * g ** (-gamma)
        rf_state = 1.0 / (P @ sdf)
        priced = {}
        for name, phi in self._leverages().items():
            g_div = g**phi
            q, _ = _price_claim(g, P, delta, gamma, g_div)
            _, _, _, R = _return_moments(g_div, q, P, pi)
            priced[name] = R

        rng = np.random.default_rng(seed)
        cdf = np.cumsum(P, axis=1)
        means = {name: [] for name in self.claims}
        for _ in range(n_samples):
            i = int(rng.choice(2, p=pi))
            path = {name: [] for name in self.claims}
            for t in range(burn_in + years):
                u = rng.random()
                j = 0 if u < cdf[i, 0] else 1
                if t >= burn_in:
                    for name, R in priced.items():
                        path[name].append(R[i, j])
                    path["bill"].append(rf_state[i])
                i = j
            for name in self.claims:
                means[name].append(float(np.mean(path[name])))
        expected = {
            name: (float(np.mean(vals)) - 1.0) * 100.0
            for name, vals in means.items()
        }
        vol = {
            name: float(np.std(vals, ddof=1)) * 100.0
            for name, vals in means.items()
        }
        return PowerUtilityResults(
            self,
            expected,
            vol,
            n_samples=n_samples,
            years=years,
            seed=seed,
        )

    def __repr__(self) -> str:
        return (
            f"PowerUtilityModel(gamma={self.gamma:g}, delta={self.delta:g}, "
            f"claims={list(self.claims)})"
        )
