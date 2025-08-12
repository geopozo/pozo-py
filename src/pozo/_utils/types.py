"""All custom types."""

from __future__ import annotations

from typing import Any, Protocol, TypedDict, Union

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
        "si unit": list[Union[str, None]],
        "pint unit": list[Union[pint.Unit, None]],
        "confidence": list[Union[int, None]],
        "comment": list[str],
        "description": list[str],
        "min": list[str],
        "med": list[str],
        "max": list[str],
        "#NaN": list[Union[int, None]],
    },
)
