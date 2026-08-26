from __future__ import annotations

import numpy as np


def book_equity(seq, txditc, pstkrv, pstkl, pstk) -> float:
    preferred = 0.0
    for cand in (pstkrv, pstkl, pstk):
        if np.isfinite(cand):
            preferred = float(cand)
            break
    tax = 0.0 if not np.isfinite(txditc) else float(txditc)
    return float(seq) + tax - preferred


def nyse_quintile_labels(bm_all, bm_nyse) -> np.ndarray:
    edges = np.quantile(np.asarray(bm_nyse, dtype=float), [0.2, 0.4, 0.6, 0.8])
    return np.digitize(np.asarray(bm_all, dtype=float), edges, right=True) + 1
