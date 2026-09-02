"""Results of solving and simulating a :class:`~geap.LongRunRisksModel`.

Every solve or simulation returns one of these objects. They hold the
numbers as attributes, print a formatted table through :meth:`summary`,
and hand back a tidy frame through :meth:`to_frame`.

They describe **claims**, never roles. A model prices a set of named
claims; which two of them form a spread, and which one stands in for the
market, are questions you ask afterwards through
:meth:`~geap.base.AssetPricingResults.compare`.

Conventions
-----------
Returns, premia, volatilities, and the risk-free rate are annualized and
in percent. Log price-dividend ratios are in logs. Quantities that vary
by claim are ``pandas.Series`` indexed by claim name; quantities that
describe the whole model are floats.
"""
from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd

from .._backend import to_backend
from ..base import AssetPricingResults, Summary, _fmt
from .analytical import AnalyticalSolution, _gordon_pieces
from .params import ModelParams

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

# Floor on a reference claim's return variance, so a degenerate claim
# cannot divide a beta by zero. Carried over from the pre-0.7.0 moments.
_VAR_FLOOR = 1e-12


def _series(values: Mapping[str, float], claims) -> pd.Series:
    """A float Series over ``claims``, NaN where a claim has no value."""
    claims = list(claims)
    return pd.Series(
        [float(values.get(name, np.nan)) for name in claims],
        index=claims,
        dtype=float,
    )


class LRRResults(AssetPricingResults):
    """Long-run-risks results: Table II params and LRR-specific headers."""

    _paper_table_vii = _PAPER_TABLE_VII

    def __init__(self, model):
        super().__init__(model)
        self.params: ModelParams = model.params

    @property
    def _is_paper_calibration(self) -> bool:
        """True for the untouched Table II calibration."""
        return self.params == ModelParams()

    def _header_lines(self, subtitle: str) -> list[str]:
        p = self.params.prefs
        return [
            "=" * 72,
            "Long-Run Risks Model Results".center(72),
            "=" * 72,
            "Model:        Kiku (2006) general equilibrium",
            f"Method:       {subtitle}",
            f"Preferences:  delta = {p.delta:g}   gamma = {p.gamma:g}   "
            f"psi = {p.psi:g}   theta = {p.theta:.1f}",
            f"Claims:       {', '.join(self.claims)}",
        ]

    def _beta_ratio(self, long: str, short: str, market: str) -> float:
        """Beta of the long leg over beta of the short leg."""
        return float("nan")


class GridResults(LRRResults):
    """Population moments from the quadrature (Tauchen-Hussey) solution.

    Moments are computed state by state and averaged under the stationary
    distribution of the discretized economy, then annualized.

    Attributes
    ----------
    expected_returns, volatility, sharpe_ratios : pandas.Series
        Annualized return moments by claim, in percent.
    mean_log_pd, price_dividend : pandas.Series
        Mean log price-dividend ratio and its level, by claim.
    risk_free : float
        Annualized risk-free rate, in percent. It follows from the SDF,
        so no claim is involved.
    return_cov : pandas.DataFrame
        Pairwise covariance of monthly gross returns, claim by claim.
    beta_matrix : pandas.DataFrame
        CAPM betas: rows are the claim, columns the reference claim.
    converged : bool
        Whether every Euler fixed point converged.
    n_x, n_s : int
        Grid size for expected growth and variance.
    z_c, z, stationary, x_nodes, s2_nodes
        The solved valuation functions and the grid behind them.
    """

    method = "grid"

    def __init__(self, model, solver):
        super().__init__(model)
        self._solver = solver
        self.n_x = solver.grid.n_x
        self.n_s = solver.grid.n_s
        self.converged = bool(solver.converged)

        from .implications.moments import population_moments

        moments = population_moments(solver)
        self._moments = moments

        self.expected_returns = _series(moments["mean_return"], self.claims)
        self.volatility = _series(moments["volatility"], self.claims)
        self.mean_log_pd = _series(moments["mean_log_pd"], self.claims)
        self.price_dividend = np.exp(self.mean_log_pd)
        self.sharpe_ratios = _series(moments["sharpe"], self.claims)
        self.risk_free = float(moments["mean_rf"])

        names = list(self.claims)
        cov = moments["covariance"]
        self.return_cov = pd.DataFrame(
            [[cov[a][b] for b in names] for a in names],
            index=names, columns=names,
        )
        self.beta_matrix = self._betas_from_cov()

    def _betas_from_cov(self) -> pd.DataFrame:
        """Betas against every reference claim: cov(a, m) / var(m)."""
        cov = self.return_cov.to_numpy()
        var = np.maximum(np.diag(cov), _VAR_FLOOR)
        betas = pd.DataFrame(
            cov / var[None, :], index=list(self.claims), columns=list(self.claims)
        )
        for name in self.claims:
            # A claim's beta on itself is one by definition, and saying so
            # keeps the variance floor from showing through on a degenerate
            # claim.
            betas.loc[name, name] = 1.0
        return betas

    def capm_betas(self, market: str) -> pd.Series:
        """CAPM betas of every claim against ``market``.

        Examples
        --------
        ```python
        res.capm_betas("market")["value"]
        ```
        """
        self._check_claim("market", market)
        return self.beta_matrix[market].rename(f"beta_vs_{market}")

    def _beta_ratio(self, long: str, short: str, market: str) -> float:
        b = self.capm_betas(market)
        return float(b[long] / b[short])

    def _subtitle(self) -> str:
        return f"grid ({self.n_x} x {self.n_s} states)"

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
        """Moments by claim, one row per claim.

        Betas need a reference claim, so they are not here; join them on
        with ``res.capm_betas("market")`` when you want them.
        """
        out = pd.DataFrame(
            {
                "expected_return": self.expected_returns,
                "volatility": self.volatility,
                "sharpe": self.sharpe_ratios,
                "mean_log_pd": self.mean_log_pd,
                "price_dividend": self.price_dividend,
            }
        )
        out.index.name = "claim"
        return to_backend(out.reset_index())

    def summary(self) -> Summary:
        """Formatted population moments, in the style of Tables VII-VIII."""
        lines = self._header_lines(self._subtitle())
        lines.append(f"Converged:    {self.converged}")
        lines.append("-" * 72)
        lines.append(
            f"{'Claim':12s} {'E[R] %':>8s} {'Vol %':>8s} {'Sharpe':>8s} "
            f"{'log(P/D)':>9s} {'P/D':>8s}"
        )
        for name in self.claims:
            lines.append(
                f"{name:12s} {_fmt(self.expected_returns[name])} "
                f"{_fmt(self.volatility[name])} {_fmt(self.sharpe_ratios[name])} "
                f"{_fmt(self.mean_log_pd[name], 9)} "
                f"{_fmt(self.price_dividend[name], 8, 1)}"
            )
        lines.append("-" * 72)
        lines.append(f"Risk-free rate                {_fmt(self.risk_free)} %")
        lines.append("=" * 72)
        lines.append(
            "Population moments under the stationary distribution, annualized."
        )
        lines.append(
            "Compare two claims with .compare(long=..., short=...)."
        )
        return Summary(lines)


class AnalyticalResults(LRRResults):
    """Loadings and risk prices from the log-linear solution (Section 3.4).

    The approximation prices each claim around a fixed linearization
    point for its log P/D, so ``mean_log_pd`` here is that anchor, not a
    solved level. ``long_run_premium`` is the compensation for
    expected-growth news only; short-run and volatility news add more.

    There is no return distribution in this solution, so it carries no
    volatilities and no betas.

    Attributes
    ----------
    A1, A2 : pandas.Series
        Price-dividend elasticities to expected growth and to volatility.
    long_run_premium : pandas.Series
        Annualized long-run risk premium by claim, in percent.
    expected_growth, gordon_return : pandas.Series
        Annualized expected cash-flow growth including convexity, and the
        Gordon return at the anchor, in percent.
    risk_prices : pandas.Series
        Prices of the short-run, long-run, and volatility shocks.
    """

    method = "analytical"
    _premium_field = ("long_run_premium", "long-run risk premium")

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
        for name, d in self.params.claims.items():
            g_eff, gordon_r = _gordon_pieces(
                d, self.params.cons, solution.mean_log_pd[name]
            )
            growth[name] = g_eff * 100.0
            gordon[name] = gordon_r * 100.0
        self.expected_growth = _series(growth, self.claims)
        self.gordon_return = _series(gordon, self.claims)

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

    def _subtitle(self) -> str:
        return "analytical (log-linear, Section 3.4)"

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
        lines = self._header_lines(self._subtitle())
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
        lines.append(
            f"Risk prices: short-run {self.Lambda_eta:.2f}, "
            f"long-run {self.Lambda_eps:.2f}, volatility {self.Lambda_w:.2f}"
        )
        lines.append("=" * 72)
        lines.append(
            "Long-run piece only, at fixed log(P/D) anchors; "
            "short-run and volatility news add more."
        )
        lines.append(
            "Compare two claims with .compare(long=..., short=...)."
        )
        return Summary(lines)


class SimulationResults(LRRResults):
    """Table VII: statistics of simulated samples, not population moments.

    Each sample is ``years`` years of annual data, aggregated from
    simulated months; the reported numbers are cross-sample means, and
    the ``*_se`` attributes are cross-sample standard deviations.

    Attributes
    ----------
    expected_returns, volatility, sharpe_ratios : pandas.Series
        Cross-sample mean annual statistics by claim.
    expected_returns_se, volatility_se, mean_log_pd_se : pandas.Series
        Cross-sample standard deviations.
    pd_levels, mean_log_pd : pandas.Series
        Mean annual price-dividend ratio and its log.
    risk_free, risk_free_se : float
        The rate and its cross-sample dispersion, in percent.
    beta_matrix : pandas.DataFrame
        Cross-sample mean CAPM betas: rows the claim, columns the
        reference claim.
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
        self.pd_levels = _series(table["mean_pd_level"], self.claims)
        self.mean_log_pd = _series(table["mean_log_pd"], self.claims)
        self.mean_log_pd_se = _series(table["mean_log_pd_se"], self.claims)

        self.risk_free = float(table["mean_rf"])
        self.risk_free_se = float(table["mean_rf_se"])

        names = list(self.claims)
        self._beta_samples = table["beta_samples"]
        matrix = table["beta_matrix"]
        self.beta_matrix = pd.DataFrame(
            [[matrix[a][b] for b in names] for a in names],
            index=names, columns=names,
        )

    def capm_betas(self, market: str) -> pd.Series:
        """Cross-sample mean CAPM betas of every claim against ``market``."""
        self._check_claim("market", market)
        return self.beta_matrix[market].rename(f"beta_vs_{market}")

    def _beta_ratio(self, long: str, short: str, market: str) -> float:
        """Cross-sample mean of the per-sample beta ratio.

        This is the paper's object, and it is not the ratio of the mean
        betas: the mean of a ratio and the ratio of means differ, by
        about a hundredth here.
        """
        samples = self._beta_samples
        return float(np.mean(samples[long][market] / samples[short][market]))

    def _subtitle(self) -> str:
        return (
            f"simulation ({self.n_samples} samples x {self.years} years, "
            f"seed {self.seed})"
        )

    def to_frame(self):
        """Simulated statistics by claim, one row per claim."""
        out = pd.DataFrame(
            {
                "expected_return": self.expected_returns,
                "expected_return_se": self.expected_returns_se,
                "volatility": self.volatility,
                "volatility_se": self.volatility_se,
                "sharpe": self.sharpe_ratios,
                "price_dividend": self.pd_levels,
                "mean_log_pd": self.mean_log_pd,
            }
        )
        out.index.name = "claim"
        return to_backend(out.reset_index())

    def summary(self) -> Summary:
        """Formatted Table VII, beside the paper's own column when comparable."""
        paper = _PAPER_TABLE_VII if self._is_paper_calibration else None
        lines = self._header_lines(self._subtitle())
        lines.append("-" * 72)
        header = (
            f"{'Claim':10s} {'E[R] %':>8s} {'(SD)':>7s} {'Vol %':>8s} "
            f"{'Sharpe':>7s} {'P/D':>7s} {'log P/D':>8s}"
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
        lines.append("=" * 72)
        if paper:
            lines.append(
                f"Paper column: Kiku (2006), Table VII "
                f"(premium {paper['value_premium']:.2f} %, "
                f"rf {paper['mean_rf']:.2f} %, "
                f"beta ratio {paper['beta_ratio']:.2f})."
            )
        lines.append(
            "Compare two claims with .compare(long=..., short=..., market=...)."
        )
        return Summary(lines)
