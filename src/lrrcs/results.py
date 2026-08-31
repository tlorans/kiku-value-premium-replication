"""Results of solving and simulating a :class:`~lrrcs.api.LongRunRisksModel`.

Every solve or simulation returns one of these objects. They hold the
numbers as attributes, print a formatted table through
:meth:`summary`, and hand back a tidy frame through :meth:`to_frame`.

Conventions
-----------
Returns, premia, volatilities, and the risk-free rate are annualized and
in percent. Log price-dividend ratios are in logs. Quantities that vary
by claim are ``pandas.Series`` indexed by claim name; quantities that
describe the whole model are floats.
"""
from __future__ import annotations

import html
from typing import Iterable, Mapping

import numpy as np
import pandas as pd

from ._backend import to_backend
from .model.analytical import AnalyticalSolution, _gordon_pieces
from .model.legs import Legs
from .model.params import ModelParams

# Kiku (2006) Table VII, Model column: cross-sample means of annual stats.
# Shown beside our own numbers when the model is the untouched Table II
# calibration, and omitted otherwise.
_PAPER_TABLE_VII = {
    "mean_return": {"growth": 6.07, "value": 11.36, "market": 7.53},
    "volatility": {"growth": 21.5, "value": 29.0, "market": 20.1},
    "capm_beta": {"growth": 1.00, "value": 0.92, "market": 1.00},
    "mean_log_pd": {"growth": 3.65, "value": 3.10, "market": 3.24},
    "mean_rf": 1.58,
    "value_premium": 5.29,
    "beta_ratio": 0.92,
}


class Summary:
    """Formatted text summary of a results object.

    Printing it, or letting a notebook or REPL echo it, shows the table.
    :meth:`as_text` returns the same thing as a string.
    """

    def __init__(self, lines: Iterable[str]):
        self._lines = list(lines)

    def as_text(self) -> str:
        """The summary as a plain string."""
        return "\n".join(self._lines)

    def __str__(self) -> str:
        return self.as_text()

    def __repr__(self) -> str:
        return self.as_text()

    def _repr_html_(self) -> str:
        return f"<pre>{html.escape(self.as_text())}</pre>"


def _series(values: Mapping[str, float], claims: Iterable[str]) -> pd.Series:
    """A float Series over ``claims``, NaN where a claim has no value."""
    claims = list(claims)
    return pd.Series(
        [float(values.get(name, np.nan)) for name in claims],
        index=claims,
        dtype=float,
    )


def _fmt(value: float, width: int = 8, decimals: int = 2) -> str:
    """Right-aligned fixed-point number, or a dash when undefined."""
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return "-".rjust(width)
    return f"{value:{width}.{decimals}f}"


class LRRResults:
    """Shared surface of every results object.

    Attributes
    ----------
    model : LongRunRisksModel
        The model these results came from.
    params : ModelParams
        Its parameterisation.
    method : str
        How the results were produced.
    claims : tuple of str
        The claim names, in the order the model prices them.
    legs : Legs
        Which claim plays the long, short, and market role.
    """

    method = "base"

    def __init__(self, model):
        self.model = model
        self.params: ModelParams = model.params
        self.claims: tuple[str, ...] = tuple(model.params.dividends)
        self.legs: Legs = model.legs

    # -- shared helpers -------------------------------------------------
    @property
    def _is_paper_calibration(self) -> bool:
        """True for the untouched Table II calibration."""
        return self.params == ModelParams()

    def _spread(self, values: pd.Series) -> float:
        """Long leg minus short leg, NaN when either leg is missing."""
        long, short = self.legs.long, self.legs.short
        if long is None or short is None:
            return float("nan")
        return float(values[long] - values[short])

    def _premium_label(self) -> str:
        paper_legs = {self.legs.long, self.legs.short} <= {"value", "growth"}
        return "Value premium" if paper_legs else "Long-short premium"

    def _header_lines(self, subtitle: str) -> list[str]:
        p = self.params.prefs
        legs = f"long={self.legs.long}, short={self.legs.short}"
        if self.legs.market:
            legs += f", market={self.legs.market}"
        return [
            "=" * 72,
            "Long-Run Risks Model Results".center(72),
            "=" * 72,
            f"Model:        Kiku (2006) general equilibrium",
            f"Method:       {subtitle}",
            f"Preferences:  delta = {p.delta:g}   gamma = {p.gamma:g}   "
            f"psi = {p.psi:g}   theta = {p.theta:.1f}",
            f"Claims:       {', '.join(self.claims)}",
            f"Legs:         {legs}",
        ]

    def summary(self) -> Summary:  # pragma: no cover - overridden
        raise NotImplementedError

    def to_frame(self):  # pragma: no cover - overridden
        raise NotImplementedError

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__} method={self.method!r} "
            f"claims={list(self.claims)} "
            f"value_premium={getattr(self, 'value_premium', float('nan')):.2f}>"
        )


class GridResults(LRRResults):
    """Population moments from the quadrature (Tauchen-Hussey) solution.

    Moments are computed state by state and averaged under the stationary
    distribution of the discretized economy, then annualized.

    Attributes
    ----------
    expected_returns, volatility, sharpe_ratios, capm_betas : pandas.Series
        Annualized return moments by claim, in percent (betas unitless).
    mean_log_pd, price_dividend : pandas.Series
        Mean log price-dividend ratio and its level, by claim.
    risk_free : float
        Annualized risk-free rate, in percent.
    value_premium : float
        Long leg minus short leg expected return, in percent.
    log_pd_spread : float
        Long leg minus short leg mean log P/D.
    converged : bool
        Whether every Euler fixed point converged.
    n_x, n_s : int
        Grid size for expected growth and variance.
    z_c, z, stationary, x_nodes, s2_nodes
        The solved valuation functions and the grid behind them.
    """

    method = "grid"

    def __init__(self, model, solver, moments: dict | None):
        super().__init__(model)
        self._solver = solver
        self._moments = moments
        self.n_x = solver.grid.n_x
        self.n_s = solver.grid.n_s
        self.converged = bool(solver.converged)

        from .implications.moments import claim_stats

        pi = solver.stationary
        stats = {name: claim_stats(solver, name, pi) for name in self.claims}

        self.expected_returns = _series(
            {n: s["mean_return"] for n, s in stats.items()}, self.claims
        )
        self.volatility = _series(
            {n: s["volatility"] for n, s in stats.items()}, self.claims
        )
        self.mean_log_pd = _series(
            {n: s["mean_log_pd"] for n, s in stats.items()}, self.claims
        )
        self.price_dividend = np.exp(self.mean_log_pd)

        if moments is not None:
            self.risk_free = float(moments["mean_rf"])
            self.capm_betas = _series(moments["capm_beta"], self.claims)
            if self.legs.market is not None:
                self.capm_betas[self.legs.market] = 1.0
        else:
            # No market claim: the risk-free rate still follows from the SDF,
            # but market betas are undefined.
            Rf = 1.0 / float(np.dot(pi, 1.0 / solver.risk_free()))
            self.risk_free = (Rf**12 - 1) * 100
            self.capm_betas = _series({}, self.claims)

        self.sharpe_ratios = pd.Series(
            [
                (self.expected_returns[n] - self.risk_free) / self.volatility[n]
                if self.volatility[n] > 0
                else np.nan
                for n in self.claims
            ],
            index=list(self.claims),
            dtype=float,
        )
        self.value_premium = self._spread(self.expected_returns)
        self.log_pd_spread = self._spread(self.mean_log_pd)

    @property
    def long_short_premium(self) -> float:
        """Alias of :attr:`value_premium` for non-paper leg names."""
        return self.value_premium

    # -- the solved objects behind the moments --------------------------
    @property
    def z_c(self) -> np.ndarray:
        """Log price-consumption ratio, state by state."""
        return self._solver.z_c

    @property
    def z(self) -> dict[str, np.ndarray]:
        """Log price-dividend ratio per claim, state by state."""
        return self._solver.z

    @property
    def stationary(self) -> np.ndarray:
        """Stationary distribution of the discretized state chain."""
        return self._solver.stationary

    @property
    def x_nodes(self) -> np.ndarray:
        """Expected-growth grid nodes."""
        return self._solver.grid.x_nodes

    @property
    def s2_nodes(self) -> np.ndarray:
        """Variance grid nodes."""
        return self._solver.grid.s2_nodes

    def states(self):
        """Per-state diagnostics as a frame.

        One row per grid state, with the expected-growth and variance
        node, the stationary weight, the risk-free rate, and each claim's
        log price-dividend ratio.
        """
        g = self._solver.grid
        out = pd.DataFrame(
            {
                "x": g.x_grid,
                "sigma2": g.s2_grid,
                "stationary": self._solver.stationary,
                "risk_free": self._solver.risk_free(),
                "z_c": self._solver.z_c,
            }
        )
        for name in self.claims:
            out[f"z_{name}"] = self._solver.z[name]
        return to_backend(out)

    def to_frame(self):
        """Moments by claim, one row per claim."""
        out = pd.DataFrame(
            {
                "expected_return": self.expected_returns,
                "volatility": self.volatility,
                "sharpe": self.sharpe_ratios,
                "capm_beta": self.capm_betas,
                "mean_log_pd": self.mean_log_pd,
                "price_dividend": self.price_dividend,
            }
        )
        out.index.name = "claim"
        return to_backend(out.reset_index())

    def summary(self) -> Summary:
        """Formatted population moments, in the style of Tables VII-VIII."""
        lines = self._header_lines(f"grid ({self.n_x} x {self.n_s} states)")
        lines.append(f"Converged:    {self.converged}")
        lines.append("-" * 72)
        lines.append(
            f"{'Claim':12s} {'E[R] %':>8s} {'Vol %':>8s} {'Sharpe':>8s} "
            f"{'CAPM b':>8s} {'log(P/D)':>9s} {'P/D':>8s}"
        )
        for name in self.claims:
            lines.append(
                f"{name:12s} {_fmt(self.expected_returns[name])} "
                f"{_fmt(self.volatility[name])} {_fmt(self.sharpe_ratios[name])} "
                f"{_fmt(self.capm_betas[name])} {_fmt(self.mean_log_pd[name], 9)} "
                f"{_fmt(self.price_dividend[name], 8, 1)}"
            )
        lines.append("-" * 72)
        lines.append(f"Risk-free rate                {_fmt(self.risk_free)} %")
        lines.append(f"{self._premium_label():29s} {_fmt(self.value_premium)} %")
        lines.append(f"log(P/D) spread (long-short)  {_fmt(self.log_pd_spread)}")
        lines.append("=" * 72)
        lines.append(
            "Population moments under the stationary distribution, annualized."
        )
        return Summary(lines)


class AnalyticalResults(LRRResults):
    """Loadings and risk prices from the log-linear solution (Section 3.4).

    The approximation prices each claim around a fixed linearization
    point for its log P/D, so ``mean_log_pd`` here is that anchor, not a
    solved level. ``long_run_premium`` is the compensation for
    expected-growth news only; short-run and volatility news add more.

    Attributes
    ----------
    A1, A2 : pandas.Series
        Price-dividend elasticities to expected growth and to volatility.
    long_run_premium : pandas.Series
        Annualized long-run risk premium by claim, in percent.
    expected_growth, gordon_return : pandas.Series
        Annualized expected dividend growth including convexity, and the
        Gordon return at the anchor, in percent.
    risk_prices : pandas.Series
        Prices of the short-run, long-run, and volatility shocks.
    value_premium : float
        Long leg minus short leg long-run premium, in percent.
    """

    method = "analytical"

    def __init__(self, model, solution: AnalyticalSolution):
        super().__init__(model)
        self._solution = solution
        self.kappa_c1 = float(solution.kappa_c1)
        self.A_c1 = float(solution.A_c1)
        self.A_c2 = float(solution.A_c2)
        self.risk_prices = pd.Series(
            {
                "eta": float(solution.Lambda_eta),
                "eps": float(solution.Lambda_eps),
                "w": float(solution.Lambda_w),
            }
        )
        self.A1 = _series(solution.A1, self.claims)
        self.A2 = _series(solution.A2, self.claims)
        # The engine returns decimals; results are in percent throughout.
        self.long_run_premium = _series(solution.premium_lr, self.claims) * 100.0
        self.mean_log_pd = _series(solution.mean_log_pd, self.claims)

        growth, gordon = {}, {}
        for name, d in self.params.dividends.items():
            g_eff, gordon_r = _gordon_pieces(
                d, self.params.cons, solution.mean_log_pd[name]
            )
            growth[name] = g_eff * 100.0
            gordon[name] = gordon_r * 100.0
        self.expected_growth = _series(growth, self.claims)
        self.gordon_return = _series(gordon, self.claims)

        self.value_premium = self._spread(self.long_run_premium)

    @property
    def long_short_premium(self) -> float:
        """Alias of :attr:`value_premium` for non-paper leg names."""
        return self.value_premium

    @property
    def Lambda_eta(self) -> float:
        """Price of the short-run consumption shock."""
        return float(self.risk_prices["eta"])

    @property
    def Lambda_eps(self) -> float:
        """Price of the long-run (expected-growth) shock."""
        return float(self.risk_prices["eps"])

    @property
    def Lambda_w(self) -> float:
        """Price of the volatility shock."""
        return float(self.risk_prices["w"])

    def to_frame(self):
        """Loadings and premia by claim, one row per claim."""
        out = pd.DataFrame(
            {
                "A1": self.A1,
                "A2": self.A2,
                "long_run_premium": self.long_run_premium,
                "mean_log_pd": self.mean_log_pd,
                "expected_growth": self.expected_growth,
                "gordon_return": self.gordon_return,
            }
        )
        out.index.name = "claim"
        return to_backend(out.reset_index())

    def summary(self) -> Summary:
        """Formatted loadings, long-run premia, and risk prices."""
        lines = self._header_lines("analytical (log-linear, Section 3.4)")
        lines.append("-" * 72)
        lines.append(
            f"{'Claim':12s} {'A1':>9s} {'A2':>11s} {'LR prem %':>10s} "
            f"{'E[g] %':>8s} {'log(P/D)':>9s}"
        )
        for name in self.claims:
            lines.append(
                f"{name:12s} {_fmt(self.A1[name], 9, 1)} "
                f"{_fmt(self.A2[name], 11, 1)} "
                f"{_fmt(self.long_run_premium[name], 10)} "
                f"{_fmt(self.expected_growth[name])} "
                f"{_fmt(self.mean_log_pd[name], 9)}"
            )
        lines.append("-" * 72)
        if np.isfinite(self.value_premium):
            lines.append(
                f"{self._premium_label()} from long-run risks  "
                f"{_fmt(self.value_premium)} %"
            )
        lines.append(
            f"Risk prices: short-run {self.Lambda_eta:.2f}, "
            f"long-run {self.Lambda_eps:.2f}, volatility {self.Lambda_w:.2f}"
        )
        lines.append("=" * 72)
        lines.append(
            "Long-run piece only, at fixed log(P/D) anchors; "
            "short-run and volatility news add more."
        )
        return Summary(lines)


class SimulationResults(LRRResults):
    """Table VII: statistics of simulated samples, not population moments.

    Each sample is ``years`` years of annual data, aggregated from
    simulated months; the reported numbers are cross-sample means, and
    the ``*_se`` attributes are cross-sample standard deviations.

    Attributes
    ----------
    expected_returns, volatility, sharpe_ratios, capm_betas : pandas.Series
        Cross-sample mean annual statistics by claim.
    expected_returns_se, volatility_se, mean_log_pd_se : pandas.Series
        Cross-sample standard deviations.
    pd_levels, mean_log_pd : pandas.Series
        Mean annual price-dividend ratio and its log.
    risk_free, risk_free_se, value_premium, beta_ratio : float
        Whole-model statistics; rates and premia in percent.
    n_samples, years, seed : int
        What was simulated.
    """

    method = "simulation"

    def __init__(self, model, table: dict, seed: int):
        super().__init__(model)
        self._table = table
        self.n_samples = int(table["n_samples"])
        self.years = int(table["years"])
        self.seed = int(seed)

        self.expected_returns = _series(table["mean_return"], self.claims)
        self.expected_returns_se = _series(table["mean_return_se"], self.claims)
        self.volatility = _series(table["volatility"], self.claims)
        self.volatility_se = _series(table["volatility_se"], self.claims)
        self.sharpe_ratios = _series(table["sharpe"], self.claims)
        self.capm_betas = _series(table["capm_beta"], self.claims)
        self.pd_levels = _series(table["mean_pd_level"], self.claims)
        self.mean_log_pd = _series(table["mean_log_pd"], self.claims)
        self.mean_log_pd_se = _series(table["mean_log_pd_se"], self.claims)

        self.risk_free = float(table["mean_rf"])
        self.risk_free_se = float(table["mean_rf_se"])
        self.value_premium = float(table["value_premium"])
        self.beta_ratio = float(table["beta_ratio"])

    @property
    def long_short_premium(self) -> float:
        """Alias of :attr:`value_premium` for non-paper leg names."""
        return self.value_premium

    def to_frame(self):
        """Simulated statistics by claim, one row per claim."""
        out = pd.DataFrame(
            {
                "expected_return": self.expected_returns,
                "expected_return_se": self.expected_returns_se,
                "volatility": self.volatility,
                "volatility_se": self.volatility_se,
                "sharpe": self.sharpe_ratios,
                "capm_beta": self.capm_betas,
                "price_dividend": self.pd_levels,
                "mean_log_pd": self.mean_log_pd,
            }
        )
        out.index.name = "claim"
        return to_backend(out.reset_index())

    def summary(self) -> Summary:
        """Formatted Table VII, beside the paper's own column when comparable."""
        paper = _PAPER_TABLE_VII if self._is_paper_calibration else None
        lines = self._header_lines(
            f"simulation ({self.n_samples} samples x {self.years} years, seed {self.seed})"
        )
        lines.append("-" * 72)
        header = (
            f"{'Claim':10s} {'E[R] %':>8s} {'(SD)':>7s} {'Vol %':>8s} "
            f"{'Sharpe':>7s} {'beta':>6s} {'P/D':>7s} {'log P/D':>8s}"
        )
        if paper:
            header += f" {'Paper E[R]':>11s}"
        lines.append(header)
        for name in self.claims:
            row = (
                f"{name:10s} {_fmt(self.expected_returns[name])} "
                f"{_fmt(self.expected_returns_se[name], 7)} "
                f"{_fmt(self.volatility[name])} "
                f"{_fmt(self.sharpe_ratios[name], 7)} "
                f"{_fmt(self.capm_betas[name], 6)} "
                f"{_fmt(self.pd_levels[name], 7, 1)} "
                f"{_fmt(self.mean_log_pd[name], 8)}"
            )
            if paper:
                row += f" {_fmt(paper['mean_return'].get(name, np.nan), 11)}"
            lines.append(row)
        lines.append("-" * 72)
        lines.append(
            f"Risk-free rate                {_fmt(self.risk_free)} %  "
            f"(SD {self.risk_free_se:.2f})"
        )
        lines.append(f"{self._premium_label():29s} {_fmt(self.value_premium)} %")
        beta_label = f"CAPM beta ratio ({self.legs.long}/{self.legs.short})"
        lines.append(f"{beta_label:29s} {self.beta_ratio:8.2f}")
        lines.append("=" * 72)
        if paper:
            lines.append(
                f"Paper column: Kiku (2006), Table VII "
                f"(premium {paper['value_premium']:.2f} %, "
                f"rf {paper['mean_rf']:.2f} %, "
                f"beta ratio {paper['beta_ratio']:.2f})."
            )
        return Summary(lines)
