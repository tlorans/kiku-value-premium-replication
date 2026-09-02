"""Results of a GMM estimation."""
from __future__ import annotations

from typing import Iterable

import numpy as np
import pandas as pd

from .._backend import to_backend
from ..base import Summary


def _fmt(value: float | None, width: int = 12, decimals: int = 4) -> str:
    if value is None or (isinstance(value, float) and not np.isfinite(value)):
        return "-".rjust(width)
    return f"{value:{width}.{decimals}f}"


class GMMResults:
    """Hansen GMM fit: parameters, pricing errors, and optional inference.

    This is an estimator result, not an :class:`~geap.base.AssetPricingResults`.
    """

    def __init__(
        self,
        theta: np.ndarray,
        g: np.ndarray,
        W: np.ndarray,
        *,
        objective: float,
        nobs: int | None,
        names: Iterable[str],
        steps: int,
        cov: np.ndarray | None = None,
        se: np.ndarray | None = None,
        S: np.ndarray | None = None,
        J: float | None = None,
        J_df: int = 0,
        J_pvalue: float | None = None,
    ):
        self.theta = np.asarray(theta, dtype=float).ravel()
        self.g = np.asarray(g, dtype=float).ravel()
        self.W = np.asarray(W, dtype=float)
        self.objective = float(objective)
        self.nobs = None if nobs is None else int(nobs)
        self.names = tuple(names)
        self.n_params = int(self.theta.size)
        self.n_moments = int(self.g.size)
        self.steps = int(steps)
        self.cov = None if cov is None else np.asarray(cov, dtype=float)
        self.se = None if se is None else np.asarray(se, dtype=float).ravel()
        self.S = None if S is None else np.asarray(S, dtype=float)
        self.J = None if J is None else float(J)
        self.J_df = int(J_df)
        self.J_pvalue = None if J_pvalue is None else float(J_pvalue)

    def to_frame(self):
        se = (
            self.se
            if self.se is not None
            else np.full(self.n_params, np.nan)
        )
        out = pd.DataFrame(
            {
                "parameter": list(self.names),
                "theta": self.theta,
                "se": se,
            }
        )
        return to_backend(out)

    def summary(self) -> Summary:
        nobs = "—" if self.nobs is None else str(self.nobs)
        lines = [
            "=" * 72,
            "GMM Results".center(72),
            "=" * 72,
            f"Moments:      {self.n_moments:<6d} Parameters: {self.n_params:<6d} "
            f"Observations: {nobs}",
            f"Steps:        {self.steps}",
            "-" * 72,
            f"{'Parameter':16s} {'Estimate':>12s} {'SE':>12s}",
        ]
        for i, name in enumerate(self.names):
            se = None if self.se is None else float(self.se[i])
            lines.append(f"{name:16s} {_fmt(float(self.theta[i]))} {_fmt(se)}")
        lines.append("-" * 72)
        lines.append("Pricing errors")
        for i, gi in enumerate(self.g):
            lines.append(f"  g[{i}]{'':10s} {_fmt(float(gi))}")
        obj_label = "Objective g'Wg"
        lines.append(f"{obj_label:28s} {_fmt(self.objective)}")
        if self.J_pvalue is not None and self.J is not None:
            lines.append(
                f"{'J-test':28s} {_fmt(self.J)}   df = {self.J_df}   "
                f"p = {self.J_pvalue:.4f}"
            )
        elif self.n_moments > self.n_params:
            lines.append(
                "J-test                       —   (chi-square requires two-step W)"
            )
        lines.append("=" * 72)
        return Summary(lines)

    def __repr__(self) -> str:
        vals = ", ".join(
            f"{n}={v:.4g}" for n, v in zip(self.names, self.theta)
        )
        return f"<GMMResults {vals}>"
