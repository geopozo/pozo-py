import numpy as np
import pint
import pandas as pd
import polars as pl


# get_interval has one parameter, this return dictionary with info about
# start, stop, step, size and sample_rate_consistent from the depth intervals
def get_interval(depth):
    if not hasattr(depth, "__len__"):
        raise ValueError("You must use for depth a list, tuple or an numpy array")
    starts = np.array([])
    stops = np.array([])
    steps = np.array([])
    size = np.array([])
    sample_rate_consistent = True
    for i in range(len(depth) - 1):
        if depth[i] == depth[-1]:
            break
        start = depth[i]
        stop = depth[i + 1]
        step, sample_rate_consistent = is_close(
            start, stop, sample_rate_consistent, 0.0001
        )
        step = stop - start
        if step == 0:
            step = 0.0001
        if sample_rate_consistent is False:
            starts = np.append(starts, start)
            stops = np.append(stops, stop)
            steps = None
        else:
            starts = np.append(starts, start)
            stops = np.append(stops, stop)
            steps = np.append(steps, step)
        size = np.append(size, stop - step)
    interval = {"start": starts, "stop": stops, "step": steps, "size": size}
    interval["sample_rate_consistent"] = (
        False if sample_rate_consistent is False else True
    )
    return interval


# is_close has 4 parameters, this return a boolean value that verify the cosistent
# from the depth data
def is_close(n_1, n_2, sample_rate_consistent, percent):
    diff_percent = (abs(n_2 - n_1) / ((n_2 + n_1) / 2)) * 100
    if diff_percent > percent or sample_rate_consistent is False:
        sample_rate_consistent = False
    else:
        sample_rate_consistent = True
    return sample_rate_consistent


# hash_depth has one parameter, this return a hash from the depth data
def hash_depth(depth):
    if isinstance(depth, np.ndarray):
        return hash(depth.tobytes())
    elif is_array(depth):
        depth_array = np.array(depth)
        return hash(depth_array.tobytes())
    else:
        raise ValueError("You must use for depth a list, tuple or an numpy array")


# These are all utility functions
# Taken by the principal __ini__.py
def deLASio(mnemonic):
    return mnemonic.split(":", 1)[0] if ":" in mnemonic else mnemonic


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


def verify_data_type(data):
    pass


def min_data(data):
    pass


def max_data(data):
    pass


def abs_data(arg):
    pass


def isfinite_data(data):
    pass


def isnan_data(data):
    pass


def count_nonzero_data(data, axis=None, *, keepdims=False):
    pass


def nanquantile_data(data, q, axis = None):
    pass


def round_data(data):
    pass


def linspace_data(start, stop, num=50, endpoint=True, retstep=False, axis=0):
    pass


def append_data(arg, data):
    pass
