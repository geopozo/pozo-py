from collections.abc import Iterable

import numpy as np
import pandas as pd


def make_param_list(*args: Iterable):  # no me parece necesario esto
    return list(zip(*args))


# si vamos a usar listas como definiciones, y las mismas listas, debemos
# usarlas como constantes
# list_ints = [1, 5, 3, 9, 2]
# array_int64 = np.array(list_ints, dtype=np.int64)
# etc
data_array = {
    "list_ints": [1, 5, 3, 9, 2],
    "list_negative_ints": [-1, -5, -3, -9, -2],
    "list_with_nan": [1, np.nan, 3, 5, np.nan],
    "list_single_value": [42],
    "array_ints": np.array([1, 5, 3, 9, 2]),
    "array_with_nan": np.array([1, np.nan, 3, 5, np.nan]),
    "array_float32": np.array([1.5, 5.2, 3.1, 9.8, 2.3], dtype=np.float32),
    "array_int64": np.array([1, 5, 3, 9, 2], dtype=np.int64),
    "list_floats": [1, 2.5, np.nan, 4, np.nan],
    "pd_series": pd.Series([10, 20, 30]),
    "pd_series_uint16": pd.Series([1, 2, 3], dtype="uint16"),
    "pd_series_float64": pd.Series([1.5, 2.5, 3.5], dtype="float64"),
    "np_uint8": np.uint8(255),
    "range_obj": range(5),
}

data_empty = {
    "list_empty": [],
    "array_empty": np.array([]),
}


data_str = {
    "csv_comma": "a,b\n1,2\n4,5",
    "csv_semicolon": "a;b\n1;2\n4;5",
    "csv_tab": "a\tb\n1\t2\n4\t5",
}
