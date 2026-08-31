"""Exact Table II dividend-process parameters (bottom panel)."""
from __future__ import annotations
from typing import Dict
from ..model.params import ClaimParams


# Exact values from Table II (bottom panel)
TABLE_II_DIVIDENDS = {
    "growth": dict(mu=0.0009, phi=2.6, phi_sigma=8.4, alpha=0.27),
    "value":  dict(mu=0.0019, phi=6.2, phi_sigma=7.4, alpha=0.15),
    "market": dict(mu=0.0012, phi=2.8, phi_sigma=7.5, alpha=0.55),
}


def get_table_ii_claims() -> Dict[str, ClaimParams]:
    """Return the exact ClaimParams used in the paper (Table II)."""
    return {name: ClaimParams(**kwargs) for name, kwargs in TABLE_II_DIVIDENDS.items()}
