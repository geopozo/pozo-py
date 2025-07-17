import numpy as np
import pandas as pd
import pytest

from pozo.utils._stats import (
    count_missing_values,
    format_csv,
    max_value,
    min_value,
    quantiles_values,
)


class TestFormatCsv:
    def test_format_csv_comma_delimiter(self):
        data = "a,b,c\n1,2,3\n4,5,6"
        result = format_csv(data, ",")
        expected = pd.DataFrame({"a": [1, 4], "b": [2, 5], "c": [3, 6]})
        pd.testing.assert_frame_equal(result, expected)

    def test_format_csv_semicolon_delimiter(self):
        data = "x;y;z\n10;20;30\n40;50;60"
        result = format_csv(data, ";")
        expected = pd.DataFrame({"x": [10, 40], "y": [20, 50], "z": [30, 60]})
        pd.testing.assert_frame_equal(result, expected)

    def test_format_csv_tab_delimiter(self):
        data = "name\tage\tcity\nJohn\t25\tNY\nJane\t30\tLA"
        result = format_csv(data, "\t")
        expected = pd.DataFrame(
            {"name": ["John", "Jane"], "age": [25, 30], "city": ["NY", "LA"]}
        )
        pd.testing.assert_frame_equal(result, expected)

    def test_format_csv_single_row(self):
        data = "col1,col2\nvalue1,value2"
        result = format_csv(data, ",")
        expected = pd.DataFrame({"col1": ["value1"], "col2": ["value2"]})
        pd.testing.assert_frame_equal(result, expected)


class TestMaxValue:
    @pytest.mark.parametrize(
        ("data", "expected"),
        [
            ([1, 5, 3, 9, 2], 9.0),
            ([-1, -5, -3, -9, -2], -1.0),
            ([-1, 5, -3, 9, 2], 9.0),
            ([1, np.nan, 3, 5, np.nan], 5.0),
            ([42], 42.0),
            (np.array([1, 5, 3, 9, 2]), 9.0),
            (np.array([1, np.nan, 3, 5, np.nan]), 5.0),
            (np.array([1.5, 5.2, 3.1, 9.8, 2.3], dtype=np.float32), 9.8),
            (np.array([1, 5, 3, 9, 2], dtype=np.int64), 9.0),
        ],
    )
    def test_max_value_success(self, data, expected):
        result = max_value(data)
        assert result == expected

    @pytest.mark.parametrize("data", [[], np.array([])])
    def test_max_value_empty_error(self, data):
        with pytest.raises(ValueError):
            max_value(data)


class TestMinValue:
    @pytest.mark.parametrize(
        ("data", "expected"),
        [
            ([1, 5, 3, 9, 2], 1.0),
            ([-1, -5, -3, -9, -2], -9.0),
            ([-1, 5, -3, 9, 2], -3.0),
            ([1, np.nan, 3, 5, np.nan], 1.0),
            ([42], 42.0),
            (np.array([1, 5, 3, 9, 2]), 1.0),
            (np.array([1, np.nan, 3, 5, np.nan]), 1.0),
            (np.array([1.5, 5.2, 3.1, 9.8, 2.3], dtype=np.float32), 1.5),
            (np.array([1, 5, 3, 9, 2], dtype=np.int64), 1.0),
        ],
    )
    def test_min_value_success(self, data, expected):
        result = min_value(data)
        assert result == expected

    @pytest.mark.parametrize("data", [[], np.array([])])
    def test_min_value_empty_error(self, data):
        with pytest.raises(ValueError):
            min_value(data)


class TestQuantilesValues:
    @pytest.mark.parametrize(
        ("data", "quantiles", "expected"),
        [
            (
                [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                [0.25, 0.5, 0.75],
                ["3.25", "5.5", "7.75"],
            ),
            ([1, 2, 3, 4, 5], [0.5], ["3.0"]),
            ([1, 2, 3, 4, 5], [0.0, 1.0], ["1.0", "5.0"]),
            ([1, np.nan, 3, 4, 5], [0.5], ["3.5"]),
            (
                np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]),
                [0.25, 0.5, 0.75],
                ["3.25", "5.5", "7.75"],
            ),
            (np.array([1, np.nan, 3, 4, 5]), [0.5], ["3.5"]),
            (np.array([1.0, 2.0, 3.0, 4.0, 5.0], dtype=np.float32), [0.5], ["3.0"]),
            (np.array([1, 2, 3, 4, 5], dtype=np.int64), [0.5], ["3.0"]),
        ],
    )
    def test_quantiles_values_success(self, data, quantiles, expected):
        result = quantiles_values(data, quantiles)
        assert result == expected


class TestCountMissingValues:
    @pytest.mark.parametrize(
        ("data", "expected"),
        [
            ([1, 2, 3, 4, 5], 0),
            ([1, np.nan, 3, np.nan, 5], 2),
            ([np.nan, np.nan, np.nan], 3),
            ([], 0),
            ([42], 0),
            ([np.nan], 1),
            ([1, 2.5, np.nan, 4, np.nan], 2),
            (np.array([1, 2, 3, 4, 5]), 0),
            (np.array([1, np.nan, 3, np.nan, 5]), 2),
            (np.array([np.nan, np.nan, np.nan]), 3),
            (np.array([]), 0),
            (np.array([1.0, np.nan, 3.0, 4.0, np.nan], dtype=np.float32), 2),
            (np.array([1, 2, 3, 4, 5], dtype=np.int64), 0),
        ],
    )
    def test_count_missing_values(self, data, expected):
        result = count_missing_values(data)
        assert result == expected
