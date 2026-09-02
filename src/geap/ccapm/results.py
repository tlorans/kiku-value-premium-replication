"""Results of solving or simulating a :class:`~geap.PowerUtilityModel`."""
from __future__ import annotations

from typing import Mapping

import numpy as np
import pandas as pd

from .._backend import to_backend
from ..base import AssetPricingResults, Summary, _fmt


def _series(values: Mapping[str, float], claims) -> pd.Series:
    claims = list(claims)
    return pd.Series(
        [float(values.get(name, np.nan)) for name in claims],
        index=claims,
        dtype=float,
    )


class PowerUtilityResults(AssetPricingResults):
    """Unconditional moments of the two-state economy, in percent."""

    method = "grid"

    def __init__(
        self,
        model,
        expected_returns: Mapping[str, float],
        volatility: Mapping[str, float] | None = None,
        mean_log_pd: Mapping[str, float] | None = None,
        *,
        n_samples: int | None = None,
        years: int | None = None,
        seed: int | None = None,
    ):
        super().__init__(model)
        self.expected_returns = _series(expected_returns, self.claims)
        self.volatility = (
            _series(volatility, self.claims) if volatility is not None else None
        )
        self.mean_log_pd = (
            _series(mean_log_pd, self.claims) if mean_log_pd is not None else None
        )
        self.risk_free = float(self.expected_returns["bill"])
        self.n_samples = n_samples
        self.years = years
        self.seed = seed
        if n_samples is not None:
            self.method = "simulation"

    def _subtitle(self) -> str:
        if self.method == "simulation":
            return (
                f"simulation ({self.n_samples} samples x {self.years} years, "
                f"seed {self.seed})"
            )
        return "two-state Markov chain (Mehra and Prescott 1985)"

    def _header_lines(self, subtitle: str) -> list[str]:
        return [
            "=" * 72,
            "Power Utility Model Results".center(72),
            "=" * 72,
            "Model:        Mehra and Prescott (1985) two-state CCAPM",
            f"Method:       {subtitle}",
            f"Preferences:  delta = {self.model.delta:g}   "
            f"gamma = {self.model.gamma:g}",
            f"Claims:       {', '.join(self.claims)}",
        ]

    def to_frame(self):
        out = pd.DataFrame({"expected_return": self.expected_returns})
        if self.volatility is not None:
            out["volatility"] = self.volatility
        if self.mean_log_pd is not None:
            out["mean_log_pd"] = self.mean_log_pd
        out.index.name = "claim"
        return to_backend(out.reset_index())

    def summary(self) -> Summary:
        lines = self._header_lines(self._subtitle())
        lines.append("-" * 72)
        lines.append(
            f"{'Claim':12s} {'E[R] %':>8s} {'Vol %':>8s} {'log(P/D)':>9s}"
        )
        vol = self.volatility
        pd_ = self.mean_log_pd
        for name in self.claims:
            lines.append(
                f"{name:12s} {_fmt(self.expected_returns[name])} "
                f"{_fmt(vol[name] if vol is not None else np.nan)} "
                f"{_fmt(pd_[name] if pd_ is not None else np.nan, 9)}"
            )
        lines.append("-" * 72)
        prem = self.compare("equity", "bill").premium
        lines.append(f"Equity premium                 {_fmt(prem)} %")
        lines.append("=" * 72)
        lines.append(
            "Unconditional means under the stationary distribution, annual."
        )
        return Summary(lines)
