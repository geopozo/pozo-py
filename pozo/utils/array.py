import numpy as np
import math
import pint
import pandas as pd
import polars as pl
import hashlib
import warnings
import pozo
import pozo.drawable


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
        step = (
            stop - start
            if is_close(start, stop, sample_rate_consistent, sample, 0.0001)
            else None
        )  # REVISAR
        if step == 0:
            step = 0.0001
        steps.append(step)
        if not is_close(start, stop, sample_rate_consistent, sample, 0.0001):
            sample_rate_consistent = False

        starts.append(start)
        stops.append(stop)
        size.append(stop - step)  # REVISAR

    interval = {
        "start": np.array(starts),
        "stop": np.array(stops),
        "step": np.array(steps) if not np.any(steps == None) else None,
        "size": np.array(size),
        "sample_rate_consistent": sample_rate_consistent,
    }

    return interval


# is_close has 4 parameters, this return a boolean value that verify the cosistent
# from the depth data
def is_close(a, b, rel_tol, abs_tol):
    warnings.warn("You must import math to use this function")
    return math.isclose(a=a, b=b, rel_tol=rel_tol, abs_tol=abs_tol)


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
    if isinstance(
        value, (pozo.Track, pozo.Trace, pozo.Axis, pozo.Graph, pozo.Drawable, pozo.Note)
    ):
        raise ValueError("You mustn't use pozo objects for this function")

    if isinstance(value, str):
        return False
    if isinstance(value, pint.Quantity):
        return is_array(value.magnitude)
    return hasattr(value, "__len__")


# verify_array_len use three inputs to verify the lenght in the data
# Taken by the principal __ini__.py
def verify_array_len(constant, data):
    if is_array(constant) and len(constant) != len(data):
        return False
    return True


# check_numpy verify if numpy is at the global scope, so this function try to
# import it, but if you do not have this installed, raise an import error
def check_numpy():
    if "np" not in globals():
        try:
            import numpy as np

            globals()["np"] = np
        except ImportError:
            raise ImportError(
                "Please install numpy. It must be installed like: pip install numpy"
            )


# check_pandas verify if pandas is at the global scope, so this function try to
# import it, but if you do not have this installed, raise an import error
def check_pandas():
    if "pd" not in globals():
        try:
            import pandas as pd

            globals()["pd"] = pd
        except ImportError:
            raise ImportError(
                "Please install pandas. It must be installed like: pip install pandas"
            )


# check_polars verify if polars is at the global scope, so this function try to
# import it, but if you do not have this installed, raise an import error
def check_polars():
    if "pl" not in globals():
        try:
            import polars as pl

            globals()["pl"] = pl
        except ImportError:
            raise ImportError(
                "Please install polars. It must be installed like: pip install polars"
            )


def verify_type(data):
    if not isfinite(data):
        raise ValueError("You mustn't use float('inf'), -float('inf'), float('nan')")


def min(data):
    if hasattr(data, "min"):
        try:
            return data.min(skipna=True)
        except ValueError:
            return data.min()
    elif hasattr(data, "nan_min"):
        return data.nan_min()
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.nanmin(data)
        except ValueError:
            raise ValueError("Pozo does not support this object for this function")


def max(data):
    if hasattr(data, "min"):
        try:
            return data.max(skipna=True)
        except ValueError:
            return data.max()
    elif hasattr(data, "nan_max"):
        return data.nan_max()
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.nanmax(data)
        except ValueError:
            raise ValueError("Pozo does not support this object for this function")


def abs(data):
    if hasattr(data, "abs"):
        return data.abs()
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.absolute(data)
        except ValueError:
            raise ValueError("Pozo does not support this object for this function")


def isfinite(data):
    if hasattr(data, "is_infinite"):
        return data.is_finite()
    elif hasattr(data, "isin"):
        return ~data.isin([np.inf, -np.inf])
    elif isinstance(data, pl.DataFrame):
        check_numpy()
        warnings.warn("You must import polars to use this function")
        return pl.DataFrame({data.columns[0]: (np.isfinite(data))})
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.isfinite(data)
        except ValueError:
            raise ValueError("Pozo does not support this object for this function")


def isnan(data):
    if hasattr(data, "isnull"):
        return data.isnull().any().any()
    elif hasattr(data, "is_null"):
        return data.is_null()
    elif hasattr(data, "null_count"):
        return data.null_count() > 0
    else:
        check_numpy()
        if isinstance(data, (list, tuple)):
            data = np.array(data)
        try:
            return np.isnan(data)
        except ValueError:
            raise ValueError("Pozo does not support this object for this function")


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
