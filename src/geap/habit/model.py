"""Campbell and Cochrane (1999) external-habit model."""
from __future__ import annotations

from dataclasses import replace as _replace

import numpy as np

from ..base import AssetPricingModel
from .params import CampbellCochraneParams
from .results import CampbellCochraneResults

_MONTHS = 12


def _monthly(params: CampbellCochraneParams):
    """Monthly g, sigma, phi, and gross bill from annual paper numbers."""
    g = params.g / _MONTHS
    sigma = params.sigma / np.sqrt(_MONTHS)
    phi = params.phi ** (1.0 / _MONTHS)
    rf = np.exp(params.rf / _MONTHS)
    return g, sigma, phi, rf


def _gauss_hermite(n: int, sigma: float):
    x, w = np.polynomial.hermite.hermgauss(n)
    v = sigma * np.sqrt(2.0) * x
    weights = w / np.sqrt(np.pi)
    return v, weights


class CampbellCochraneModel(AssetPricingModel):
    """External habit on i.i.d. consumption growth.

    The default is the postwar monthly calibration of Campbell and
    Cochrane (1999). The model prices the consumption claim (``equity``)
    and the one-period bill. Surplus consumption is the only state.

    Parameters
    ----------
    params : CampbellCochraneParams, optional
        Complete parameterisation.
    gamma, g, sigma, phi, rf : float, optional
        Overrides of the annual paper numbers.
    n_s : int
        Surplus grid size.
    n_quad : int
        Gauss-Hermite nodes for the consumption shock.
    """

    def __init__(
        self,
        params: CampbellCochraneParams | None = None,
        *,
        gamma: float | None = None,
        g: float | None = None,
        sigma: float | None = None,
        phi: float | None = None,
        rf: float | None = None,
        n_s: int = 121,
        n_quad: int = 8,
    ):
        base = params if params is not None else CampbellCochraneParams()
        over = {
            k: v
            for k, v in (
                ("gamma", gamma),
                ("g", g),
                ("sigma", sigma),
                ("phi", phi),
                ("rf", rf),
            )
            if v is not None
        }
        self.params = _replace(base, **over)
        self._kwargs = {
            "gamma": gamma,
            "g": g,
            "sigma": sigma,
            "phi": phi,
            "rf": rf,
        }
        self.n_s = int(n_s)
        self.n_quad = int(n_quad)

        g_m, sig_m, phi_m, rf_m = _monthly(self.params)
        self._g = g_m
        self._sigma = sig_m
        self._phi = phi_m
        self._rf_m = rf_m

        self.Sbar = sig_m * np.sqrt(self.params.gamma / (1.0 - phi_m))
        self.sbar = float(np.log(self.Sbar))
        self.s_max = self.sbar + 0.5 * (1.0 - self.Sbar**2)
        self._s_grid = np.linspace(self.s_max - 50.0, self.s_max, self.n_s)

        # δ so that Rf at steady state equals the target.
        lam_bar = 1.0 / self.Sbar - 1.0
        expo = (
            self.params.gamma * g_m
            - 0.5 * (self.params.gamma**2) * (1.0 + lam_bar) ** 2 * sig_m**2
        )
        self.delta = (1.0 / rf_m) * np.exp(expo)
        self._solved: dict | None = None

    @property
    def gamma(self) -> float:
        return self.params.gamma

    @property
    def claims(self) -> tuple[str, ...]:
        return ("equity", "bill")

    def sensitivity(self, s):
        """λ(s) of Campbell and Cochrane, equation (10), with b = 0."""
        s = np.asarray(s, dtype=float)
        inside = np.maximum(1.0 - 2.0 * (s - self.sbar), 0.0)
        lam = (1.0 / self.Sbar) * np.sqrt(inside) - 1.0
        return np.where(s <= self.s_max, lam, 0.0)

    def replace(self, **kwargs) -> "CampbellCochraneModel":
        merged = {k: v for k, v in self._kwargs.items() if v is not None}
        merged.update(kwargs)
        n_s = merged.pop("n_s", self.n_s)
        n_quad = merged.pop("n_quad", self.n_quad)
        return type(self)(self.params, n_s=n_s, n_quad=n_quad, **merged)

    def _price_consumption_claim(self):
        if self._solved is not None:
            return self._solved
        s = self._s_grid
        v, w = _gauss_hermite(self.n_quad, self._sigma)
        gamma = self.gamma
        g, phi, delta = self._g, self._phi, self.delta
        pc = np.full_like(s, np.log(25.0))
        for _ in range(400):
            pc_next = np.empty_like(pc)
            rf_state = np.empty_like(pc)
            for i, si in enumerate(s):
                lam = float(self.sensitivity(si))
                s_n = (1.0 - phi) * self.sbar + phi * si + lam * v
                s_n = np.clip(s_n, s[0], s[-1])
                G = np.exp(g + v)
                M = delta * G ** (-gamma) * np.exp(-gamma * (s_n - si))
                pc_n = np.interp(s_n, s, pc)
                payoff = M * G * (1.0 + np.exp(pc_n))
                pc_next[i] = np.log(float(w @ payoff))
                rf_state[i] = 1.0 / float(w @ M)
            if float(np.max(np.abs(pc_next - pc))) < 1e-8:
                pc = pc_next
                break
            pc = pc_next
        self._solved = {"pc": pc, "rf_state": rf_state, "s": s}
        return self._solved

    def _path(self, months: int, *, seed: int, burn_in: int):
        solved = self._price_consumption_claim()
        s_grid, pc, rf_s = solved["s"], solved["pc"], solved["rf_state"]
        rng = np.random.default_rng(seed)
        si = self.sbar
        eq, bill, z = [], [], []
        phi, g, sig = self._phi, self._g, self._sigma
        for t in range(burn_in + months):
            lam = float(self.sensitivity(si))
            shock = rng.normal(scale=sig)
            s_n = (1.0 - phi) * self.sbar + phi * si + lam * shock
            s_n = float(np.clip(s_n, s_grid[0], s_grid[-1]))
            G = np.exp(g + shock)
            pc_i = float(np.interp(si, s_grid, pc))
            pc_n = float(np.interp(s_n, s_grid, pc))
            R_eq = G * (1.0 + np.exp(pc_n)) / np.exp(pc_i)
            R_f = float(np.interp(si, s_grid, rf_s))
            if t >= burn_in:
                eq.append(R_eq)
                bill.append(R_f)
                z.append(pc_i)
            si = s_n
        return np.array(eq), np.array(bill), np.array(z)

    @staticmethod
    def _annualize(monthly: np.ndarray) -> np.ndarray:
        n = (len(monthly) // _MONTHS) * _MONTHS
        if n == 0:
            return np.array([])
        grouped = monthly[:n].reshape(-1, _MONTHS)
        return grouped.prod(axis=1)

    def solve(self, method: str = "grid", **kwargs) -> CampbellCochraneResults:
        if method not in ("grid", "analytical"):
            raise ValueError(
                f"method must be 'grid' or 'analytical', got {method!r}."
            )
        eq, bill, z = self._path(24_000, seed=0, burn_in=2_000)
        eq_a = self._annualize(eq)
        bill_a = self._annualize(bill)
        expected = {
            "equity": (float(eq_a.mean()) - 1.0) * 100.0,
            "bill": (float(bill_a.mean()) - 1.0) * 100.0,
        }
        vol = {
            "equity": float(eq_a.std(ddof=1)) * 100.0,
            "bill": float(bill_a.std(ddof=1)) * 100.0,
        }
        log_pd = {
            "equity": float(z.mean()),
            "bill": float("nan"),
        }
        return CampbellCochraneResults(self, expected, vol, log_pd)

    def simulate(
        self,
        n_samples: int = 50,
        years: int = 70,
        *,
        seed: int = 0,
        burn_in: int = 120,
    ) -> CampbellCochraneResults:
        months = years * _MONTHS
        eq_means, bill_means = [], []
        rng_seeds = np.random.default_rng(seed).integers(0, 2**31, size=n_samples)
        for sample_seed in rng_seeds:
            eq, bill, _ = self._path(months, seed=int(sample_seed), burn_in=burn_in)
            eq_a = self._annualize(eq)
            bill_a = self._annualize(bill)
            eq_means.append(float(eq_a.mean()))
            bill_means.append(float(bill_a.mean()))
        expected = {
            "equity": (float(np.mean(eq_means)) - 1.0) * 100.0,
            "bill": (float(np.mean(bill_means)) - 1.0) * 100.0,
        }
        vol = {
            "equity": float(np.std(eq_means, ddof=1)) * 100.0,
            "bill": float(np.std(bill_means, ddof=1)) * 100.0,
        }
        return CampbellCochraneResults(
            self,
            expected,
            vol,
            n_samples=n_samples,
            years=years,
            seed=seed,
        )

    def __repr__(self) -> str:
        return (
            f"CampbellCochraneModel(gamma={self.gamma:g}, "
            f"phi={self.params.phi:g}, Sbar={self.Sbar:.3f})"
        )
