from typing import Any, Protocol, TypeAlias

Array: TypeAlias = Any  # temporal


class Curve(Protocol):
    @property
    def mnemonic(self) -> str: ...
    @property
    def unit(self) -> str: ...
    @property
    def data(self) -> Array | None: ...
