"""Annual (or sample-frequency) expected-growth proxies for x_t."""
from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike
from scipy.optimize import minimize


def expected_growth_proxy(dc: ArrayLike, window: int = 2) -> np.ndarray:
    """Moving average of lagged consumption growth (Kiku eq. 19 regressor).

    Entry ``t`` is ``mean(dc[t-window:t])`` for ``t >= window``, and ``nan``
    before that.

    Examples
    --------
    ```python
    import lrrcs as lrr
    x_hat = lrr.expected_growth_proxy(dc, window=2)
    ```
    """
    y = np.asarray(dc, dtype=float).ravel()
    if window < 1:
        raise ValueError("window must be >= 1")
    if y.size <= window:
        raise ValueError("Series too short for the requested window")
    ma = np.full(y.size, np.nan)
    for t in range(window, y.size):
        ma[t] = float(np.mean(y[t - window : t]))
    return ma


def _kalman_filter(
    y: np.ndarray, mu: float, rho: float, q: float, r: float
) -> tuple[float, np.ndarray]:
    """Filtered means E[x_t | y_{1:t}] and Gaussian log-likelihood."""
    n = y.size
    x_filt = np.empty(n)
    x_pred = 0.0
    p_pred = q / max(1.0 - rho * rho, 1e-8)
    loglik = 0.0
    two_pi = 2.0 * np.pi
    for t in range(n):
        innov = y[t] - mu - x_pred
        s = p_pred + r
        if not np.isfinite(s) or s <= 1e-18:
            return -np.inf, x_filt
        k = p_pred / s
        x_upd = x_pred + k * innov
        p_upd = (1.0 - k) * p_pred
        loglik += -0.5 * (np.log(two_pi * s) + innov * innov / s)
        x_filt[t] = x_upd
        x_pred = rho * x_upd
        p_pred = rho * rho * p_upd + q
    return float(loglik), x_filt


def filter_expected_growth(dc: ArrayLike) -> dict:
    """Univariate Kalman / AR(1) filter for expected consumption growth.

    State space (sample frequency, typically annual)::

        y_t = mu + x_t + v_t
        x_{t+1} = rho * x_t + w_t

    ``rho`` is *not* the monthly Table II value 0.98. Starting values are
    AC1(y) and half the sample variance. MLE uses ``scipy.optimize.minimize``.

    Examples
    --------
    ```python
    import lrrcs as lrr
    out = lrr.filter_expected_growth(dc)
    ```
    """
    y = np.asarray(dc, dtype=float).ravel()
    if y.size < 8:
        raise ValueError("Series too short for Kalman filter")
    mu = float(np.mean(y))
    var = float(np.var(y))
    if var < 1e-18:
        raise ValueError("Consumption growth has no variation")
    rho0 = float(np.corrcoef(y[:-1], y[1:])[0, 1])
    if not np.isfinite(rho0):
        rho0 = 0.5
    rho0 = float(np.clip(rho0, 1e-6, 0.999))
    q0 = r0 = max(var / 2.0, 1e-12)

    def nll(theta: np.ndarray) -> float:
        rho, q, r = float(theta[0]), float(theta[1]), float(theta[2])
        ll, _ = _kalman_filter(y, mu, rho, q, r)
        if not np.isfinite(ll):
            return 1e20
        return -ll

    res = minimize(
        nll,
        x0=np.array([rho0, q0, r0], dtype=float),
        method="L-BFGS-B",
        bounds=[(1e-6, 0.999), (1e-12, None), (1e-12, None)],
    )
    if not res.success:
        raise ValueError(f"Kalman MLE did not converge: {res.message}")
    rho, q, r = (float(res.x[0]), float(res.x[1]), float(res.x[2]))
    loglik, x_filt = _kalman_filter(y, mu, rho, q, r)
    if not np.isfinite(loglik):
        raise ValueError("Kalman MLE did not converge: non-finite likelihood")
    return {
        "x": x_filt,
        "mu": mu,
        "rho": rho,
        "q": q,
        "r": r,
        "loglik": loglik,
    }
