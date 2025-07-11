from typing import Any, Protocol, TypeAlias

import pint

Array: TypeAlias = Any


class Curve(Protocol):
    @property
    def mnemonic(self) -> str: ...
    @property
    def unit(self) -> str | pint.Unit | None: ...
    @property
    def data(self) -> Array | None: ...
