from __future__ import annotations

from io import StringIO
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from typing import Union

    from pozo.utils import types

    Numeric = Union[int, float]


def read_csv(data: str, delimiter: str = ",") -> pd.DataFrame:
    return pd.read_csv(StringIO(data), delimiter=delimiter, na_filter=False)


def max_value(data: types.Array) -> Numeric:
    return np.nanmax(data)


def min_value(data: types.Array) -> Numeric:
    return np.nanmin(data)


def quantiles_values(data: types.Array, quantiles: list) -> list[Numeric]:
    return list(np.nanquantile(data, quantiles))


def count_missing_values(data: types.Array) -> int:
    return np.count_nonzero(np.isnan(data))
