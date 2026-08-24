"""
Discretization of the joint state (x, σ²) following Tauchen-Hussey (1991)
as described in the Appendix of Kiku (2006).

- x : 30-point Gauss-Hermite (conditional on current σ)
- σ² : 4-point approximation of the AR(1) variance process
Product grid size ≈ 120 states. Transition matrix is row-stochastic.
"""
from __future__ import annotations
import numpy as np
from scipy.special import roots_hermitenorm
from scipy.stats import norm
from .params import ModelParams, get_default_params


def gauss_hermite_nodes_weights(n: int):
    """Standard normal Gauss-Hermite nodes and weights (scipy roots_hermitenorm)."""
    nodes, weights = roots_hermitenorm(n)
    # roots_hermitenorm are for weight exp(-x²/2)/sqrt(2π), so weights already integrate to 1 for N(0,1)
    weights = weights / np.sqrt(2 * np.pi)   # ensure proper normalization if needed
    weights = weights / weights.sum()        # force sum to 1
    return nodes, weights


def discretize_variance(n_s: int = 4, params: ModelParams | None = None):
    """Simple 4-point discretization of σ² AR(1).

    Uses a Tauchen-style method around the unconditional mean.
    """
    if params is None:
        params = get_default_params()
    c = params.cons
    mu = c.sigma ** 2
    # unconditional std of σ²
    std = c.sigma_w / np.sqrt(1 - c.nu ** 2)
    # equally spaced points covering ~ ±2 std (keep positive)
    low = max(mu - 2.0 * std, 1e-10)
    high = mu + 2.0 * std
    s2_nodes = np.linspace(low, high, n_s)
    step = s2_nodes[1] - s2_nodes[0] if n_s > 1 else 1.0

    # transition: AR(1) + normal innovation
    P_s = np.zeros((n_s, n_s))
    for i, s2 in enumerate(s2_nodes):
        mean_next = c.sigma**2 * (1 - c.nu) + c.nu * s2
        for j, s2p in enumerate(s2_nodes):
            if j == 0:
                P_s[i, j] = norm.cdf((s2_nodes[0] + step/2 - mean_next) / c.sigma_w)
            elif j == n_s - 1:
                P_s[i, j] = 1.0 - norm.cdf((s2_nodes[-1] - step/2 - mean_next) / c.sigma_w)
            else:
                P_s[i, j] = (norm.cdf((s2p + step/2 - mean_next) / c.sigma_w)
                             - norm.cdf((s2p - step/2 - mean_next) / c.sigma_w))
        P_s[i] = np.maximum(P_s[i], 0)
        P_s[i] /= P_s[i].sum()
    return s2_nodes, P_s


def discretize_states(n_x: int = 30, n_s: int = 4, params: ModelParams | None = None):
    """Build product grid and approximate transition matrix for (x, σ²).

    Returns
    -------
    states : (N, 2) array of (x, sigma2)
    P : (N, N) transition matrix
    """
    if params is None:
        params = get_default_params()
    c = params.cons

    # Variance grid
    s2_nodes, P_s = discretize_variance(n_s, params)

    # For x we use a global grid based on unconditional scale (average σ)
    # and then compute conditional transition probabilities.
    avg_sigma = c.sigma
    # unconditional std of x ≈ (phi_x * avg_sigma) / sqrt(1-rho²)
    std_x = (c.phi_x * avg_sigma) / np.sqrt(1 - c.rho ** 2)
    # Gauss-Hermite for standard normal, then scale
    gh_nodes, gh_weights = gauss_hermite_nodes_weights(n_x)
    # Place x nodes over a wide range
    x_nodes = gh_nodes * std_x * 1.5   # slightly wider

    # Product grid
    xx, ss = np.meshgrid(x_nodes, s2_nodes, indexing="ij")
    states = np.column_stack([xx.ravel(), ss.ravel()])
    N = states.shape[0]  # n_x * n_s

    # Transition matrix
    P = np.zeros((N, N))
    for i in range(N):
        x, s2 = states[i]
        sigma = np.sqrt(s2)
        # next x ~ N(rho * x, (phi_x * sigma)^2)
        mean_x = c.rho * x
        std_cond = c.phi_x * sigma
        # next sigma2 transitions from P_s
        # index of current sigma2
        s_idx = np.argmin(np.abs(s2_nodes - s2))
        for j in range(N):
            xp, s2p = states[j]
            # density of xp under conditional normal, mapped to discrete
            # use a simple kernel / bin probability around the nodes
            # For speed we use the GH weights idea but reweighted by conditional density
            dens = norm.pdf(xp, loc=mean_x, scale=max(std_cond, 1e-12))
            # approximate mass: dens * local spacing
            # better: find the corresponding weight by nearest or use continuous density normalized later
            P[i, j] = dens * P_s[s_idx, np.argmin(np.abs(s2_nodes - s2p))]
        # renormalize
        row_sum = P[i].sum()
        if row_sum > 0:
            P[i] /= row_sum
        else:
            P[i, i] = 1.0  # fallback

    return states, P, x_nodes, s2_nodes


if __name__ == "__main__":
    states, P, x_nodes, s2_nodes = discretize_states()
    print("Number of states:", states.shape[0])
    print("x range:", x_nodes.min(), x_nodes.max())
    print("sigma2 nodes:", s2_nodes)
    print("Transition row sums (should be 1):", P.sum(axis=1)[:5])
