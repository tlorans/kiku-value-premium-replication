"""Asset-pricing moment constructors for Hansen GMM."""
from __future__ import annotations

from typing import Iterable

import numpy as np

from .estimate import _assemble, _as_theta
from .weighting import newey_west, resolve_weights


def power_utility_sdf(delta, gamma, growth) -> np.ndarray:
    """Power-utility SDF ``m = δ g^{-γ}`` on gross consumption growth."""
    g = np.asarray(growth, dtype=float)
    return float(delta) * g ** (-float(gamma))


def sdf_moments(m, excess_returns) -> np.ndarray:
    """Observation-level pricing errors ``g_t = m_t R^e_t``, shape ``(T, N)``."""
    m = np.asarray(m, dtype=float).ravel()
    re = np.asarray(excess_returns, dtype=float)
    if re.ndim == 1:
        re = re[:, None]
    if re.shape[0] != m.size:
        raise ValueError(
            f"SDF has length {m.size}, excess returns have {re.shape[0]} rows."
        )
    return m[:, None] * re


def _closed_form(mean: np.ndarray, beta: np.ndarray, W: np.ndarray) -> np.ndarray:
    """λ̂ = (β' W β)^{-1} β' W R̄."""
    gram = beta.T @ W @ beta
    rhs = beta.T @ W @ mean
    gram = np.atleast_2d(np.asarray(gram, dtype=float))
    rhs = np.atleast_1d(np.asarray(rhs, dtype=float)).ravel()
    try:
        return np.linalg.solve(gram, rhs)
    except np.linalg.LinAlgError:
        return (np.linalg.pinv(gram) @ rhs).ravel()


def linear_factor(
    excess_returns,
    beta,
    *,
    W="identity",
    steps: int = 1,
    hac_lags: int | None = None,
    names: Iterable[str] | None = None,
):
    """Price of risk from ``E[R^e] = β λ``.

    Parameters
    ----------
    excess_returns : array-like
        Length-``N`` mean excess returns, or a ``(T, N)`` panel.
    beta : array-like
        Length-``N`` betas, or an ``(N, K)`` factor loading matrix.
    W, steps, hac_lags, names
        Forwarded to the GMM engine. The estimator is closed form:
        ``λ = (β' W β)^{-1} β' W R̄``. With identity weights this is
        OLS of average excess returns on betas.
    """
    returns = np.asarray(excess_returns, dtype=float)
    loadings = np.asarray(beta, dtype=float)
    if loadings.ndim == 1:
        loadings = loadings[:, None]
    if returns.ndim == 1:
        panel = None
        mean = returns.ravel()
    elif returns.ndim == 2:
        panel = returns
        mean = returns.mean(axis=0)
    else:
        raise ValueError("excess_returns must be 1-d means or a 2-d panel.")
    n_assets = int(mean.size)
    if loadings.shape[0] != n_assets:
        raise ValueError(
            f"beta has {loadings.shape[0]} rows, excess returns have {n_assets} assets."
        )
    n_factors = int(loadings.shape[1])
    if n_assets < n_factors:
        raise ValueError(
            f"GMM needs at least as many moments as parameters; "
            f"got {n_assets} moments and {n_factors} parameters."
        )
    n_steps = int(steps)
    w_spec = W
    if isinstance(W, str) and W.lower() == "optimal":
        n_steps = max(n_steps, 2)
        w_spec = "identity"
    if n_steps < 1:
        raise ValueError("steps must be >= 1")
    if n_steps > 1 and panel is None:
        raise ValueError(
            "Two-step GMM needs observation-level moments of shape (T, k)."
        )
    lags = 0 if hac_lags is None else int(hac_lags)
    g_probe = panel
    W_mat = resolve_weights(w_spec, g_probe, n_assets)
    theta = _closed_form(mean, loadings, W_mat)
    for _ in range(n_steps - 1):
        g_t = panel - (loadings @ theta)
        S = newey_west(g_t, lags=lags)
        W_mat = np.linalg.pinv(S)
        theta = _closed_form(mean, loadings, W_mat)
    theta = _as_theta(theta)
    if panel is None:
        g_t = None
        g_T = mean - (loadings @ theta)
    else:
        g_t = panel - (loadings @ theta)
        g_T = g_t.mean(axis=0)
    if names is None:
        names_t = (
            ("lambda",) if n_factors == 1 else tuple(f"lambda{i}" for i in range(n_factors))
        )
    else:
        names_t = tuple(names)
    jacobian = -loadings
    return _assemble(
        theta,
        g_t,
        g_T,
        W_mat,
        steps=n_steps,
        hac_lags=lags,
        names=names_t,
        jacobian=jacobian,
        efficient=n_steps >= 2,
    )
