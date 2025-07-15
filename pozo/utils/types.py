from __future__ import annotations

from typing import Any, Protocol, TypeAlias, TypedDict

Array: TypeAlias = Any  # temporal


class Curve(Protocol):
    """Protocol with curve properties."""

    @property
    def mnemonic(self) -> str: ...  # noqa: D102
    @property
    def unit(self) -> str: ...  # noqa: D102
    @property
    def data(self) -> Array | None: ...  # noqa: D102


class Diagnosis(TypedDict):
    """Custom Dict type for diagnosis of las to si."""

    mnemonic: str
    las_unit: str
    data: Array | None
    confidence: int
    comment: str
    si_unit: str
    v_min: str
    v_med: str
    v_max: str
    n_nan: int
