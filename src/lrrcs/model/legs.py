"""Resolve long, short, and market claims from a dividend dictionary.

Paper keys ``value`` / ``growth`` / ``market`` remain valid. Further
applications pass ``long`` / ``short`` (and optionally ``market``) instead
of renaming a profitability or size leg ``value``.
"""
from __future__ import annotations

from typing import Any, Iterable, Mapping, NamedTuple

ROLE_ALIASES = {
    "long": ("long", "value"),
    "short": ("short", "growth"),
    "market": ("market",),
}


class Legs(NamedTuple):
    """The claim names playing the long, short, and market roles.

    ``market`` is ``None`` when the model prices no market claim.
    """

    long: str
    short: str
    market: str | None


def resolve_legs(
    claims: Mapping[str, Any] | Iterable[str],
    long: str | None = None,
    short: str | None = None,
    market: str | None = None,
) -> tuple[str, str, str | None]:
    """Return ``(long_key, short_key, market_key)``.

    ``market_key`` is ``None`` if no market series is present and none was
    named. Raises ``KeyError`` if the long or short leg cannot be resolved.
    """
    keys = set(claims if isinstance(claims, Mapping) else claims)

    def pick(role: str, explicit: str | None, required: bool) -> str | None:
        if explicit is not None:
            if explicit not in keys:
                raise KeyError(
                    f"{role}={explicit!r} is not among the claims {sorted(keys)}."
                )
            return explicit
        for alias in ROLE_ALIASES[role]:
            if alias in keys:
                return alias
        if required:
            aliases = " or ".join(repr(a) for a in ROLE_ALIASES[role])
            raise KeyError(
                f"No {role} claim in {sorted(keys)}. "
                f"Pass {role}='...' or name a series {aliases}."
            )
        return None

    return pick("long", long, True), pick("short", short, True), pick(
        "market", market, False
    )
