from typing import Any, Protocol, TypeAlias

from pint import Unit

Array: TypeAlias = Any


class Curve(Protocol):
    @property
    def mnemonic(self) -> str: ...
    @property
    def unit(self) -> str | Unit | None: ...
    @property
    def data(self) -> Array | None: ...
