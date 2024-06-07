import random
import pozo.utils.array as pzutils
import numpy as np
import pandas as pd
import polars as pl
import xarray as xr

datatypes = ["np", "pl", "pd", "list", "tuple"]


def pytest_generate_tests(metafunc):
    if "datatype" in metafunc.fixturenames:
        metafunc.parametrize("datatype", datatypes)


def list_random(n):
    if n < 5:
        raise ValueError("You must use a value >= 5")
    random_list = [random.randint(0, 100000) for _ in range(n)]
    random_list.append(float("nan"))
    random_list.append(float("inf"))
    random_list.append(-float("inf"))
    return random.shuffle(random_list)


class Data:
    def __init__(self, data=None, size=None):
        if pzutils.is_array(data):
            self.data = data
        elif size:
            self.data = list_random(size)
        else:
            raise ValueError("You must supply data or size to initiate a data class")

    def to_numpy(self):
        return np.array(self.data)

    def to_pandas(self):
        return pd.Serie(self.data)

    def to_polars(self):
        return pl.Serie(self.data)

    conversion_lut = {
        "np": to_numpy,
        "pl": to_polars,
        "pd": to_pandas,
    }

    def conversion(self, string):
        if string in self.conversion_lut:
            return self.conversion_lut[string](self.data)
        elif string == "list":
            return list(self.data)
        elif string == "tuple":
            return tuple(self.data)
        else:
            raise ValueError("You must use 'np', 'pl', 'pd', 'list' or 'tuple'")

    def min(self):
        return min(self.data)

    def max(self):
        return max(self.data)


@pytest.fixture  # noqa
def new_data(input_argument):
    return Data(input_argument)
