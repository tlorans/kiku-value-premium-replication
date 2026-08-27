"""Long-run risks in the time series and the cross section.

Companion to tidyfinance. Documented import::

    import tidyfinance as tf
    import lrrcs as lrr
"""

from __future__ import annotations

import importlib
import pkgutil
import types

__version__ = "0.5.0"

_EXCLUDE = {"annotations"}
__all__: list[str] = []
_seen: set[str] = set()

if "__path__" in globals():
    for _finder, _module_name, _ispkg in pkgutil.iter_modules(__path__):
        if _module_name.startswith("_"):
            continue
        _module = importlib.import_module(f".{_module_name}", package=__name__)
        for _name in dir(_module):
            if _name.startswith("__") and _name.endswith("__"):
                continue
            if _name.startswith("_"):
                continue
            if _name in _EXCLUDE or _name in _seen:
                continue
            _obj = getattr(_module, _name)
            if not isinstance(_obj, (types.FunctionType, type)):
                continue
            if not getattr(_obj, "__module__", "").startswith(__name__):
                continue
            globals()[_name] = _obj
            __all__.append(_name)
            _seen.add(_name)

del importlib, pkgutil, types
del _seen
for _leaked in (
    "_finder",
    "_ispkg",
    "_module_name",
    "_module",
    "_name",
    "_obj",
    "_leaked",
):
    globals().pop(_leaked, None)
