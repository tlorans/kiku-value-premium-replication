"""
Monte-Carlo simulation and annual aggregation for moment matching
(Tables III–V of the paper).
"""
from __future__ import annotations
import numpy as np
from .model.params import ModelParams, get_default_params
from .model.dynamics import Dynamics


def annualize(monthly: np.ndarray) -> np.ndarray:
    """Sum of log-growths over 12 months (approx annual growth)."""
    T = len(monthly)
    n_years = T // 12
    return monthly[: n_years * 12].reshape(n_years, 12).sum(axis=1)


def simulate_moments(n_sims: int = 200, years: int = 74, seed: int = 42,
                     params: ModelParams | None = None) -> dict:
    """
    Run n_sims paths of length years*12, aggregate to annual, return average
    moments that can be compared with Tables III–V.
    """
    if params is None:
        params = get_default_params()
    dyn = Dynamics(params, seed=seed)

    cons_means, cons_vols, cons_ac1 = [], [], []
    div_means = {k: [] for k in ["growth", "value", "market"]}
    div_vols = {k: [] for k in ["growth", "value", "market"]}
    div_ac1 = {k: [] for k in ["growth", "value", "market"]}
    corr_c_d = {k: [] for k in ["growth", "value", "market"]}

    T = years * 12
    for s in range(n_sims):
        path = dyn.simulate_cashflows(T)
        dc_a = annualize(path["dc"])
        cons_means.append(dc_a.mean() * 100)  # percent
        cons_vols.append(dc_a.std() * 100)
        if len(dc_a) > 1:
            cons_ac1.append(np.corrcoef(dc_a[:-1], dc_a[1:])[0, 1])

        for name in ["growth", "value", "market"]:
            dd_a = annualize(path[f"dd_{name}"])
            div_means[name].append(dd_a.mean() * 100)
            div_vols[name].append(dd_a.std() * 100)
            if len(dd_a) > 1:
                div_ac1[name].append(np.corrcoef(dd_a[:-1], dd_a[1:])[0, 1])
            if len(dc_a) == len(dd_a):
                corr_c_d[name].append(np.corrcoef(dc_a, dd_a)[0, 1])

    def avg(lst):
        return float(np.mean(lst)) if lst else np.nan

    return {
        "consumption": {
            "E[dc]": avg(cons_means),
            "sigma(dc)": avg(cons_vols),
            "AC1": avg(cons_ac1),
        },
        "dividends": {
            name: {
                "E[dd]": avg(div_means[name]),
                "sigma(dd)": avg(div_vols[name]),
                "AC1": avg(div_ac1[name]),
                "corr(dc,dd)": avg(corr_c_d[name]),
            }
            for name in ["growth", "value", "market"]
        },
    }


def print_moments(moments: dict) -> None:
    print("Model-implied annual moments (compare to Tables III–IV):")
    c = moments["consumption"]
    print(f"  Consumption: E={c['E[dc]']:.2f}%, vol={c['sigma(dc)']:.2f}%, AC1={c['AC1']:.2f}")
    for name, m in moments["dividends"].items():
        print(f"  {name:8s}: E={m['E[dd]']:.2f}%, vol={m['sigma(dd)']:.2f}%, "
              f"AC1={m['AC1']:.2f}, corr(c,d)={m['corr(dc,dd)']:.2f}")
