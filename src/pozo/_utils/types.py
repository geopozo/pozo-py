"""All custom types."""

from __future__ import annotations

from typing import Any, Protocol, TypedDict

import pint

Array = Any  # temporal


class Curve(Protocol):
    """Protocol with curve properties."""

    @property
    def mnemonic(self) -> str: ...
    @property
    def unit(self) -> str: ...
    @property
    def data(self) -> Array | None: ...


CurveData = TypedDict(
    "CurveData",
    {
        "mnemonic": list[str],
        "las unit": list[str],
        "si unit": list[str | None],
        "pint unit": list[pint.Unit | None],
        "confidence": list[int | None],
        "comment": list[str | None],
        "description": list[str],
        "min": list[str | None],
        "med": list[str | None],
        "max": list[str | None],
        "#NaN": list[int | None],
    },
)
