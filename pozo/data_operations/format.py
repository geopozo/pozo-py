from io import StringIO

import pandas as pd


def parse_csv_to_str(data, delimiter):
    return pd.read_csv(StringIO(data), delimiter=delimiter, na_filter=False)
