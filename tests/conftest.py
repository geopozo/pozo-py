import pytest
import random
import pozo.utils.array as pzutils
import numpy as np
import pandas as pd
import polars as pl
#import xarray as xr


# One way to parameterize tests directly above your tests:
# ```
#   @pytest.mark.parametrize("letter,number", [("a", 1), ("b", 2), ("c", 3)])
#   def test_something(letter, number):
#       pass
# ```
#
# Note: When you use @pytest.mark.parameterize(), all parameters are passed as reference,
# so modifying the variable may modify it for all tests.

datatypes = ["np", "pl", "pd", "list", "tuple"]

# this creates a global parameterization option
# and is also useful if you have command line options
def pytest_generate_tests(metafunc):
    if "datatype" in metafunc.fixturenames:
        metafunc.parametrize("datatype", datatypes)

## Data class to supply some random data and provide methods to analyze and change it
class Data:
    def __init__(self, *, data=None, size=5):
        if pzutils.is_array(data):
            self.data = data
        elif size  and size >= 5:
            self.data = random.shuffle(
                    list(np.random.randint(low = 0, high = 10**5, size=size))
                    .extend([float("nan"), float("inf"), -float("inf")])
                    )
        else:
            raise ValueError("You must supply data or size (at least of 5) to initiate a data class")

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


@pytest.fixture
def new_Data(request=None):
    if request:
        return Data(request.param)
    return Data()

# If we want to pass an argument to the above fixture, we pretend we have a parameter
#   @pytest.mark.parametrize('new_Data', ['thing'], indirect=True)
#   def test_something(new_Data):
#       pass
# By setting indirect=True, the parametrize doesn't replace the variable `new_Data`,
# instead, it passes an argyment called `request` with a member `.param` with the value
# 'thing'.

# There is a new, undocument feature that will allow you to pass a variable to a fixure
# more intuitively:
#   @pytest.fixture
#   def new_Data(input_data=None):
#       if input_data:
#           return Data(input_data)
#       return Data()

#   @pytest.mark.parametrize('input_data', ['thing'])
#   def test_something(new_Data):
#           pass
