"""Time-aggregated moments of the LRR model (BKY 2016, appendix B)."""
from __future__ import annotations

import numpy as np

from .solution import BKYParams, LogLinearSolution, solve_loglinear


def long_run_variance_share(p: BKYParams, h: int) -> float:
    """Share of aggregated consumption variance from x and its innovations."""
    vx = var_x(p)
    cx, ce, ceta = _flow_loadings(h, p.rho, p.phi_e, p.sigma, 1.0, 1.0)
    tot = cx**2 * vx + float(ce @ ce) + float(ceta @ ceta)
    if tot <= 0:
        return 0.0
    return float((cx**2 * vx + float(ce @ ce)) / tot)


def var_x(p: BKYParams) -> float:
    return (p.phi_e * p.sigma) ** 2 / (1.0 - p.rho**2)


def var_sigma2(p: BKYParams) -> float:
    if p.sigma_w == 0.0 or abs(p.nu) >= 1.0:
        return 0.0
    return p.sigma_w**2 / (1.0 - p.nu**2)


def _flow_weights(h: int) -> np.ndarray:
    """Working-style weights on Δy_{t-2h+1}, …, Δy_t (length 2h)."""
    w = np.zeros(2 * h)
    for k in range(2, h + 1):
        w[k - 1] = (k - 1) / float(h)
    for j in range(1, h + 1):
        w[h + j - 1] = (h - j + 1) / float(h)
    return w


def _flow_loadings(
    h: int,
    rho: float,
    phi_e: float,
    sigma: float,
    phi_x: float,
    phi_shock: float,
    shift: int = 0,
    n_periods: int | None = None,
) -> tuple[float, np.ndarray, np.ndarray]:
    """Loadings of an aggregated flow on x_{origin}, e-shocks, and own shocks.

    ``shift`` moves the window forward by that many decision periods.
    Shocks are indexed from the origin (shift 0 starts at t-2h).
    """
    w = _flow_weights(h)
    n = 2 * h
    total = n_periods if n_periods is not None else n + shift
    coef_x = 0.0
    load_e = np.zeros(total)
    load_own = np.zeros(total)
    for k in range(1, n + 1):
        wk = w[k - 1]
        if wk == 0.0:
            continue
        time = shift + k  # Δy at origin+time uses x_{origin+time-1}
        coef_x += wk * phi_x * (rho ** (time - 1))
        # own shock at origin+time
        if 1 <= time <= total:
            load_own[time - 1] += wk * phi_shock * sigma
        for i in range(1, time):
            if i <= total:
                load_e[i - 1] += wk * phi_x * phi_e * sigma * (rho ** (time - 1 - i))
    return float(coef_x), load_e, load_own


def _second_moments_flow(
    p: BKYParams,
    h: int,
    phi_x: float,
    phi_shock: float,
    rho_own_eta: float,
) -> dict[str, float]:
    """Mean, vol, AC1, AC2 of an aggregated flow, and its corr with Δc^a."""
    vx = var_x(p)
    c_x, c_e, c_eta = _flow_loadings(
        h, p.rho, p.phi_e, p.sigma, 1.0, 1.0, shift=0, n_periods=4 * h
    )
    y_x, y_e, y_own = _flow_loadings(
        h, p.rho, p.phi_e, p.sigma, phi_x, phi_shock, shift=0, n_periods=4 * h
    )

    def cov_same(x1, e1, o1, x2, e2, o2, rho_cross: float) -> float:
        return (
            x1 * x2 * vx
            + float(e1 @ e2)
            + rho_cross * float(o1 @ o2)
        )

    # For consumption, own shock is η so rho_own_eta=1 with itself.
    var_c = cov_same(c_x, c_e, c_eta, c_x, c_e, c_eta, 1.0)
    var_y = cov_same(y_x, y_e, y_own, y_x, y_e, y_own, 1.0)
    cov_cy = (
        c_x * y_x * vx
        + float(c_e @ y_e)
        + rho_own_eta * float(c_eta @ y_own)
    )

    c1_x, c1_e, c1_eta = _flow_loadings(
        h, p.rho, p.phi_e, p.sigma, 1.0, 1.0, shift=h, n_periods=4 * h
    )
    y1_x, y1_e, y1_own = _flow_loadings(
        h, p.rho, p.phi_e, p.sigma, phi_x, phi_shock, shift=h, n_periods=4 * h
    )
    c2_x, c2_e, c2_eta = _flow_loadings(
        h, p.rho, p.phi_e, p.sigma, 1.0, 1.0, shift=2 * h, n_periods=4 * h
    )
    y2_x, y2_e, y2_own = _flow_loadings(
        h, p.rho, p.phi_e, p.sigma, phi_x, phi_shock, shift=2 * h, n_periods=4 * h
    )

    ac1_c = cov_same(c_x, c_e, c_eta, c1_x, c1_e, c1_eta, 1.0) / var_c
    ac2_c = cov_same(c_x, c_e, c_eta, c2_x, c2_e, c2_eta, 1.0) / var_c
    ac1_y = cov_same(y_x, y_e, y_own, y1_x, y1_e, y1_own, 1.0) / var_y
    return {
        "var_c": var_c,
        "var_y": var_y,
        "cov_cy": cov_cy,
        "ac1_c": ac1_c,
        "ac2_c": ac2_c,
        "ac1_y": ac1_y,
    }


def _geom(a: float, n: int) -> float:
    if n <= 0:
        return 0.0
    if abs(a - 1.0) < 1e-15:
        return float(n)
    return (1.0 - a**n) / (1.0 - a)


def _pi_q(p: BKYParams, h: int) -> tuple[float, np.ndarray]:
    rho = p.rho
    q = np.zeros(h + 1)
    if h == 1 or abs(rho - 1.0) < 1e-15:
        return 0.0, q
    den = 1.0 - rho
    pi = (p.phi_d / (h * den)) * (rho * _geom(rho, h - 1) - (h - 1) * rho**h)
    for j in range(1, h + 1):
        q[j] = (p.phi_d / (h * (rho ** (j - 1)) * den)) * (
            _geom(rho, h - 1)
            - (h - 1) * rho ** (h - 1)
            - _geom(rho, j - 1)
            + (j - 1) * rho ** (j - 1)
        )
    return float(pi), q


def _zd_moments(p: BKYParams, sol: LogLinearSolution, h: int) -> dict[str, float]:
    """Year-end affine P/D plus trailing-dividend noise.

    Intra-year e and w shocks already sit in year-end ``x_t`` and
    ``σ²_t``, so they are not added again. The remaining noise is the
    residual dividend sum in the annual P/D definition.
    """
    A0, A1, A2 = sol.A_d0, sol.A_d1, sol.A_d2
    vx, vs = var_x(p), var_sigma2(p)
    mean = A0 + A2 * p.sigma**2 - np.log(max(h, 1)) - 0.5 * p.mu_d * (h - 1)
    var = A1**2 * vx + A2**2 * vs
    for j in range(1, h):
        var += ((h - j) / h * p.phi_d_sigma * p.sigma) ** 2
    acov = A1**2 * (p.rho**h) * vx + A2**2 * (p.nu**h) * vs
    ac1 = acov / var if var > 0 else 0.0
    return {
        "mean_zd": float(mean),
        "vol_zd": float(np.sqrt(max(var, 0.0))),
        "ac1_zd": float(ac1),
        "var_zd": float(var),
    }


def _rf_moments(p: BKYParams, sol: LogLinearSolution, h: int) -> dict[str, float]:
    F0, F1, F2 = sol.F
    vx, vs = var_x(p), var_sigma2(p)
    mean = h * (F0 + F2 * p.sigma**2)
    s_rho = _geom(p.rho, h)
    s_nu = _geom(p.nu, h)
    var = (F1 * s_rho) ** 2 * vx + (F2 * s_nu) ** 2 * vs
    for j in range(1, h):
        var += (F1 * p.phi_e * _geom(p.rho, h - j)) ** 2 * p.sigma**2
        var += (F2 * _geom(p.nu, h - j)) ** 2 * p.sigma_w**2
    return {"mean_rf": float(mean), "vol_rf": float(np.sqrt(max(var, 0.0))), "var_rf": float(var)}


def _rd_moments(p: BKYParams, sol: LogLinearSolution, h: int) -> dict[str, float]:
    B0, B1, B2 = sol.B_d
    bu, be, bw = sol.beta_d
    vx, vs = var_x(p), var_sigma2(p)
    mean = h * (B0 + B2 * p.sigma**2)
    s_rho = _geom(p.rho, h)
    s_nu = _geom(p.nu, h)
    var = (B1 * s_rho) ** 2 * vx + (B2 * s_nu) ** 2 * vs
    for j in range(1, h + 1):
        var += (B1 * p.phi_e * _geom(p.rho, h - j) + be) ** 2 * p.sigma**2
        var += (B2 * _geom(p.nu, h - j) + bw) ** 2 * p.sigma_w**2
    var += h * (bu * p.sigma) ** 2
    lam = sol.Lambda
    b_eta = p.phi_d_sigma * p.rho_d
    prem = (
        lam[0] * p.sigma**2 * b_eta
        + lam[1] * p.sigma**2 * be
        + lam[2] * p.sigma_w**2 * bw
    )
    return {
        "mean_rd": float(mean),
        "vol_rd": float(np.sqrt(max(var, 0.0))),
        "var_rd": float(var),
        "mean_excess": float(h * prem),
    }


def _predictability(
    p: BKYParams,
    sol: LogLinearSolution,
    h: int,
    var_c: float,
    var_rd: float,
    var_zd: float,
    c_x: float,
) -> dict[str, float]:
    """corr(r_d^a, z_{d,-1}^a) and corr(Δc^a, z_{d,-1}^a)."""
    A1, A2 = sol.A_d1, sol.A_d2
    B1, B2 = sol.B_d[1], sol.B_d[2]
    vx, vs = var_x(p), var_sigma2(p)
    c_e_full = _flow_loadings(
        h, p.rho, p.phi_e, p.sigma, 1.0, 1.0, shift=0, n_periods=2 * h
    )[1]
    # z_{τ-1} is year-end of the previous year: x_{t-h}, σ²_{t-h}.
    # Cov(Δc^a, z^a) = A1 * Cov(Δc^a, x_{t-h}); the second factor is the
    # loading on x_{t-2h} plus the e-shock overlap of the 2h-window Δc
    # with the h shocks that build x_{t-h} from x_{t-2h}.
    cov_cx = c_x * (p.rho**h) * vx
    if h >= 1:
        load_x_end = np.array(
            [p.rho ** (h - i) * p.phi_e * p.sigma for i in range(1, h + 1)]
        )
        cov_cx += float(c_e_full[:h] @ load_x_end)
    cov_cz = A1 * cov_cx
    cov_rz = B1 * _geom(p.rho, h) * A1 * vx
    cov_rz += B2 * _geom(p.nu, h) * A2 * vs
    corr_cz = cov_cz / np.sqrt(var_c * var_zd) if var_c > 0 and var_zd > 0 else 0.0
    corr_rz = cov_rz / np.sqrt(var_rd * var_zd) if var_rd > 0 and var_zd > 0 else 0.0
    return {"corr_dc_zd": float(corr_cz), "corr_rd_zd": float(corr_rz)}


def _a_j(rho: float, h: int, j: int) -> float:
    """WP p.12: a_j coefficient on lagged expected-growth shocks."""
    if j < 1:
        return 0.0
    den = 1.0 - rho
    if abs(den) < 1e-15:
        return 0.0
    scale = 1.0 / (h * (rho ** (j - 1)))
    return scale * (
        (1.0 - rho**h) / den
        - (1.0 / den) * ((1.0 - rho ** (j - 1)) / den - (j - 1) * rho ** (j - 1))
    )


def _b_j(rho: float, h: int, j: int) -> float:
    den = 1.0 - rho
    if abs(den) < 1e-15:
        return 0.0
    return (1.0 / (h * (rho ** (j - 1)))) * (j - rho * (1.0 - rho**j) / den)


def model_moments(
    params: BKYParams,
    h: int,
    sol: LogLinearSolution | None = None,
) -> dict[str, float]:
    """Unconditional time-aggregated moments at ``h`` decision periods per sample."""
    p = params
    if sol is None:
        sol = solve_loglinear(p)
    flows = _second_moments_flow(
        p, h, phi_x=p.phi_d, phi_shock=p.phi_d_sigma, rho_own_eta=p.rho_d
    )
    zd = _zd_moments(p, sol, h)
    rf = _rf_moments(p, sol, h)
    rd = _rd_moments(p, sol, h)
    c_x, _, _ = _flow_loadings(h, p.rho, p.phi_e, p.sigma, 1.0, 1.0)
    pred = _predictability(
        p, sol, h, flows["var_c"], rd["var_rd"], zd["var_zd"], c_x
    )
    return {
        "mean_dc": float(h * p.mu_c),
        "vol_dc": float(np.sqrt(max(flows["var_c"], 0.0))),
        "ac1_dc": float(flows["ac1_c"]),
        "ac2_dc": float(flows["ac2_c"]),
        "mean_dd": float(h * p.mu_d),
        "vol_dd": float(np.sqrt(max(flows["var_y"], 0.0))),
        "ac1_dd": float(flows["ac1_y"]),
        "corr_dc_dd": float(
            flows["cov_cy"] / np.sqrt(flows["var_c"] * flows["var_y"])
            if flows["var_c"] > 0 and flows["var_y"] > 0
            else 0.0
        ),
        **zd,
        **rf,
        **rd,
        **pred,
        "mean_excess_log": float(rd["mean_rd"] - rf["mean_rf"]),
    }
