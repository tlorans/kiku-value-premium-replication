"""Printed Bansal, Kiku, and Yaron (2016, JME) tables.

These are the paper's numbers, not the package's output. Tests compare
the reconstruction and the closed forms to these cells.
"""
from __future__ import annotations

from .solution import BKYParams

START = 1930
END = 2015
QUARTERLY_START = 1948

# Table 1, annual 1930–2015.
TABLE_1 = {
    "dc_mean": 0.018,
    "dc_std": 0.02,
    "dd_mean": 0.014,
    "dd_std": 0.11,
    "rm_mean": 0.081,
    "rm_std": 0.19,
    "log_pd_mean": 3.404,
    "log_pd_std": 0.45,
    "rf_mean": 0.005,
    "rf_std": 0.03,
}

# Table 2, LRR column (decision-frequency parameters).
TABLE_2_LRR = BKYParams(
    gamma=9.67,
    psi=2.18,
    delta=0.9990,
    mu_c=0.0016,
    rho=0.9762,
    phi_e=0.0318,
    sigma=0.0070,
    nu=0.9984,
    sigma_w=2.12e-6,
    mu_d=0.0027,
    phi_d=4.51,
    phi_d_sigma=4.65,
    rho_d=0.51,
)
TABLE_2_LRR_H = 11

# Table 2 LRR standard errors (block bootstrap, eight-year blocks).
TABLE_2_SE = {
    "gamma": 1.44,
    "psi": 0.21,
    "delta": 0.0001,
    "mu_c": 0.0005,
    "rho": 0.0035,
    "phi_e": 0.0053,
    "sigma": 0.0009,
    "nu": 0.0007,
    "sigma_w": 5.32e-7,
    "mu_d": 0.0010,
    "phi_d": 0.45,
    "phi_d_sigma": 0.48,
    "rho_d": 0.10,
    "h": 2.16,
}

# Bansal–Yaron (2004) / Kiku (2006) Table II monthly values. Not Table 2.
COLD_START = BKYParams(
    gamma=10.0,
    psi=1.5,
    delta=0.999,
    mu_c=0.0015,
    rho=0.98,
    phi_e=0.032,
    sigma=0.0064,
    nu=0.99,
    sigma_w=1.7e-6,
    mu_d=0.0012,
    phi_d=2.8,
    phi_d_sigma=7.5,
    rho_d=0.55,
)

# Table 3 sample column plus Table 1 means (the GMM targets).
TABLE_3_SAMPLE = {
    "mean_dc": 0.018,
    "vol_dc": 0.021,
    "ac1_dc": 0.472,
    "ac2_dc": 0.184,
    "mean_dd": 0.014,
    "vol_dd": 0.111,
    "ac1_dd": 0.189,
    "corr_dc_dd": 0.508,
    "mean_zd": 3.404,
    "vol_zd": 0.450,
    "ac1_zd": 0.859,
    "mean_excess": 0.075,
    "vol_rd": 0.194,
    "mean_rf": 0.005,
    # corr(r_d, z_{d,-1}) is the lagged predictability correlation of
    # returns with the price-dividend ratio, which is negative in both
    # the sample and the LRR model (Table 3).
    "corr_rd_zd": -0.165,
    "corr_dc_zd": 0.176,
}

# Table 2, No-Vol column. ν and σ_w are shut off.
TABLE_2_NOVOL = BKYParams(
    gamma=7.98,
    psi=2.28,
    delta=0.9987,
    mu_c=0.0016,
    rho=0.9796,
    phi_e=0.0399,
    sigma=0.0081,
    nu=0.0,
    sigma_w=0.0,
    mu_d=0.0025,
    phi_d=4.77,
    phi_d_sigma=4.44,
    rho_d=0.41,
)
TABLE_2_NOVOL_H = 9

# Table 4 / Table 6 annual column (h = 1, no time aggregation).
TABLE_4_ANNUAL = BKYParams(
    gamma=13.83,
    psi=1.05,
    delta=0.9944,
    mu_c=0.0141,
    rho=0.8741,
    phi_e=0.1661,
    sigma=0.0241,
    nu=0.9220,
    sigma_w=3.49e-6,
    mu_d=0.0107,
    phi_d=2.51,
    phi_d_sigma=5.12,
    rho_d=0.60,
)

# Table 6 fixed-h specifications.
TABLE_6 = {
    26: BKYParams(
        gamma=6.54, psi=2.44, delta=0.9996,
        mu_c=0.0005, rho=0.9946, phi_e=0.0090, sigma=0.0055,
        nu=0.9989, sigma_w=1.21e-6,
        mu_d=0.0008, phi_d=4.32, phi_d_sigma=5.00, rho_d=0.49,
    ),
    12: BKYParams(
        gamma=8.12, psi=2.45, delta=0.9990,
        mu_c=0.0016, rho=0.9753, phi_e=0.0340, sigma=0.0064,
        nu=0.9981, sigma_w=3.56e-6,
        mu_d=0.0026, phi_d=4.23, phi_d_sigma=5.55, rho_d=0.54,
    ),
    4: BKYParams(
        gamma=11.66, psi=1.82, delta=0.9965,
        mu_c=0.0024, rho=0.9682, phi_e=0.0395, sigma=0.0116,
        nu=0.9978, sigma_w=6.07e-6,
        mu_d=0.0059, phi_d=4.89, phi_d_sigma=4.80, rho_d=0.46,
    ),
    1: TABLE_4_ANNUAL,
}

# Table 5, annual-specification model column.
TABLE_5_ANNUAL_MODEL = {
    "vol_dc": 0.025,
    "ac1_dc": 0.092,
    "vol_zd": 0.083,
    "mean_excess": 0.040,
    "vol_rd": 0.130,
    "mean_rf": 0.011,
}

# Table 7 Panel A.
TABLE_7_MU = {"small": 0.0048, "large": 0.0021, "growth": 0.0027, "value": 0.0050}
TABLE_7_PHI = {"small": 10.69, "large": 4.70, "growth": 5.33, "value": 7.51}
TABLE_7_PHI_SIGMA = {"small": 10.42, "large": 5.83, "growth": 6.09, "value": 7.51}
TABLE_7_RHO = {"small": 0.41, "large": 0.40, "growth": 0.20, "value": 0.61}
TABLE_7_PREMIA_DATA = {"small": 13.61, "large": 7.12, "growth": 7.03, "value": 12.38}
TABLE_7_PREMIA_MODEL = {"small": 13.93, "large": 6.52, "growth": 6.65, "value": 11.46}
TABLE_7_CAPM = {
    "small_large": {"beta_data": 0.59, "beta_model": 0.86, "alpha_data": 2.07, "alpha_model": 1.63},
    "value_growth": {"beta_data": 0.30, "beta_model": 0.45, "alpha_data": 3.13, "alpha_model": 1.78},
}

# Table 8, post-war quarterly.
TABLE_8_TA = BKYParams(
    gamma=7.45, psi=2.02, delta=0.9987,
    mu_c=0.0013, rho=0.9861, phi_e=0.0504, sigma=0.0041,
    nu=0.9909, sigma_w=2.92e-6,
    mu_d=0.0027, phi_d=4.29, phi_d_sigma=5.11, rho_d=0.03,
)
TABLE_8_H = 2
TABLE_8_NO_TA = BKYParams(
    gamma=8.66, psi=2.83, delta=0.9981,
    mu_c=0.0041, rho=0.9766, phi_e=0.0785, sigma=0.0034,
    nu=0.9945, sigma_w=1.68e-6,
    mu_d=0.0020, phi_d=6.50, phi_d_sigma=5.39, rho_d=0.01,
)

# Table 3, LRR model column (annual moments at Table 2).
TABLE_3_LRR_MODEL = {
    "vol_dc": 0.022,
    "ac1_dc": 0.395,
    "ac2_dc": 0.159,
    "vol_dd": 0.101,
    "ac1_dd": 0.388,
    "corr_dc_dd": 0.625,
    "mean_zd": 3.409,
    "vol_zd": 0.423,
    "ac1_zd": 0.929,
    "mean_excess": 0.067,
    "vol_rd": 0.173,
    "mean_rf": 0.010,
    "corr_rd_zd": -0.088,
    "corr_dc_zd": 0.240,
}

# Table 3, No-Vol model column (the same sample moments, a model with no
# stochastic volatility). corr(r_d, z_{d,-1}) flips sign relative to the
# LRR model because the volatility channel is absent.
TABLE_3_NOVOL_MODEL = {
    "vol_dc": 0.024,
    "ac1_dc": 0.461,
    "ac2_dc": 0.247,
    "vol_dd": 0.110,
    "ac1_dd": 0.482,
    "corr_dc_dd": 0.614,
    "mean_zd": 3.366,
    "vol_zd": 0.320,
    "ac1_zd": 0.814,
    "mean_excess": 0.067,
    "vol_rd": 0.204,
    "mean_rf": 0.010,
    "corr_rd_zd": 0.028,
    "corr_dc_zd": 0.593,
}
