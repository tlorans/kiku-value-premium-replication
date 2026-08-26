START = 1930
END = 2003
FIGURE2_START = 1952

# Table I Panel A: (printed, Newey-West SE, 8 lags). Returns and growth in percent.
TABLE_I = {
    "Growth": {
        "ret_mean": (7.81, 1.98),
        "ret_sd": (20.2, 2.00),
        "dg_mean": (0.68, 1.25),
        "dg_sd": (13.9, 2.24),
        "log_pd": (3.61, 0.18),
    },
    "Value": {
        "ret_mean": (13.88, 1.74),
        "ret_sd": (29.9, 4.34),
        "dg_mean": (3.63, 3.06),
        "dg_sd": (18.1, 2.69),
        "log_pd": (3.25, 0.12),
    },
    "Market": {
        "ret_mean": (8.56, 1.79),
        "ret_sd": (20.1, 2.23),
        "dg_mean": (0.85, 0.95),
        "dg_sd": (10.9, 2.41),
        "log_pd": (3.34, 0.13),
    },
}
TABLE_I_CORR_RET = {
    ("Growth", "Value"): (0.75, 0.05),
    ("Growth", "Market"): (0.95, 0.01),
    ("Value", "Market"): (0.87, 0.04),
}
TABLE_I_CORR_DG = {
    ("Growth", "Value"): (0.32, 0.17),
    ("Growth", "Market"): (0.80, 0.09),
    ("Value", "Market"): (0.53, 0.10),
}
TABLE_III_DATA = {
    "mean": (1.96, 0.32),
    "sd": (2.20, 0.45),
    "ac1": (0.44, 0.12),
    "ac2": (0.16, 0.15),
}
# Table VI uses 4 lags
TABLE_VI_PHI = {
    "Growth": (-0.38, 1.34),
    "Value": (2.16, 1.44),
    "Market": (0.66, 1.20),
}
TABLE_VI_INNOV = {
    "Growth": (0.37, 0.14),
    "Value": (0.30, 0.07),
    "Market": (0.58, 0.15),
}

CASHFLOW_NOTE = (
    "Campbell–Shiller D_t = (ret − retx) V_{t−1} is zero for the 1933 Value "
    "quintile because every month has ret == retx (no ordinary dividend). "
    "That year pd and dgrowth are NaN; the 1931–32 collapse and 1935–36 rebound "
    "then put Value dg_sd, the Value–Market Δd correlation, Value φ̃, and Value "
    "innov_corr outside the printed SE. Those four cells are ranking/sign checks, "
    "not the hard SE gate. Printed goldens are unchanged."
)
