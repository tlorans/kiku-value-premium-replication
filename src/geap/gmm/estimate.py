"""Hansen GMM: choose θ to make sample moments close to zero."""
from __future__ import annotations

from typing import Callable, Iterable

import numpy as np
from scipy.optimize import minimize
from scipy.stats import chi2

from .results import GMMResults
from .weighting import hansen_j_general, invvar_weights, newey_west, resolve_weights, sandwich

MomentFn = Callable[[np.ndarray], np.ndarray]


def _as_theta(theta) -> np.ndarray:
    return np.atleast_1d(np.asarray(theta, dtype=float)).ravel()


def _unpack(raw) -> tuple[np.ndarray | None, np.ndarray]:
    """Return ``(g_t or None, g_T)`` from a moments() evaluation."""
    arr = np.asarray(raw, dtype=float)
    if arr.ndim == 0:
        arr = arr.reshape(1)
    if arr.ndim == 1:
        return None, arr
    if arr.ndim == 2:
        return arr, arr.mean(axis=0)
    raise ValueError("moments must return a 1-d g_T or a 2-d array g_t of shape (T, k).")


def _eval(moments: MomentFn, theta: np.ndarray) -> tuple[np.ndarray | None, np.ndarray]:
    return _unpack(moments(_as_theta(theta)))


def _finite_difference_jacobian(moments: MomentFn, theta: np.ndarray) -> np.ndarray:
    theta = _as_theta(theta)
    _, g0 = _eval(moments, theta)
    d = np.empty((g0.size, theta.size), dtype=float)
    for j, value in enumerate(theta):
        step = 1e-8 * (1.0 + abs(float(value)))
        bumped = theta.copy()
        bumped[j] = value + step
        _, gp = _eval(moments, bumped)
        d[:, j] = (gp - g0) / step
    return d


def _default_names(n_params: int) -> tuple[str, ...]:
    if n_params == 1:
        return ("theta",)
    return tuple(f"theta{i}" for i in range(n_params))


def _assemble(
    theta: np.ndarray,
    g_t: np.ndarray | None,
    g_T: np.ndarray,
    W: np.ndarray,
    *,
    steps: int,
    hac_lags: int,
    names: tuple[str, ...],
    jacobian: np.ndarray | None = None,
    moments: MomentFn | None = None,
    efficient: bool,
    j_test: bool = False,
) -> GMMResults:
    nobs = None if g_t is None else int(g_t.shape[0])
    n_params = int(theta.size)
    n_moments = int(g_T.size)
    objective = float(g_T @ W @ g_T)
    cov = se = S = J = J_pvalue = None
    j_df = n_moments - n_params
    if g_t is not None and nobs is not None and nobs > 0:
        S = newey_west(g_t, lags=hac_lags)
        if jacobian is None:
            if moments is None:
                raise ValueError("Inference needs a Jacobian or the moments callable.")
            jacobian = _finite_difference_jacobian(moments, theta)
        cov = sandwich(jacobian, W, S, nobs)
        se = np.sqrt(np.clip(np.diag(cov), 0.0, None))
        if n_moments > n_params and (efficient or j_test):
            if efficient and not j_test:
                J = float(nobs * objective)
            else:
                J, j_df = hansen_j_general(g_T, jacobian, W, S, nobs)
            J_pvalue = float(chi2.sf(J, j_df))
    return GMMResults(
        theta,
        g_T,
        W,
        objective=objective,
        nobs=nobs,
        names=names,
        steps=steps,
        cov=cov,
        se=se,
        S=S,
        J=J,
        J_df=j_df,
        J_pvalue=J_pvalue,
    )


def estimate(
    moments: MomentFn,
    theta0,
    *,
    W="identity",
    steps: int = 1,
    hac_lags: int | None = None,
    bounds=None,
    names: Iterable[str] | None = None,
    options: dict | None = None,
    j_test: bool = False,
) -> GMMResults:
    """Hansen GMM: minimise ``g_T(θ)' W g_T(θ)``.

    Parameters
    ----------
    moments : callable
        ``moments(theta)`` returns either a length-``k`` sample moment
        vector ``g_T`` or a ``(T, k)`` array of observation-level
        moments ``g_t``. Observation-level moments are required for
        two-step weights, standard errors, and the J-test.
    theta0 : array-like
        Starting value, length ``p``.
    W : {"identity", "invvar", "optimal"} or ndarray
        Weighting matrix. ``"optimal"`` is two-step GMM starting from
        the identity. An explicit ``(k, k)`` array is used as the
        first-step weights.
    steps : int
        ``1`` uses ``W`` as given. ``2`` or more rebuilds
        ``W = S^{-1}`` from the Newey-West covariance of ``g_t``.
    hac_lags : int, optional
        Newey-West lags. ``None`` (the default) is iid, ``L = 0``.
    bounds : sequence, optional
        Passed to ``scipy.optimize.minimize``. Switches the solver to
        L-BFGS-B.
    names : sequence of str, optional
        Parameter names for :class:`GMMResults`.
    options : dict, optional
        Solver options for ``scipy.optimize.minimize``.
    """
    theta = _as_theta(theta0)
    n_params = int(theta.size)
    g_t, g_T = _eval(moments, theta)
    n_moments = int(g_T.size)
    if n_moments < n_params:
        raise ValueError(
            f"GMM needs at least as many moments as parameters; "
            f"got {n_moments} moments and {n_params} parameters."
        )
    lags = 0 if hac_lags is None else int(hac_lags)
    n_steps = int(steps)
    w_spec = W
    if isinstance(W, str) and W.lower() == "optimal":
        n_steps = max(n_steps, 2)
        w_spec = "identity"
    if n_steps < 1:
        raise ValueError("steps must be >= 1")
    if n_steps > 1 and g_t is None:
        raise ValueError(
            "Two-step GMM needs observation-level moments of shape (T, k)."
        )
    cue = isinstance(W, str) and W.lower() == "cue_invvar"
    if cue and g_t is None:
        raise ValueError("cue_invvar weights need observation-level moments of shape (T, k).")
    W_mat = resolve_weights(w_spec, g_t, n_moments)
    names_t = tuple(names) if names is not None else _default_names(n_params)
    if len(names_t) != n_params:
        raise ValueError(
            f"names has length {len(names_t)}; expected {n_params} parameters."
        )

    method = "L-BFGS-B" if bounds is not None else "Nelder-Mead"
    solver_options = dict(options or {})
    if method == "Nelder-Mead":
        solver_options.setdefault("xatol", 1e-12)
        solver_options.setdefault("fatol", 1e-16)
        solver_options.setdefault("maxiter", 4000)

    current = theta
    current_W = W_mat
    current_gt, current_gT = g_t, g_T
    for step in range(n_steps):
        def objective(th, _W=current_W, _cue=cue, _lags=lags):
            gt, g = _eval(moments, th)
            if _cue:
                if gt is None:
                    raise ValueError(
                        "cue_invvar weights need observation-level moments of shape (T, k)."
                    )
                _W = invvar_weights(gt, lags=_lags)
            return float(g @ _W @ g)

        result = minimize(
            objective,
            current,
            method=method,
            bounds=bounds,
            options=solver_options,
        )
        current = _as_theta(result.x)
        current_gt, current_gT = _eval(moments, current)
        if cue and current_gt is not None:
            current_W = invvar_weights(current_gt, lags=lags)
        if step < n_steps - 1:
            if current_gt is None:
                raise ValueError(
                    "Two-step GMM needs observation-level moments of shape (T, k)."
                )
            S = newey_west(current_gt, lags=lags)
            current_W = np.linalg.pinv(S)

    return _assemble(
        current,
        current_gt,
        current_gT,
        current_W,
        steps=n_steps,
        hac_lags=lags,
        names=names_t,
        moments=moments,
        efficient=n_steps >= 2,
        j_test=j_test,
    )
