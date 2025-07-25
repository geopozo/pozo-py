from __future__ import annotations

import csv
from io import StringIO
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from typing import Union

    from pozo._utils import types

    Numeric = Union[int, float]


def read_csv(data: str, delimiter: str = ",") -> list:
    return list(csv.reader(StringIO(data), delimiter=delimiter))


def max_value(data: types.Array) -> Numeric:
    return np.nanmax(data)


def min_value(data: types.Array) -> Numeric:
    return np.nanmin(data)


def quantiles_values(data: types.Array, quantiles: list) -> np.ndarray:
    return np.nanquantile(data, quantiles)


def count_missing_values(data: types.Array) -> int:
    return np.count_nonzero(np.isnan(data))
