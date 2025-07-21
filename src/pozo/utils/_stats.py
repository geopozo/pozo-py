from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

import numpy as np  # type: ignore[import-untyped]
import pandas as pd  # type: ignore[import-untyped]
# es difícil crear que no tienen tipos para estos

if TYPE_CHECKING:
    from typing import TypeAlias

    from pozo.utils import types

    Numeric: TypeAlias = int | float


def format_csv(data: str, delimiter: str) -> pd.DataFrame:
    return pd.read_csv(StringIO(data), delimiter=delimiter, na_filter=False)


def max_value(data: types.Array) -> np.float64:
    return np.nanmax(data) # podemos usasr narwhals?


def min_value(data: types.Array) -> np.float64:
    return np.nanmin(data) # podemos usar narwhals?

# narwhals cuenta como dependencia los paquetes como pandas/polars?


def quantiles_values(data: types.Array, quantiles: types.Array) -> list[str]:
    return [str(x) for x in np.nanquantile(data, quantiles)]
    # quantiles no es una lista?


def count_missing_values(data: types.Array) -> int:
    return np.count_nonzero(np.isnan(data))
