import numpy as np
import pandas as pd
import pytest

from pozo.utils._stats import (
    count_missing_values,
    format_csv,
    max_value,
    min_value,
    quantiles_values,
)  # sabes el asunto que tengo acá
from tests.data_types import (
    data_array,
    data_empty,
    data_str,
    make_param_list,
)


class TestFormatCsv:
    @pytest.mark.parametrize(
        ("data", "expected", "delimiter"),
        make_param_list(
            data_str.values(),
            [{"a": [1, 4], "b": [2, 5]}] * 3,
            # expected debe estar en data_types
            [",", ";", "\t"],
        ),
        ids=data_str.keys(),
    )
    def test_format_csv_success(self, data, expected, delimiter):
        expected = pd.DataFrame(expected)
        result = format_csv(data, delimiter)
        pd.testing.assert_frame_equal(result, expected)


class TestMaxValue:
    @pytest.mark.parametrize(
        ("data", "expected"),
        make_param_list(
            data_array.values(),
            [
                9.0,
                -1.0,
                5.0,
                42.0,
                9.0,
                5.0,
                9.8,
                9.0,
                np.float64(4.0),
                np.int64(30),
                np.uint16(3),
                np.float64(3.5),
                np.uint8(255),
                np.int64(4),
            ],
        ),
        ids=data_array.keys(),
    )
    def test_max_value_success(self, data, expected):
        result = max_value(data)
        assert result == expected

        # otra cosa

    @pytest.mark.parametrize("data", data_empty.values())
    def test_max_value_empty_error(self, data):
        with pytest.raises(ValueError):
            max_value(data)


class TestMinValue:
    @pytest.mark.parametrize(
        ("data", "expected"),
        make_param_list(
            data_array.values(),
            [
                1.0,
                -9.0,
                1.0,
                42.0,
                1.0,
                1.0,
                1.5,
                1.0,
                np.float64(1.0),
                np.int64(10),
                1,
                np.float64(1.5),
                np.uint8(255),
                np.uint16(0),
            ],
        ),
        ids=data_array.keys(),
    )
    def test_min_value_success(self, data, expected):
        result = min_value(data)
        assert result == expected

    @pytest.mark.parametrize("data", data_empty.values())
    def test_min_value_empty_error(self, data):
        with pytest.raises(ValueError):
            min_value(data)


class TestQuantilesValues:
    @pytest.mark.parametrize(
        ("data", "quantiles", "expected"),
        make_param_list(
            data_array.values(),
            [[0.25, 0.5, 0.75]] * 15,
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
        ids=data_array.keys(),
    )
    def test_quantiles_values_success(self, data, quantiles, expected):
        result = quantiles_values(data, quantiles)
        print(result)
        assert result == expected


class TestCountMissingValues:
    @pytest.mark.parametrize(
        ("data", "expected"),
        make_param_list(
            data_array.values(),
            [0, 0, 2, 0, 0, 2, 0, 0, 2, 0, 0, 0, 0, 0, 1],
        ),
        ids=data_array.keys(),
    )
    def test_count_missing_values(self, data, expected):
        result = count_missing_values(data)
        assert result == expected


# pero tambien esta bien la cantidad de funciones, pero expectedes deben
# venir con los data_types
