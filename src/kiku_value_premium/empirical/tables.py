from __future__ import annotations

import numpy as np
import pandas as pd

CLAIMS = ("Growth", "Value", "Market")


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


def _slice_window(bm: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    return bm[(bm["year"] >= start) & (bm["year"] <= end)].copy()


def newey_west_ols_se(y: np.ndarray, x: np.ndarray, lags: int = 4) -> float:
    """Newey–West HAC SE of the slope in y = a + b x."""
    y = np.asarray(y, dtype=float).ravel()
    x = np.asarray(x, dtype=float).ravel()
    mask = np.isfinite(y) & np.isfinite(x)
    y, x = y[mask], x[mask]
    t = y.size
    if t < 3:
        return float("nan")
    X = np.column_stack([np.ones(t), x])
    try:
        xtx_inv = np.linalg.inv(X.T @ X)
    except np.linalg.LinAlgError:
        return float("nan")
    beta = xtx_inv @ (X.T @ y)
    e = y - X @ beta
    u = e[:, None] * X
    acc = u.T @ u
    lmax = min(int(lags), t - 1)
    for k in range(1, lmax + 1):
        w = 1.0 - k / (lmax + 1)
        g = u[k:].T @ u[:-k]
        acc += w * (g + g.T)
    vcov = xtx_inv @ acc @ xtx_inv
    return float(np.sqrt(max(float(vcov[1, 1]), 0.0)))


def _ols_slope(y: np.ndarray, x: np.ndarray) -> float:
    y = np.asarray(y, dtype=float).ravel()
    x = np.asarray(x, dtype=float).ravel()
    mask = np.isfinite(y) & np.isfinite(x)
    y, x = y[mask], x[mask]
    if y.size < 2:
        return float("nan")
    xd = x - x.mean()
    den = float(np.dot(xd, xd))
    if den == 0.0:
        return float("nan")
    return float(np.dot(xd, y - y.mean()) / den)


def _eq19_yx(
    dgrowth: pd.Series, dc: pd.Series, window: int = 2
) -> tuple[pd.Series, pd.Series]:
    ma = dc.shift(1)
    for k in range(2, window + 1):
        ma = ma + dc.shift(k)
    ma = ma / float(window)
    frame = pd.concat({"y": dgrowth.astype(float), "x": ma.astype(float)}, axis=1).dropna()
    return frame["y"], frame["x"]


def _ar1_residual(dc: pd.Series) -> pd.Series:
    s = pd.Series(dc).astype(float).dropna()
    if s.size < 3:
        return pd.Series(dtype=float)
    y = s.iloc[1:].to_numpy()
    x = s.iloc[:-1].to_numpy()
    X = np.column_stack([np.ones(y.size), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    eta = y - X @ beta
    return pd.Series(eta, index=s.index[1:], name="eta")


def table_i(bm: pd.DataFrame, start: int, end: int) -> pd.DataFrame:
    """Table I Panel A: means and vols. Returns and Δd in percent; log(P/D) in logs."""
    sub = _slice_window(bm, start, end)
    rows = []
    for claim in CLAIMS:
        g = sub[sub["claim"] == claim]
        ret = g["ret"].to_numpy(dtype=float) * 100.0
        dg = g["dgrowth"].to_numpy(dtype=float) * 100.0
        log_pd = np.log(g["pd"].to_numpy(dtype=float))
        ret_m, ret_se = newey_west_mean(ret, lags=8)
        ret_sd, ret_sd_se = sd_and_se(ret, lags=8)
        dg_m, dg_se = newey_west_mean(dg, lags=8)
        dg_sd, dg_sd_se = sd_and_se(dg, lags=8)
        pd_m, pd_se = newey_west_mean(log_pd, lags=8)
        rows.append(
            {
                "claim": claim,
                "ret_mean": ret_m,
                "ret_se": ret_se,
                "ret_sd": ret_sd,
                "ret_sd_se": ret_sd_se,
                "dg_mean": dg_m,
                "dg_se": dg_se,
                "dg_sd": dg_sd,
                "dg_sd_se": dg_sd_se,
                "log_pd": pd_m,
                "log_pd_se": pd_se,
            }
        )
    return pd.DataFrame(rows)


def table_i_corr(bm: pd.DataFrame, start: int, end: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Table I Panel B: return and dividend-growth correlations."""
    sub = _slice_window(bm, start, end)

    def _corr(kind: str) -> pd.DataFrame:
        wide = sub.pivot(index="year", columns="claim", values=kind)
        wide = wide.reindex(columns=list(CLAIMS))
        mat = pd.DataFrame(index=list(CLAIMS), columns=list(CLAIMS), dtype=float)
        for a in CLAIMS:
            for b in CLAIMS:
                if a == b:
                    mat.loc[a, b] = 1.0
                    continue
                pair = wide[[a, b]].dropna()
                if len(pair) < 3 or pair[a].std(ddof=1) == 0 or pair[b].std(ddof=1) == 0:
                    mat.loc[a, b] = float("nan")
                else:
                    mat.loc[a, b] = float(pair[a].corr(pair[b]))
        mat.index.name = "claim"
        return mat

    return _corr("ret"), _corr("dgrowth")


def table_vi_data(
    bm: pd.DataFrame, dc: pd.Series, start: int, end: int
) -> pd.DataFrame:
    """Table VI data column: eq. (19) φ̃ (NW 4 lags) and innovation correlations."""
    sub = _slice_window(bm, start, end)
    dc_s = pd.Series(dc).astype(float)
    eta = _ar1_residual(dc_s)
    rows = []
    for claim in CLAIMS:
        dg = (
            sub.loc[sub["claim"] == claim]
            .set_index("year")["dgrowth"]
            .astype(float)
        )
        y, x = _eq19_yx(dg, dc_s)
        if y.size < 2:
            phi = float("nan")
            phi_se = float("nan")
            innov = float("nan")
        else:
            phi = _ols_slope(y.to_numpy(), x.to_numpy())
            phi_se = newey_west_ols_se(y.to_numpy(), x.to_numpy(), lags=4)
            resid = y.to_numpy() - (
                y.to_numpy().mean() + phi * (x.to_numpy() - x.to_numpy().mean())
            )
            resid_s = pd.Series(resid, index=y.index)
            pair = pd.concat({"e": resid_s, "eta": eta}, axis=1).dropna()
            if (
                len(pair) < 2
                or pair["e"].std(ddof=1) == 0
                or pair["eta"].std(ddof=1) == 0
            ):
                innov = float("nan")
            else:
                innov = float(pair["e"].corr(pair["eta"]))
        rows.append(
            {
                "claim": claim,
                "phi_tilde": phi,
                "phi_se": phi_se,
                "innov_corr": innov,
            }
        )
    return pd.DataFrame(rows)

