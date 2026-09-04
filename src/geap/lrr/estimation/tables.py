"""Table 3 and Table 5 sample–model–t frames (BKY 2016)."""
from __future__ import annotations

import numpy as np
import pandas as pd

from ...gmm.weighting import newey_west
from .aggregation import model_moments
from .moments import MOMENT_NAMES, _eta2_model, observation_moments
from .solution import BKYParams

# Paper p. 61 order.
_TABLE3_KEYS = (
    "vol_dc",
    "ac1_dc",
    "ac2_dc",
    "vol_dd",
    "ac1_dd",
    "corr_dc_dd",
    "e_eta",
    "e_u",
    "e_eta_x",
    "e_eta2_s2",
    "vol_eta2",
    "ac1_eta2",
    "mean_zd",
    "vol_zd",
    "ac1_zd",
    "mean_excess",
    "vol_rd",
    "mean_rf",
    "corr_rd_zd",
    "corr_dc_zd",
)

# Orthogonality restrictions: the model implication is zero.
_ZERO_MODEL = frozenset({"e_eta", "e_u", "e_eta_x", "e_eta2_s2"})


def table3_keys() -> tuple[str, ...]:
    return _TABLE3_KEYS


def _ac1(x: np.ndarray) -> float:
    y = np.asarray(x, dtype=float)
    y = y[np.isfinite(y)]
    if y.size < 3:
        return float("nan")
    yd = y - y.mean()
    return float(np.corrcoef(yd[1:], yd[:-1])[0, 1])


def _ac2(x: np.ndarray) -> float:
    y = np.asarray(x, dtype=float)
    y = y[np.isfinite(y)]
    if y.size < 4:
        return float("nan")
    yd = y - y.mean()
    return float(np.corrcoef(yd[2:], yd[:-2])[0, 1])


def sample_table3(data: pd.DataFrame) -> dict[str, float]:
    """Sample analogs of Table 3 moments in the paper's units."""
    dc = data["dc"].to_numpy(dtype=float)
    dd = data["dd"].to_numpy(dtype=float)
    z = data["log_pd"].to_numpy(dtype=float)
    rf = data["rf"].to_numpy(dtype=float)
    rm = data["rm"].to_numpy(dtype=float)
    excess = rm - rf
    return {
        "mean_dc": float(np.nanmean(dc)),
        "vol_dc": float(np.nanstd(dc, ddof=1)),
        "ac1_dc": _ac1(dc),
        "ac2_dc": _ac2(dc),
        "mean_dd": float(np.nanmean(dd)),
        "vol_dd": float(np.nanstd(dd, ddof=1)),
        "ac1_dd": _ac1(dd),
        "corr_dc_dd": float(np.corrcoef(dc, dd)[0, 1]),
        "mean_zd": float(np.nanmean(z)),
        "vol_zd": float(np.nanstd(z, ddof=1)),
        "ac1_zd": _ac1(z),
        "mean_excess": float(np.nanmean(excess)),
        "vol_rd": float(np.nanstd(rm, ddof=1)),
        "mean_rf": float(np.nanmean(rf)),
        "corr_rd_zd": float(np.corrcoef(rm[1:], z[:-1])[0, 1]),
        "corr_dc_zd": float(np.corrcoef(dc[1:], z[:-1])[0, 1]),
    }


def _column_t(g_col: np.ndarray, hac_lags: int) -> float:
    y = np.asarray(g_col, dtype=float)
    y = y[np.isfinite(y)]
    nobs = y.size
    if nobs < 2:
        return float("nan")
    bar = float(y.mean())
    s = newey_west(y.reshape(-1, 1), lags=hac_lags)
    var_mean = float(s[0, 0]) / nobs
    if var_mean <= 0.0 or not np.isfinite(var_mean):
        return float("nan")
    return bar / float(np.sqrt(var_mean))


def _state_sample(g: np.ndarray) -> dict[str, float]:
    idx = {name: i for i, name in enumerate(MOMENT_NAMES)}
    eta = g[:, idx["e_eta"]]
    eta2 = eta**2
    return {
        "e_eta": float(np.nanmean(eta)),
        "e_u": float(np.nanmean(g[:, idx["e_u"]])),
        "e_eta_x": float(np.nanmean(g[:, idx["e_eta_x"]])),
        "e_eta2_s2": float(np.nanmean(g[:, idx["e_eta2_s2"]])),
        "vol_eta2": float(np.nanstd(eta2, ddof=1)),
        "ac1_eta2": _ac1(eta2),
    }


def table3_frame(
    data: pd.DataFrame,
    params: BKYParams,
    h: int,
    *,
    hac_lags: int = 1,
) -> pd.DataFrame:
    """Table 3 sample, model, and t(diff) at ``params`` and aggregation ``h``."""
    model = model_moments(params, h)
    vol_e2, ac1_e2, _var_e2 = _eta2_model(params, h)
    model["vol_eta2"] = float(vol_e2)
    model["ac1_eta2"] = float(ac1_e2)
    sample = sample_table3(data)
    g = np.asarray(observation_moments(data, params, h), dtype=float)
    sample.update(_state_sample(g))
    name_index = {name: i for i, name in enumerate(MOMENT_NAMES)}
    rows = []
    for key in table3_keys():
        if key in _ZERO_MODEL:
            model_value = 0.0
        elif key in model:
            model_value = float(model[key])
        else:
            model_value = float("nan")
        if key in name_index:
            t_diff = _column_t(g[:, name_index[key]], hac_lags)
        else:
            t_diff = float("nan")
        rows.append(
            {
                "moment": key,
                "sample": float(sample.get(key, np.nan)),
                "model": model_value,
                "t_diff": t_diff,
            }
        )
    return pd.DataFrame(rows)


def table5_frame(
    data: pd.DataFrame,
    params: BKYParams,
    h: int = 1,
    *,
    hac_lags: int = 1,
) -> pd.DataFrame:
    """Table 5 sample, model, and t(diff) for the annual specification."""
    return table3_frame(data, params, h, hac_lags=hac_lags)
