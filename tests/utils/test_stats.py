import math
import statistics

import numpy as np
import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pozo._utils import stats
from tests import data_types


class TestReadCsv:
    @pytest.mark.parametrize(
        ("data", "delimiter"),
        list(
            zip(
                ["a,b\n1,2\n4,5", "a;b\n1;2\n4;5", "a\tb\n1\t2\n4\t5"],
                [",", ";", "\t"],
            ),
        ),
    )
    def test_read_csv_success(self, data, delimiter):
        expected = [["a", "b"], ["1", "2"], ["4", "5"]]
        result = stats.read_csv(data, delimiter)
        assert result == expected
        assert isinstance(result, list)


class TestMaxValue:
    @pytest.mark.parametrize(
        "converter",
        list(data_types.converters.values()),
        ids=list(data_types.converters.keys()),
    )
    @settings(max_examples=20)
    @given(st.data())
    def test_max_value_success(self, converter, data):
        strategy = converter["st"]
        cast_fn = converter["cast_fn"]
        arr = cast_fn(data.draw(strategy))
        result = stats.max_value(arr)
        assert result == max(arr)
        assert isinstance(result, arr.dtype.type)


class TestMinValue:
    @pytest.mark.parametrize(
        "converter",
        list(data_types.converters.values()),
        ids=list(data_types.converters.keys()),
    )
    @settings(max_examples=20)
    @given(st.data())
    def test_min_value_success(self, converter, data):
        strategy = converter["st"]
        cast_fn = converter["cast_fn"]
        arr = cast_fn(data.draw(strategy))
        result = stats.min_value(arr)
        assert result == min(arr)
        assert isinstance(result, arr.dtype.type)


class TestQuantilesValues:
    @pytest.mark.parametrize(
        "converter",
        list(data_types.converters.values()),
        ids=list(data_types.converters.keys()),
    )
    @settings(max_examples=20)
    @given(st.data())
    def test_quantiles_values_success(self, converter, data):
        quantiles = [0.25, 0.5, 0.75]
        strategy = converter["st"]
        cast_fn = converter["cast_fn"]
        arr = cast_fn(data.draw(strategy))
        result = stats.quantiles_values(arr, quantiles)
        expected = statistics.quantiles(arr, method="inclusive")
        assert np.allclose(result, expected)


class TestCountMissingValues:
    @pytest.mark.parametrize(
        "converter",
        list(data_types.converters.values()),
        ids=list(data_types.converters.keys()),
    )
    @settings(max_examples=20)
    @given(st.data())
    def test_count_missing_values(self, converter, data):
        strategy = converter["st"]
        cast_fn = converter["cast_fn"]
        arr = cast_fn(data.draw(strategy))
        result = stats.count_missing_values(arr)

        expected = sum(
            x is None or (isinstance(x, float) and math.isnan(x)) for x in arr
        )  # Esta es la forma canónica que encontré de contar valores faltantes

        assert result == expected
