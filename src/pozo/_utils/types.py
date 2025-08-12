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
        "si unit": list[str],
        "pint unit": list[Union[pint.Unit, str]],  # para pint.unit y que None sea ""
        "confidence": list[int],
        "comment": list[str],
        "description": list[str],
        "min": list[str],
        "med": list[str],
        "max": list[str],
        "#NaN": list[int],
    },
)
