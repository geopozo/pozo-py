import statistics

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from pozo._utils import stats
from tests import data_types


class TestFormatCsv:
    @pytest.mark.parametrize(
        ("data", "delimiter"),
        list(
            zip(
                ["a,b\n1,2\n4,5", "a;b\n1;2\n4;5", "a\tb\n1\t2\n4\t5"],
                [",", ";", "\t"],
            )
        ),
    )
    def test_format_csv_success(self, data, delimiter):
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
        ("data", "expected"),
        list(
            zip(
                data_types.data_array.values(),
                [
                    ["2.0", "3.0", "5.0"],
                    ["-5.0", "-3.0", "-2.0"],
                    ["2.0", "3.0", "4.0"],
                    ["42.0", "42.0", "42.0"],
                    ["2.0", "3.0", "5.0"],
                    ["2.0", "3.0", "4.0"],
                    ["2.299999952316284", "3.0999999046325684", "5.199999809265137"],
                    ["2.0", "3.0", "5.0"],
                    ["1.75", "2.5", "3.25"],
                    ["15.0", "20.0", "25.0"],
                    ["1.5", "2.0", "2.5"],
                    ["2.0", "2.5", "3.0"],
                    ["255.0", "255.0", "255.0"],
                    ["1.0", "2.0", "3.0"],
                ],
            ),
        ),
        ids=data_types.data_array.keys(),
    )
    def test_quantiles_values_success(self, data, expected):
        result = stats.quantiles_values(data, [0.25, 0.5, 0.75])
        print(result)
        assert result == expected


class TestCountMissingValues:
    @pytest.mark.parametrize(
        ("data", "expected"),
        list(
            zip(
                data_types.data_array.values(),
                [0, 0, 2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 1],
            ),
        ),
        ids=data_types.data_array.keys(),
    )
    def test_count_missing_values(self, data, expected):
        result = stats.count_missing_values(data)
        assert result == expected
