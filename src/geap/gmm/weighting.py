"""Weighting matrices and the Newey-West covariance of sample moments."""
from __future__ import annotations

import numpy as np


def newey_west(g_t: np.ndarray, lags: int = 0) -> np.ndarray:
    """Uncentered Newey-West covariance of observation-level moments.

    ``S = Γ_0 + Σ_ℓ w_ℓ (Γ_ℓ + Γ_ℓ')`` with Bartlett weights
    ``w_ℓ = 1 - ℓ/(L+1)``. ``lags=0`` is the iid second-moment matrix.
    """
    g_t = np.asarray(g_t, dtype=float)
    if g_t.ndim != 2:
        raise ValueError("Newey-West needs g_t with shape (T, k).")
    nobs, _ = g_t.shape
    if nobs < 1:
        raise ValueError("Newey-West needs at least one observation.")
    lags = int(lags)
    if lags < 0:
        raise ValueError("hac_lags must be >= 0")
    scale = 1.0 / nobs
    s = g_t.T @ g_t * scale
    for lag in range(1, lags + 1):
        gamma = g_t[lag:].T @ g_t[:-lag] * scale
        weight = 1.0 - lag / (lags + 1)
        s = s + weight * (gamma + gamma.T)
    return s


def invvar_weights(g_t: np.ndarray, lags: int = 0) -> np.ndarray:
    """Diagonal weights: inverse of each moment's variance.

    ``lags=0`` is the iid sample variance. ``lags>0`` takes the diagonal
    of the Newey-West covariance (Hansen, Heaton, Yaron 1996 CUE with
    a HAC diagonal, as in Bansal, Kiku, and Yaron 2016).
    """
    g_t = np.asarray(g_t, dtype=float)
    if g_t.ndim != 2:
        raise ValueError("invvar weights need observation-level moments of shape (T, k).")
    if lags:
        var = np.diag(newey_west(g_t, lags=lags))
    else:
        var = np.var(g_t, axis=0, ddof=1)
    if np.any(var <= 0.0) or not np.all(np.isfinite(var)):
        raise ValueError("invvar weights need finite positive moment variances.")
    return np.diag(1.0 / var)


def resolve_weights(W, g_t: np.ndarray | None, k: int) -> np.ndarray:
    """Turn a W spec into a ``(k, k)`` matrix."""
    if isinstance(W, str):
        key = W.lower()
        if key in ("identity", "optimal"):
            return np.eye(k)
        if key in ("invvar", "cue_invvar"):
            if g_t is None:
                raise ValueError(
                    "invvar weights need observation-level moments of shape (T, k)."
                )
            return invvar_weights(g_t)
        raise ValueError(
            f"Unknown weighting {W!r}; use 'identity', 'invvar', 'optimal', "
            "or a matrix."
        )
    W = np.asarray(W, dtype=float)
    if W.shape != (k, k):
        raise ValueError(f"W must be shape {(k, k)}, got {W.shape}.")
    return W


def hansen_j_general(
    g: np.ndarray,
    jacobian: np.ndarray,
    W: np.ndarray,
    S: np.ndarray,
    nobs: int,
) -> tuple[float, int]:
    """Hansen (1982) Lemma 4.2 J-test for a general weighting matrix.

    At the GMM optimum ``D' W g = 0``. The statistic is
    ``T g' (M S M')^{+} g`` with ``M = I - D (D' W D)^{-1} D' W``,
    which reduces to ``T g' S^{-1} g`` when ``W = S^{-1}``.
    """
    g = np.asarray(g, dtype=float).ravel()
    d = np.asarray(jacobian, dtype=float)
    w = np.asarray(W, dtype=float)
    s = np.asarray(S, dtype=float)
    k = int(g.size)
    p = int(d.shape[1])
    dtW = d.T @ w
    bread = np.linalg.pinv(dtW @ d)
    m = np.eye(k) - d @ bread @ dtW
    v = m @ s @ m.T
    j = float(nobs * g @ np.linalg.pinv(v) @ g)
    return j, max(k - p, 0)


def sandwich(
    jacobian: np.ndarray,
    W: np.ndarray,
    S: np.ndarray,
    nobs: int,
) -> np.ndarray:
    """Asymptotic variance of ``θ̂``: sandwich over ``T``.

    With efficient ``W = S^{-1}`` this equals ``(D' S^{-1} D)^{-1} / T``.
    """
    d = np.asarray(jacobian, dtype=float)
    bread_inv = d.T @ W @ d
    try:
        bread = np.linalg.inv(bread_inv)
    except np.linalg.LinAlgError:
        bread = np.linalg.pinv(bread_inv)
    meat = d.T @ W @ S @ W @ d
    return (bread @ meat @ bread) / float(nobs)
