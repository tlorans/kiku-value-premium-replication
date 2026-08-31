"""Asset-pricing implications: population moments, simulation, figures.

The documented way in is :meth:`lrrcs.LongRunRisksModel.solve` and
:meth:`lrrcs.LongRunRisksModel.simulate`; the names here are the
machinery behind them.
"""
from .moments import claim_stats, compute_asset_pricing_moments, residual_correlation
from .figures import figure5, figure_lr_premium, figure_mean_pd
from .simulation import simulate_table_vii

__all__ = [
    "compute_asset_pricing_moments",
    "residual_correlation",
    "claim_stats",
    "simulate_table_vii",
    "figure_lr_premium",
    "figure_mean_pd",
    "figure5",
]
