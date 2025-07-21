from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

import numpy as np  # type: ignore[import-untyped]
import pandas as pd  # type: ignore[import-untyped]

if TYPE_CHECKING:
    from pozo.utils import types

    Numeric: int | float


def format_csv(data: str, delimiter: str) -> pd.DataFrame:
    return pd.read_csv(StringIO(data), delimiter=delimiter, na_filter=False)


def max_value(data: types.Array) -> np.float64:
    return np.nanmax(data)


def min_value(data: types.Array) -> np.float64:
    return np.nanmin(data)


def quantiles_values(data: types.Array, quantiles: types.Array) -> list[str]:
    return [str(x) for x in np.nanquantile(data, quantiles)]


def count_missing_values(data: types.Array) -> int:
    return np.count_nonzero(np.isnan(data))
