"""The model object: specify a calibration, solve it, simulate it.

One class carries the whole workflow::

    import lrrcs as lrr

    model = lrr.LongRunRisksModel()      # Table II calibration
    res = model.solve()                  # quadrature solution
    res.summary()                        # formatted moments
    res.value_premium                    # 5.18

    sim = model.simulate(n_samples=1000, years=74, seed=0)
    sim.summary()                        # Table VII

A model is a specification, not a workspace: solving and simulating
never change its parameters. To vary a parameter, build another model
with :meth:`LongRunRisksModel.replace` or pass overrides to the
constructor.
"""
from __future__ import annotations

from dataclasses import replace as _replace
from typing import Mapping

import numpy as np

from .model.analytical import solve_analytical
from .model.legs import Legs, resolve_legs
from .model.params import (
    ConsumptionParams,
    DividendParams,
    ModelParams,
    PreferencesParams,
)
from .model.solver import ModelSolver
from .results import AnalyticalResults, GridResults, SimulationResults

_PREFERENCE_FIELDS = ("delta", "gamma", "psi")
_CONSUMPTION_FIELDS = ("mu", "rho", "phi_x", "sigma", "nu", "sigma_w")
_DIVIDEND_FIELDS = ("mu", "phi", "phi_sigma", "alpha")


def _as_dividend(value, base: DividendParams | None, name: str) -> DividendParams:
    """Coerce a claim specification to ``DividendParams``.

    A ``DividendParams`` replaces outright. A mapping replaces when it
    gives all four fields and merges onto ``base`` when it gives some,
    which is what makes one-parameter counterfactuals a one-liner.
    """
    if isinstance(value, DividendParams):
        return value
    if not isinstance(value, Mapping):
        raise TypeError(
            f"Claim {name!r} must be a DividendParams or a mapping of "
            f"{list(_DIVIDEND_FIELDS)}, got {type(value).__name__}."
        )
    unknown = set(value) - set(_DIVIDEND_FIELDS)
    if unknown:
        raise TypeError(
            f"Claim {name!r} got unknown field(s) {sorted(unknown)}; "
            f"expected any of {list(_DIVIDEND_FIELDS)}."
        )
    if base is None:
        missing = set(_DIVIDEND_FIELDS) - set(value)
        if missing:
            raise TypeError(
                f"New claim {name!r} needs all of {list(_DIVIDEND_FIELDS)}; "
                f"missing {sorted(missing)}."
            )
        return DividendParams(**value)
    return _replace(base, **value)


class LongRunRisksModel:
    """Kiku (2006) long-run risks general-equilibrium model.

    Parameters
    ----------
    params : ModelParams, optional
        Complete parameterisation. Defaults to the Table II calibration.
        The object passed in is never modified.
    delta, gamma, psi : float, optional
        Epstein-Zin preference overrides.
    mu, rho, phi_x, sigma, nu, sigma_w : float, optional
        Consumption-process overrides.
    claims : mapping, optional
        Dividend claims to price, as ``DividendParams`` or as mappings of
        ``mu``, ``phi``, ``phi_sigma``, ``alpha``. A mapping that gives
        only some fields merges onto the claim already there, so
        ``claims={"value": {"phi": 2.6}}`` changes one number and leaves
        the rest of the calibration alone.
    long, short, market : str, optional
        Which claim plays each role. By default ``value`` or ``long`` is
        the long leg, ``growth`` or ``short`` the short leg, and
        ``market`` the market.
    residual_corr : mapping, optional
        Correlations of orthogonalised dividend residuals, keyed by pairs
        of claim names: ``{("high", "low"): 0.2}``. Needed only for
        claims outside the paper's three portfolios, which correlate at
        zero without it.

    Attributes
    ----------
    params : ModelParams
        The assembled parameterisation.
    legs : Legs
        The resolved long, short, and market claim names.

    Examples
    --------
    ```python
    import lrrcs as lrr

    model = lrr.LongRunRisksModel()
    print(model.solve().summary())

    # risk aversion of 7.5 instead of 10
    lrr.LongRunRisksModel(gamma=7.5).solve().value_premium

    # give value the same long-run leverage as growth
    lrr.LongRunRisksModel(claims={"value": {"phi": 2.6}}).solve().value_premium
    ```
    """

    def __init__(
        self,
        params: ModelParams | None = None,
        *,
        delta: float | None = None,
        gamma: float | None = None,
        psi: float | None = None,
        mu: float | None = None,
        rho: float | None = None,
        phi_x: float | None = None,
        sigma: float | None = None,
        nu: float | None = None,
        sigma_w: float | None = None,
        claims: Mapping | None = None,
        long: str | None = None,
        short: str | None = None,
        market: str | None = None,
        residual_corr: Mapping | None = None,
    ):
        base = params if params is not None else ModelParams()

        prefs_over = {
            k: v
            for k, v in (("delta", delta), ("gamma", gamma), ("psi", psi))
            if v is not None
        }
        cons_over = {
            k: v
            for k, v in (
                ("mu", mu),
                ("rho", rho),
                ("phi_x", phi_x),
                ("sigma", sigma),
                ("nu", nu),
                ("sigma_w", sigma_w),
            )
            if v is not None
        }

        dividends = dict(base.dividends)
        if claims is not None:
            if not claims:
                raise ValueError("claims is empty; a model needs at least one claim.")
            replacing_all = set(claims) - set(dividends)
            if replacing_all:
                # Naming any claim the base does not have means the caller is
                # describing their own cross-section, not tweaking the paper's.
                dividends = {
                    name: _as_dividend(spec, None, name)
                    for name, spec in claims.items()
                }
            else:
                for name, spec in claims.items():
                    dividends[name] = _as_dividend(spec, dividends[name], name)

        self.params = ModelParams(
            prefs=_replace(base.prefs, **prefs_over),
            cons=_replace(base.cons, **cons_over),
            dividends=dividends,
            residual_corr_gv=base.residual_corr_gv,
            residual_corr_gm=base.residual_corr_gm,
            residual_corr_vm=base.residual_corr_vm,
            residual_corr=(
                dict(residual_corr)
                if residual_corr is not None
                else (dict(base.residual_corr) if base.residual_corr else None)
            ),
        )

        if len(self.params.dividends) == 1:
            # A single claim has no cross-section: it is its own long leg.
            only = next(iter(self.params.dividends))
            self.legs = Legs(long=only, short=only, market=market)
        else:
            self.legs = Legs(
                *resolve_legs(
                    self.params.dividends, long=long, short=short, market=market
                )
            )

        self._kwargs = {
            "delta": delta,
            "gamma": gamma,
            "psi": psi,
            "mu": mu,
            "rho": rho,
            "phi_x": phi_x,
            "sigma": sigma,
            "nu": nu,
            "sigma_w": sigma_w,
            "long": long,
            "short": short,
            "market": market,
        }
        self._solved: dict[tuple, ModelSolver] = {}

    # -- alternative constructors ---------------------------------------
    @classmethod
    def from_loading(
        cls,
        phi: float,
        *,
        mu: float = 0.0015,
        phi_sigma: float = 7.5,
        alpha: float = 0.5,
        name: str = "claim",
        params: ModelParams | None = None,
        **overrides,
    ) -> "LongRunRisksModel":
        """Price one synthetic claim from its cash-flow loading on x_t.

        The loading is measured from cash flows, never from returns; see
        :func:`lrrcs.estimate_long_run_leverage`. With a single claim
        there is no market, so market betas are undefined and the
        analytical method is the natural one to use.

        Examples
        --------
        ```python
        import lrrcs as lrr
        res = lrr.LongRunRisksModel.from_loading(1.5).solve(method="analytical")
        res.A1["claim"], res.long_run_premium["claim"]
        ```
        """
        claim = DividendParams(mu=mu, phi=phi, phi_sigma=phi_sigma, alpha=alpha)
        base = params if params is not None else ModelParams()
        stripped = ModelParams(
            prefs=base.prefs,
            cons=base.cons,
            dividends={name: claim},
        )
        return cls(stripped, **overrides)

    @classmethod
    def from_cashflows(
        cls,
        dc,
        claims: Mapping | None = None,
        *,
        long=None,
        short=None,
        market=None,
        frequency: str = "annual",
        window: int = 2,
        default_phi_sigma: float = 7.5,
        params: ModelParams | None = None,
        **overrides,
    ) -> "LongRunRisksModel":
        """Calibrate the dividend claims from consumption and dividend growth.

        Returns never enter the calibration, which is the paper's
        identification discipline: only ``dc`` and the dividend growth
        series are used.

        Parameters
        ----------
        dc : array-like
            Consumption growth.
        claims : mapping of str to array-like, optional
            Dividend growth by claim name, when you want your own names.
        long, short, market : array-like or str, optional
            A growth series names that leg and calibrates it, so
            ``long=dd_value`` produces a claim called ``long``. A string
            instead picks which of ``claims`` plays the role, the same
            way it does on the constructor.

        Examples
        --------
        ```python
        import lrrcs as lrr

        # the paper's three legs, named by role
        model = lrr.LongRunRisksModel.from_cashflows(
            dc, long=dd_value, short=dd_growth, market=dd_market
        )

        # your own names, with the roles named too
        model = lrr.LongRunRisksModel.from_cashflows(
            dc,
            claims={"quality": dd_q, "junk": dd_j, "market": dd_m},
            long="quality", short="junk",
        )
        print(model.solve().summary())
        ```
        """
        from .calibration.from_data import calibrate_from_data

        def role(value):
            """A role is either a claim name or a growth series."""
            if value is None or isinstance(value, str):
                return None, value
            return value, None

        long_series, long_name = role(long)
        short_series, short_name = role(short)
        market_series, market_name = role(market)

        dividends = calibrate_from_data(
            dc,
            dict(claims) if claims else None,
            frequency=frequency,
            window=window,
            default_phi_sigma=default_phi_sigma,
            long=long_series,
            short=short_series,
            market=market_series,
        )
        base = params if params is not None else ModelParams()
        stripped = ModelParams(
            prefs=base.prefs, cons=base.cons, dividends=dividends
        )
        return cls(
            stripped,
            long=long_name,
            short=short_name,
            market=market_name,
            **overrides,
        )

    def replace(self, **kwargs) -> "LongRunRisksModel":
        """A new model with some constructor arguments changed.

        The one-liner for a sensitivity sweep::

            [model.replace(gamma=g).solve().value_premium for g in (5, 10, 15)]
        """
        merged = {k: v for k, v in self._kwargs.items() if v is not None}
        merged.update(kwargs)
        claims = merged.pop("claims", None)
        return type(self)(self.params, claims=claims, **merged)

    # -- solving ---------------------------------------------------------
    def _grid_solver(self, n_x: int, n_s: int, max_iter: int, tol: float) -> ModelSolver:
        """Solve on the grid, reusing an identical earlier solve."""
        key = (n_x, n_s, max_iter, tol)
        if key not in self._solved:
            solver = ModelSolver(self.params, n_x=n_x, n_s=n_s)
            solver.solve(max_iter=max_iter, tol=tol)
            self._solved[key] = solver
        return self._solved[key]

    def solve(
        self,
        method: str = "grid",
        *,
        n_x: int = 30,
        n_s: int = 4,
        max_iter: int = 200_000,
        tol: float = 1e-10,
        pd_anchor: float | Mapping[str, float] | None = None,
        pd_anchor_c: float | None = None,
    ):
        """Solve the model and return its results.

        Parameters
        ----------
        method : {"grid", "analytical"}
            ``"grid"`` solves the Euler equations on the Tauchen-Hussey
            state space, which is what the paper's numbers come from.
            ``"analytical"`` is the log-linear approximation of Section
            3.4: instant, and the right tool for reading loadings.
        n_x, n_s : int
            Grid size for expected growth and variance. Grid method only;
            the paper uses 30 x 4.
        max_iter, tol : int, float
            Fixed-point iteration limits. Grid method only.
        pd_anchor : float or mapping, optional
            Linearization points for log P/D, as one number for every
            claim or a mapping by claim name. Analytical method only.
        pd_anchor_c : float, optional
            Linearization point for the consumption claim's log P/C.
            Analytical method only.

        Returns
        -------
        GridResults or AnalyticalResults

        Raises
        ------
        SolverDivergenceError
            If a fixed point leaves the plausible range, which usually
            means the grid is too coarse for the calibration.

        Examples
        --------
        ```python
        import lrrcs as lrr
        res = lrr.LongRunRisksModel().solve()
        print(res.summary())
        ```
        """
        if method == "grid":
            if pd_anchor is not None or pd_anchor_c is not None:
                raise ValueError(
                    "pd_anchor and pd_anchor_c apply to method='analytical'; "
                    "the grid method solves for log(P/D) instead of anchoring it."
                )
            solver = self._grid_solver(n_x, n_s, max_iter, tol)
            moments = None
            if self.legs.market is not None:
                from .implications.moments import compute_asset_pricing_moments

                moments = compute_asset_pricing_moments(
                    solver,
                    long=self.legs.long,
                    short=self.legs.short,
                    market=self.legs.market,
                )
            return GridResults(self, solver, moments)

        if method == "analytical":
            for name, value, default in (
                ("n_x", n_x, 30),
                ("n_s", n_s, 4),
                ("max_iter", max_iter, 200_000),
                ("tol", tol, 1e-10),
            ):
                if value != default:
                    raise ValueError(
                        f"{name} applies to method='grid'; the analytical "
                        "solution has no state grid."
                    )
            anchors = pd_anchor
            if isinstance(pd_anchor, (int, float)):
                anchors = {name: float(pd_anchor) for name in self.params.dividends}
            solution = solve_analytical(
                self.params,
                mean_zc=3.5 if pd_anchor_c is None else float(pd_anchor_c),
                mean_zs=anchors,
            )
            return AnalyticalResults(self, solution)

        raise ValueError(
            f"method must be 'grid' or 'analytical', got {method!r}."
        )

    # -- simulating -------------------------------------------------------
    def simulate(
        self,
        n_samples: int = 1000,
        years: int = 74,
        *,
        seed: int = 0,
        burn_in_years: int = 5,
        n_x: int = 30,
        n_s: int = 4,
    ) -> SimulationResults:
        """Simulate artificial samples and report Table VII statistics.

        The paper's model column is not a population moment: it is the
        average, across samples, of statistics estimated on ``years``
        years of annual data. This reproduces that object.

        Parameters
        ----------
        n_samples, years : int
            Number of artificial samples and their length (paper:
            1000 x 74).
        seed : int
            Seed of the random generator.
        burn_in_years : int
            Initial years discarded so states start near the stationary
            distribution.
        n_x, n_s : int
            Grid size of the underlying solve.

        Returns
        -------
        SimulationResults

        Examples
        --------
        ```python
        import lrrcs as lrr
        sim = lrr.LongRunRisksModel().simulate(n_samples=300, years=74, seed=0)
        print(sim.summary())
        ```
        """
        if self.legs.market is None:
            raise ValueError(
                "Simulation needs a market claim for the CAPM betas. Name one "
                "claim 'market', or pass market='...' when building the model."
            )
        from .implications.simulation import simulate_table_vii

        solver = self._grid_solver(n_x, n_s, 200_000, 1e-10)
        table = simulate_table_vii(
            solver,
            n_samples=n_samples,
            years=years,
            seed=seed,
            burn_in_years=burn_in_years,
            long=self.legs.long,
            short=self.legs.short,
            market=self.legs.market,
        )
        return SimulationResults(self, table, seed=seed)

    def simulate_paths(self, months: int, *, seed: int | None = None):
        """Simulate one path of the state and cash-flow processes.

        No prices are involved: this is the endowment side of the model,
        useful for seeing what expected growth and consumption growth
        actually look like.

        Parameters
        ----------
        months : int
            Length of the path.
        seed : int, optional
            Seed of the random generator.

        Returns
        -------
        DataFrame
            Columns ``x`` (expected growth), ``sigma2`` (variance),
            ``dc`` (consumption growth), and ``dd_<claim>`` for each
            claim, one row per month.

        Examples
        --------
        ```python
        import lrrcs as lrr
        path = lrr.LongRunRisksModel().simulate_paths(480, seed=3)
        path[["x", "dc"]].head()
        ```
        """
        import pandas as pd

        from ._backend import to_backend
        from .model.dynamics import Dynamics

        path = Dynamics(self.params, seed=seed).simulate_cashflows(months)
        return to_backend(pd.DataFrame(path))

    def simulate_cashflows(
        self, n_sims: int = 200, years: int = 74, seed: int = 42
    ):
        """Simulated cash-flow moments, with no prices involved.

        The calibration check behind Tables III to V: does the cash-flow
        side of the model look like the data before any asset is priced?

        Returns
        -------
        DataFrame
            One row per series (consumption and each claim), with the
            annual mean and volatility in percent, the first
            autocorrelation, and the correlation with consumption growth.
        """
        import pandas as pd

        from ._backend import to_backend
        from .calibration.simulation import simulate_cashflow_moments

        moments = simulate_cashflow_moments(
            n_sims=n_sims, years=years, seed=seed, params=self.params
        )
        cons = moments["consumption"]
        rows = {
            "consumption": {
                "mean": cons["E[dc]"],
                "volatility": cons["sigma(dc)"],
                "ac1": cons["AC1"],
                "corr_with_consumption": 1.0,
            }
        }
        for name, m in moments["dividends"].items():
            rows[name] = {
                "mean": m["E[dd]"],
                "volatility": m["sigma(dd)"],
                "ac1": m["AC1"],
                "corr_with_consumption": m["corr(dc,dd)"],
            }
        out = pd.DataFrame(rows).T
        out.index.name = "series"
        return to_backend(out.reset_index())

    # -- display ----------------------------------------------------------
    def __repr__(self) -> str:
        p = self.params.prefs
        return (
            f"LongRunRisksModel(gamma={p.gamma:g}, psi={p.psi:g}, "
            f"delta={p.delta:g}, claims={list(self.params.dividends)}, "
            f"long={self.legs.long!r}, short={self.legs.short!r})"
        )
