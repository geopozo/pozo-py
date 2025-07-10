from io import StringIO

import numpy as np
import pandas as pd


def format_csv(data, delimiter):
    return pd.read_csv(StringIO(data), delimiter=delimiter, na_filter=False)


def get_max_value(data):
    return np.nanmax(data)


def get_min_value(data):
    return np.nanmin(data)
