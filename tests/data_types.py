from types import FunctionType

import numpy as np
import pandas as pd
from hypothesis import strategies as st


def np_lambda(kind: type) -> FunctionType:
    return lambda lst: np.array(lst, dtype=kind)


def pd_lambda(kind: str) -> FunctionType:
    return lambda lst: pd.Series(lst, dtype=kind)


def gen_st(kind: type, *, allow_nan=False) -> st.SearchStrategy:
    if issubclass(kind, np.floating):
        finfo: np.finfo = np.finfo(kind)
        strategy = st.floats(
            min_value=finfo.min,
            max_value=finfo.max,
            allow_infinity=False,
            allow_nan=allow_nan,
        )
    else:
        iinfo: np.iinfo = np.iinfo(kind)
        strategy = st.integers(min_value=iinfo.min, max_value=iinfo.min)
    return st.lists(strategy, min_size=4, max_size=8)


converters = {
    #"np.float16": {"cast_fn": np_lambda(np.float16), "st": gen_st(np.float16)},
    "np.float32": {"cast_fn": np_lambda(np.float32), "st": gen_st(np.float32)},
    "np.float64": {"cast_fn": np_lambda(np.float64), "st": gen_st(np.float64)},
    "np.int8": {"cast_fn": np_lambda(np.int8), "st": gen_st(np.int8)},
    "np.int16": {"cast_fn": np_lambda(np.int16), "st": gen_st(np.int16)},
    "np.int32": {"cast_fn": np_lambda(np.int32), "st": gen_st(np.int32)},
    "np.int64": {"cast_fn": np_lambda(np.int64), "st": gen_st(np.int64)},
    "np.uint8": {"cast_fn": np_lambda(np.uint8), "st": gen_st(np.uint8)},
    "np.uint16": {"cast_fn": np_lambda(np.uint16), "st": gen_st(np.uint16)},
    "np.uint32": {"cast_fn": np_lambda(np.uint32), "st": gen_st(np.uint32)},
    "np.uint64": {"cast_fn": np_lambda(np.uint64), "st": gen_st(np.uint64)},
    #"pd.float16": {"cast_fn": pd_lambda("float16"), "st": gen_st(np.float16)},
    "pd.float32": {"cast_fn": pd_lambda("float32"), "st": gen_st(np.float32)},
    "pd.float64": {"cast_fn": pd_lambda("float64"), "st": gen_st(np.float64)},
    "pd.int8": {"cast_fn": pd_lambda("int8"), "st": gen_st(np.int8)},
    "pd.int16": {"cast_fn": pd_lambda("int16"), "st": gen_st(np.int16)},
    "pd.int32": {"cast_fn": pd_lambda("int32"), "st": gen_st(np.int32)},
    "pd.int64": {"cast_fn": pd_lambda("int64"), "st": gen_st(np.int64)},
    "pd.uint8": {"cast_fn": pd_lambda("uint8"), "st": gen_st(np.uint8)},
    "pd.uint16": {"cast_fn": pd_lambda("uint16"), "st": gen_st(np.uint16)},
    "pd.uint32": {"cast_fn": pd_lambda("uint32"), "st": gen_st(np.uint32)},
    "pd.uint64": {"cast_fn": pd_lambda("uint64"), "st": gen_st(np.uint64)},
}
