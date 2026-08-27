"""Annual (or sample-frequency) expected-growth proxies for x_t."""
from __future__ import annotations

import numpy as np
from numpy.typing import ArrayLike


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
