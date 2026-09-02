"""Shared model and results protocol for general-equilibrium families.

A model is a specification. Solving and simulating never mutate it.
Each family (long-run risks now; others later) subclasses
:class:`AssetPricingModel` and :class:`AssetPricingResults`.
"""
from __future__ import annotations

import html
from abc import ABC, abstractmethod
from typing import Iterable

import numpy as np
import pandas as pd

from ._backend import to_backend


def _fmt(value: float, width: int = 8, decimals: int = 2) -> str:
    """Right-aligned fixed-point number, or a dash when undefined."""
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return "-".rjust(width)
    return f"{value:{width}.{decimals}f}"


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


class AssetPricingModel(ABC):
    """Immutable specification of a general-equilibrium asset pricing model.

    Solving and simulating return results objects; they do not change
    the model. To vary a parameter, call :meth:`replace` or construct
    another model.
    """

    @property
    @abstractmethod
    def claims(self) -> tuple[str, ...]:
        """Names of the claims this model prices, in order."""

    @abstractmethod
    def solve(self, method: str = "grid", **kwargs) -> "AssetPricingResults":
        """Solve the model and return results."""

    def simulate(self, **kwargs) -> "AssetPricingResults":
        """Simulate samples from the solved model.

        Families that have no simulation step leave this default in
        place; it raises :class:`NotImplementedError`.
        """
        raise NotImplementedError(
            f"{type(self).__name__} does not implement simulate()"
        )

    @abstractmethod
    def replace(self, **kwargs) -> "AssetPricingModel":
        """A new model with some constructor arguments changed."""


class AssetPricingResults(ABC):
    """Shared surface of every results object.

    Attributes
    ----------
    model : AssetPricingModel
        The model these results came from.
    method : str
        How the results were produced.
    claims : tuple of str
        The claim names, in the order the model prices them.
    """

    method = "base"

    #: (attribute holding the headline per-claim measure, its prose name)
    _premium_field = ("expected_returns", "expected return")

    def __init__(self, model: AssetPricingModel):
        self.model = model
        self.claims: tuple[str, ...] = tuple(model.claims)

    def _check_claim(self, role: str, name: str) -> None:
        if name not in self.claims:
            raise KeyError(
                f"{role}={name!r} is not among the claims {list(self.claims)}."
            )

    def compare(
        self, long: str, short: str, *, market: str | None = None
    ) -> "Comparison":
        """Set two priced claims side by side.

        Parameters
        ----------
        long, short : str
            The two claims to compare. The premium is long minus short.
        market : str, optional
            The claim to measure CAPM betas against. Only betas need it.

        Returns
        -------
        Comparison
        """
        return Comparison(self, long, short, market=market)

    @abstractmethod
    def summary(self) -> Summary:
        """Formatted text summary of the results."""

    @abstractmethod
    def to_frame(self):
        """The results as a tidy frame."""

    def __repr__(self) -> str:
        return (
            f"<{type(self).__name__} method={self.method!r} "
            f"claims={list(self.claims)}>"
        )


class Comparison:
    """A pairwise comparison of two priced claims.

    Built by :meth:`AssetPricingResults.compare`, never constructed
    directly. The model prices a set of claims; which two of them form a
    spread is a question asked afterwards, and this is the answer.

    Optional LRR attributes (``mean_log_pd``, ``volatility``,
    ``capm_betas``) become NaN when a family does not provide them.
    """

    def __init__(
        self,
        results: AssetPricingResults,
        long: str,
        short: str,
        *,
        market: str | None = None,
    ):
        results._check_claim("long", long)
        results._check_claim("short", short)
        if market is not None:
            results._check_claim("market", market)
        if long == short:
            raise ValueError(
                f"compare needs two different claims; both legs are {long!r}."
            )

        self.results = results
        self.long = long
        self.short = short
        self.market = market

        field, measure = results._premium_field
        values = getattr(results, field)
        self.premium = float(values[long] - values[short])
        self.premium_measure = measure

        mean_log_pd = getattr(results, "mean_log_pd", None)
        self.log_pd_spread = (
            float(mean_log_pd[long] - mean_log_pd[short])
            if mean_log_pd is not None
            else float("nan")
        )

        vol = getattr(results, "volatility", None)
        self.volatility_spread = (
            float(vol[long] - vol[short]) if vol is not None else float("nan")
        )

        if market is not None and hasattr(results, "capm_betas"):
            self.betas = results.capm_betas(market)[[long, short]]
            ratio = getattr(results, "_beta_ratio", None)
            self.beta_ratio = (
                float(ratio(long, short, market))
                if callable(ratio)
                else float("nan")
            )
        else:
            self.betas = pd.Series(
                [np.nan, np.nan], index=[long, short], dtype=float
            )
            self.beta_ratio = float("nan")

    @property
    def label(self) -> str:
        """How a value/growth pair would be named; else a generic spread."""
        paper_pair = {self.long, self.short} <= {"value", "growth"}
        return "Value premium" if paper_pair else "Long-short premium"

    def to_frame(self):
        """The comparison as one tidy row, for stacking across a sweep."""
        out = pd.DataFrame([{
            "long": self.long,
            "short": self.short,
            "market": self.market,
            "premium": self.premium,
            "log_pd_spread": self.log_pd_spread,
            "volatility_spread": self.volatility_spread,
            "beta_long": float(self.betas[self.long]),
            "beta_short": float(self.betas[self.short]),
            "beta_ratio": self.beta_ratio,
        }])
        return to_backend(out)

    def summary(self) -> Summary:
        """The two legs and the spreads between them."""
        res = self.results
        header = getattr(res, "_header_lines", None)
        subtitle = getattr(res, "_subtitle", None)
        if callable(header) and callable(subtitle):
            lines = header(subtitle())
        else:
            lines = [
                "=" * 72,
                type(res).__name__.center(72),
                "=" * 72,
                f"Claims:       {', '.join(res.claims)}",
            ]
        market = f"   market = {self.market}" if self.market else ""
        lines.append(
            f"Comparison:   long = {self.long}   short = {self.short}{market}"
        )
        lines.append("-" * 72)
        lines.append(
            f"{'Leg':6s} {'Claim':14s} {'E[R] %':>9s} {'Vol %':>8s} "
            f"{'CAPM b':>8s} {'log(P/D)':>9s}"
        )
        values = getattr(res, res._premium_field[0])
        vol = getattr(res, "volatility", None)
        mean_log_pd = getattr(res, "mean_log_pd", None)
        for role, name in (("long", self.long), ("short", self.short)):
            log_pd = (
                mean_log_pd[name] if mean_log_pd is not None else float("nan")
            )
            lines.append(
                f"{role:6s} {name:14s} {_fmt(values[name], 9)} "
                f"{_fmt(vol[name] if vol is not None else np.nan)} "
                f"{_fmt(self.betas[name])} "
                f"{_fmt(log_pd, 9)}"
            )
        lines.append("-" * 72)
        label = f"{self.label} ({self.premium_measure})"
        lines.append(f"{label:38s} {_fmt(self.premium)} %")
        lines.append(
            f"{'log(P/D) spread (' + self.long + ' - ' + self.short + ')':38s} "
            f"{_fmt(self.log_pd_spread)}"
        )
        if np.isfinite(self.beta_ratio):
            ratio_label = f"CAPM beta ratio ({self.long}/{self.short})"
            lines.append(f"{ratio_label:38s} {_fmt(self.beta_ratio)}")
        lines.append("=" * 72)
        if (
            getattr(res, "_is_paper_calibration", False)
            and (self.long, self.short) == ("value", "growth")
        ):
            paper = getattr(res, "_paper_table_vii", None)
            if paper:
                lines.append(
                    f"Kiku (2006), Table VII: premium {paper['value_premium']:.2f} %, "
                    f"beta ratio {paper['beta_ratio']:.2f}."
                )
        return Summary(lines)

    def __repr__(self) -> str:
        return (
            f"<Comparison long={self.long!r} short={self.short!r} "
            f"premium={self.premium:.2f}>"
        )
