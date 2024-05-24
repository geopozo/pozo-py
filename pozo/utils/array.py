import numpy as np
import math
import pint
import pandas as pd
import polars as pl
import hashlib
import warnings


# summarize_array has one parameter, this return dictionary with info about
# start, stop, step, size and sample_rate_consistent from the depth intervals
def summarize_array(depth):
    if not is_array(depth):
        raise ValueError("You must use for depth a list, tuple or an numpy array")
    verify_type(depth)

    starts = []
    stops = []
    steps = []
    size = []
    sample_rate_consistent = True
    sample = depth[1] - depth[0]
    for i in range(len(depth) - 1):
        if isinstance(depth, (pd.Series, pd.DataFrame)):
            if depth.iloc[i] == depth.iloc[-1]:
                break
        elif depth[i] == depth[-1]:
            break
        start = depth[i]
        stop = depth[i + 1]
        step = stop - start # REVISAR
        if step == 0:
            step = 0.0001

        if i>1:
            if steps is None:
                steps = None
                sample_rate_consistent = False
        elif is_close(start, stop, sample_rate_consistent, sample, 0.0001):
            steps.append(step)
        else:
            steps = None
            sample_rate_consistent = False

        starts.append(start)
        stops.append(stop)
        size.append(stop - step) # REVISAR

    interval = {
        "start": np.array(starts),
        "stop": np.array(stops),
        "step": np.array(steps),
        "size": np.array(size),
        "sample_rate_consistent": sample_rate_consistent
    }

    return interval


# is_close has 4 parameters, this return a boolean value that verify the cosistent
# from the depth data
def is_close(n_1, n_2, sample_rate_consistent, sample, percent):
    diff_percent = (math.fabs(n_2 - n_1) / sample) * 100
    if diff_percent > percent or sample_rate_consistent is False:
        sample_rate_consistent = False
    else:
        sample_rate_consistent = True
    return sample_rate_consistent


# hash_array has one parameter, this return a hash from the depth data
def hash_array(depth):
    if hasattr(depth, "tobytes"):
        return hashlib.md5(str((depth.tobytes())).encode()).hexdigest()
    elif is_array(depth):
        depth_array = np.array(depth)
        return hashlib.md5(str((depth_array.tobytes())).encode()).hexdigest()
    else:
        raise ValueError("You must use for depth a list, tuple or an numpy array")


# is_array use the input data to verify if is pint data or other type that has
# __len__ and return a boolean. Be careful with this, it will return true for Pozo objects.
# Taken by the principal __ini__.py
def is_array(value):
    if isinstance(value, str):
        return False
    if isinstance(value, pint.Quantity):
        return is_array(value.magnitude)
    return hasattr(value, "__len__")


# is_scalar_number use the input data to verify if is a number data
# Taken by the principal __ini__.py
def is_scalar_number(value):
    number_types = (
        int,
        float,
        np.float16,
        np.float32,
        np.float64,
        np.int16,
        np.int32,
        np.int64,
    )
    if isinstance(value, pint.Quantity):
        return is_scalar_number(value.magnitude)
    return isinstance(value, number_types)


# verify_array_len use three inputs to verify the lenght in the data
# Taken by the principal __ini__.py
def verify_array_len(constant, data):
    if is_array(constant) and len(constant) != len(data):
        return False
    return True


def verify_type(data):
    if isinstance(data, (pd.Series, pd.DataFrame)):
        if data.isin([np.inf, -np.inf]).any() or data.isna().any():
            raise ValueError(
                "You mustn't use float('inf'), -float('inf'), float('nan')"
            )
    else:
        for item in data:
            if item == float("inf") or item == -float("inf") or item == float("nan"):
                raise ValueError(
                    "You mustn't use float('inf'), -float('inf'), float('nan')"
                )


def min(data):
    if isinstance(data, (pd.Series, pd.DataFrame)):
        warnings.warn("You must import pandas to use this function")
        return data.min(skipna=True)
    elif isinstance(data, (pl.Series, pl.DataFrame)):
        warnings.warn("You must import polars to use this function")
        return data.min()
    else:
        warnings.warn("You must import numpy to use this function")
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        return np.nanmin(data)


def max(data):
    if isinstance(data, (pd.Series, pd.DataFrame)):
        warnings.warn("You must import pandas to use this function")
        return data.max(skipna=True)
    elif isinstance(data, (pl.Series, pl.DataFrame)):
        warnings.warn("You must import polars to use this function")
        return data.max()
    else:
        warnings.warn("You must import numpy to use this function")
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        return np.nanmax(data)


def abs(data):
    if isinstance(data, (pd.Series, pd.DataFrame)):
        warnings.warn("You must import pandas to use this function")
        return data.abs()
    elif isinstance(data, (pl.Series, pl.DataFrame)):
        warnings.warn("You must import polars to use this function")
        return data.abs()
    else:
        warnings.warn("You must import numpy to use this function")
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        return np.absolute(data)


def isfinite(data):
    if isinstance(data, (pd.Series, pd.DataFrame)):
        warnings.warn("You must import pandas and numpy to use this function")
        return ~data.isin([np.inf, -np.inf])
    elif isinstance(data, pl.Series):
        warnings.warn("You must import polars to use this function")
        return data.is_finite()
    elif isinstance(data, pl.DataFrame):
        warnings.warn("You must import polars and numpy to use this function")
        return pl.DataFrame({data.columns[0]:(np.isfinite(data))})
    else:
        warnings.warn("You must import numpy to use this function")
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        return np.isfinite(data)


def isnan(data):
    if isinstance(data, (pd.Series, pd.DataFrame)):
        warnings.warn("You must import pandas to use this function")
        return data.isnull().any().any()
    elif isinstance(data, pl.Series):
        warnings.warn("You must import polars to use this function")
        return data.is_null()
    elif isinstance(data, pl.DataFrame):
        warnings.warn("You must import polars to use this function")
        return data.null_count() > 0
    else:
        warnings.warn("You must import numpy to use this function")
        if not isinstance(data, np.ndarray):
            data = np.array(data)
        return np.isnan(data)


def count_nonzero(data, axis=None, *, keepdims=False):
    pass


def nanquantile(data, q, axis=None):
    pass


def round(data):
    pass


def linspace(start, stop, num=50, endpoint=True, retstep=False, axis=0):
    pass


def append(arg, data):
    pass
