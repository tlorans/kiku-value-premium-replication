from __future__ import annotations
import numpy as np


def newey_west_mean(x: np.ndarray, lags: int = 8) -> tuple[float, float]:
    y = np.asarray(x, dtype=float)
    y = y[np.isfinite(y)]
    t = y.size
    if t == 0:
        return float("nan"), float("nan")
    mu = float(y.mean())
    e = y - mu
    gamma0 = float(np.mean(e * e))
    acc = gamma0
    lmax = min(int(lags), t - 1)
    for k in range(1, lmax + 1):
        w = 1.0 - k / (lmax + 1)
        acc += 2.0 * w * float(np.mean(e[k:] * e[:-k]))
    se = float(np.sqrt(max(acc / t, 0.0)))
    return mu, se


def sd_and_se(x: np.ndarray, lags: int = 8) -> tuple[float, float]:
    y = np.asarray(x, dtype=float)
    y = y[np.isfinite(y)]
    if y.size < 2:
        return float("nan"), float("nan")
    sd = float(np.std(y, ddof=1))
    if sd == 0.0:
        return 0.0, 0.0
    m2, se_m2 = newey_west_mean((y - y.mean()) ** 2, lags=lags)
    return sd, float(se_m2 / (2.0 * sd))


def within_se(value: float, printed: float, se: float) -> bool:
    return abs(float(value) - float(printed)) <= float(se) + 1e-12
