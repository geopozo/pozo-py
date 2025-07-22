import numpy as np
import pytest

from pozo._utils import stats
from tests import data_types


class TestFormatCsv:
    @pytest.mark.parametrize(
        ("data", "delimiter"),
        list(zip(data_types.data_str.values(), [",", ";", "\t"])),
        ids=data_types.data_str.keys(),
    )
    def test_format_csv_success(self, data, expected, delimiter):
        expected = [["a", "confidence"], ["1", "2"], ["4", "5"]]
        result = stats.read_csv(data, delimiter)
        assert result == expected


class TestMaxValue:
    @pytest.mark.parametrize(
        ("data", "expected"),
        list(
            zip(
                data_types.data_array.values(),
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
        ),
        ids=data_types.data_array.keys(),
    )
    def test_max_value_success(self, data, expected):
        result = stats.max_value(data)
        assert result == expected

    @pytest.mark.parametrize("data", data_types.data_empty.values())
    def test_max_value_empty_error(self, data):
        with pytest.raises(ValueError, match="Value error"):
            stats.max_value(data)


class TestMinValue:
    @pytest.mark.parametrize(
        ("data", "expected"),
        list(
            zip(
                data_types.data_array.values(),
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
        ),
        ids=data_types.data_array.keys(),
    )
    def test_min_value_success(self, data, expected):
        result = stats.min_value(data)
        assert result == expected

    @pytest.mark.parametrize("data", data_types.data_empty.values())
    def test_min_value_empty_error(self, data):
        with pytest.raises(ValueError, match="Value error"):
            stats.min_value(data)


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
