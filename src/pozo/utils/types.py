"""All custom types."""

from __future__ import annotations

from typing import Any, Protocol

Array = Any  # temporal


class Curve(Protocol):
    """Protocol with curve properties."""

    @property
    def mnemonic(self) -> str: ...  # noqa: D102
    @property
    def unit(self) -> str: ...  # noqa: D102
    @property
    def data(self) -> Array | None: ...  # noqa: D102
