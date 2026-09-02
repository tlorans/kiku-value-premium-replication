"""Convert frames at the geap public boundary.

Honor tidyfinance.get_backend(). Do not import tidyfinance.backend privates.
"""
from __future__ import annotations

from functools import wraps
from typing import Any, Callable


def get_active_backend() -> str:
    import tidyfinance as tf
    return tf.get_backend()


def to_pandas(obj: Any) -> Any:
    to_pd = getattr(obj, "to_pandas", None)
    if callable(to_pd):
        return to_pd()
    return obj


def to_polars(obj: Any) -> Any:
    import pandas as pd
    import polars as pl
    if isinstance(obj, (pl.DataFrame, pl.Series)):
        return obj
    if isinstance(obj, pd.DataFrame):
        return pl.from_pandas(obj)
    if isinstance(obj, pd.Series):
        name = obj.name if obj.name is not None else "value"
        return pl.from_pandas(obj.rename(name).to_frame())[name]
    return obj


def to_backend(obj: Any, backend: str | None = None) -> Any:
    backend = backend or get_active_backend()
    if backend == "polars":
        return to_polars(obj)
    return to_pandas(obj)


def use_backend(fn: Callable) -> Callable:
    @wraps(fn)
    def wrapped(*args, **kwargs):
        args = tuple(to_pandas(a) for a in args)
        kwargs = {k: to_pandas(v) for k, v in kwargs.items()}
        return to_backend(fn(*args, **kwargs))
    return wrapped
