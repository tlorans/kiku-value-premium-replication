"""
Kiku (2006) Value Premium Puzzle Replication Package

Long-run risks model of Bansal-Yaron with Epstein-Zin preferences
to explain the value premium via differential exposure to long-run consumption risks.
"""

__version__ = "0.1.0"

from .params import ModelParams, get_default_params
from .preferences import EpsteinZinPreferences

__all__ = ["ModelParams", "get_default_params", "EpsteinZinPreferences"]
