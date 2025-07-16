from io import StringIO

import numpy as np
import pandas as pd


def format_csv(data, delimiter):
    return pd.read_csv(StringIO(data), delimiter=delimiter, na_filter=False)


def max_value(data):
    return np.nanmax(data)


def min_value(data):
    return np.nanmin(data)


def quantiles_values(data, quantiles):
    return [str(x) for x in np.nanquantile(data, quantiles)]


def count_missing_values(data):
    return np.count_nonzero(np.isnan(data))
