from io import StringIO

import pandas as pd


def format_csv(data, delimiter):
    return pd.read_csv(StringIO(data), delimiter=delimiter, na_filter=False)
