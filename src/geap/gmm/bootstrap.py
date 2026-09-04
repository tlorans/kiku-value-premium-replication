"""Moving-block bootstrap of an estimator that takes row indices."""
from __future__ import annotations

from typing import Callable

import numpy as np


def moving_block_indices(
    nobs: int,
    block_length: int,
    rng: np.random.Generator,
) -> np.ndarray:
    """Resample ``nobs`` indices from contiguous blocks of ``block_length``."""
    if nobs < 1:
        raise ValueError("nobs must be >= 1")
    length = int(block_length)
    if length < 1:
        raise ValueError("block_length must be >= 1")
    length = min(length, nobs)
    n_blocks = int(np.ceil(nobs / length))
    starts = rng.integers(0, nobs - length + 1, size=n_blocks)
    idx = np.concatenate([np.arange(s, s + length) for s in starts])
    return idx[:nobs]


def block_bootstrap(
    estimate: Callable[[np.ndarray], np.ndarray],
    nobs: int,
    *,
    block_length: int = 8,
    n_boot: int = 100,
    rng: np.random.Generator | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Moving-block bootstrap standard errors.

    ``estimate(indices)`` returns a 1-d parameter vector computed on the
    observations ``indices``. Returns ``(se, draws)`` with ``draws`` of
    shape ``(n_boot, p)``.
    """
    rng = rng if rng is not None else np.random.default_rng()
    probe = np.asarray(estimate(np.arange(nobs)), dtype=float).ravel()
    draws = np.empty((int(n_boot), probe.size), dtype=float)
    for b in range(int(n_boot)):
        idx = moving_block_indices(nobs, block_length, rng)
        draws[b] = np.asarray(estimate(idx), dtype=float).ravel()
    se = draws.std(axis=0, ddof=1)
    return se, draws
