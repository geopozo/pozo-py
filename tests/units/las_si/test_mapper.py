from unittest.mock import patch

import pytest

from pozo.units.las_si.mapper import LasSiMap, Range


class TestRange:
    def test_init_valid_boundaries(self):
        """Test Range initialization with valid boundaries."""
        boundary_tests = [
            ((10, 20), "m", 1, "test"),
            ((), "m", 1, "catch-all"),
            ((0.5, 1.5), "kg", 2, "weight"),
        ]

        for boundaries, unit, confidence, comment in boundary_tests:
            range_obj = Range(unit, boundaries, confidence, comment)
            assert range_obj.boundaries == boundaries
            assert range_obj.unit == unit
            assert range_obj.confidence == confidence
            assert range_obj.comment == comment

    def test_init_invalid_boundaries(self):
        """Test Range initialization with invalid boundaries."""
        invalid_boundaries = [(10,), (10, 20, 30), [10, 20], "invalid", 123]

        for boundaries in invalid_boundaries:
            with pytest.raises(TypeError, match="boundaries should contain a tuple"):
                Range("m", boundaries, 1, "test")

    @pytest.mark.parametrize(
        ("boundaries", "min_val", "max_val", "expected"),
        list(
            zip(
                [(), (0, 100), (10, 50), (0, 100)],
                [5, 20, 5, 150],
                [95, 80, 25, 200],
                [True, True, False, False],
            ),
        ),
    )
    def test_is_within_range(self, boundaries, min_val, max_val, expected):
        """Test is_within_range method."""
        range_obj = Range("m", boundaries, 1, "test")
        assert range_obj.is_within_range(min_val, max_val) == expected

    def test_is_within_range_edge_cases(self):
        """Test is_within_range with edge cases."""
        range_obj = Range("m", (10, 20), 1, "test")

        assert range_obj.is_within_range(10, 20) is False
        assert range_obj.is_within_range(10.1, 19.9) is True
        assert range_obj.is_within_range(9.9, 20.1) is False


_mapper = LasSiMap()
_remove_suffix = "pozo.utils._lasio.remove_lasio_suffix"
_quantiles_values = "pozo.utils._stats.quantiles_values"
_count_nan = "pozo.utils._stats.count_missing_values"


class TestLasSiMap:
    def test_init(self):
        """Test LasSiMap initialization."""
        assert _mapper.las_to_ranges_by_mnemonic == {}
        assert _mapper.si_to_las_by_mnemonic == {}

    def test_add_with_string_range(self):
        """Test add method with string range."""
        _mapper.add("DEPTH", "FT", "m", 1, "depth measurement")

        assert "DEPTH" in _mapper.las_to_ranges_by_mnemonic
        assert "FT" in _mapper.las_to_ranges_by_mnemonic["DEPTH"]
        assert "DEPTH" in _mapper.si_to_las_by_mnemonic
        assert "m" in _mapper.si_to_las_by_mnemonic["DEPTH"]
        assert _mapper.si_to_las_by_mnemonic["DEPTH"]["m"] == "FT"

    def test_add_with_range_object(self):
        """Test add method with Range object."""
        range_obj = Range("m", (0, 1000), 2, "depth range")
        _mapper.add("DEPTH", "FT", [range_obj])

        assert "DEPTH" in _mapper.las_to_ranges_by_mnemonic
        assert "FT" in _mapper.las_to_ranges_by_mnemonic["DEPTH"]
        assert _mapper.las_to_ranges_by_mnemonic["DEPTH"]["FT"][0] == range_obj

    def test_add_with_multiple_ranges(self):
        """Test add method with multiple ranges."""
        range1 = Range("m", (0, 100), 1, "shallow")
        range2 = Range("km", (100, 10000), 2, "deep")
        _mapper.add("DEPTH", "FT", [range1, range2])

        ranges = _mapper.las_to_ranges_by_mnemonic["DEPTH"]["FT"]
        assert len(ranges) == 2
        assert range1 in ranges
        assert range2 in ranges

    @pytest.mark.parametrize(
        ("mnemonic", "las_unit", "data", "expected_unit"),
        list(
            zip(
                ["DEPTH", "DEPTH", "UNKNOWN"],
                ["FT", "M", "UNKNOWN_UNIT"],
                [[10, 20, 30], [100, 200, 300], [1, 2, 3]],
                ["m", "m", ""],
            ),
        ),
    )
    def test_las_to_si_with_data(self, mnemonic, las_unit, data, expected_unit):
        """Test las_to_si method with different data ranges."""

        range_obj = Range("m", (0, 1000), 1, "depth")
        _mapper.add("DEPTH", "FT", [range_obj])
        _mapper.add("DEPTH", "M", [range_obj])

        result = _mapper.las_to_si(mnemonic, las_unit, data)
        assert result == expected_unit

    def test_las_to_si_with_fallback(self):
        """Test las_to_si method with fallback to '-' mnemonic."""
        range_obj = Range("m", (0, 1000), 1, "default depth")
        _mapper.add("-", "FT", [range_obj])

        result = _mapper.las_to_si("UNKNOWN", "FT", [10, 20, 30])
        assert result == "m"

    def test_las_to_si_no_match(self):
        """Test las_to_si method with no matching range."""
        range_obj = Range("m", (0, 100), 1, "shallow only")
        _mapper.add("DEPTH", "FT", [range_obj])

        result = _mapper.las_to_si("DEPTH", "FT", [500, 600, 700])  # Outside range
        assert result == ""

    @pytest.mark.parametrize(
        ("mnemonic", "si_unit", "expected_las_unit"),
        list(zip(["DEPTH", "DEPTH", "UNKNOWN"], ["m", "kg", "m"], ["FT", None, None])),
    )
    def test_si_to_las_unit(self, mnemonic, si_unit, expected_las_unit):
        """Test si_to_las_unit method."""
        range_obj = Range("m", (0, 1000), 1, "depth")
        _mapper.add("DEPTH", "FT", [range_obj])
        _mapper.add("-", "m", [Range("FT", (), 1, "fallback")])

        result = _mapper.si_to_las_unit(mnemonic, si_unit)
        assert result == expected_las_unit

    def test_si_to_las_unit_with_fallback(self):
        """Test si_to_las_unit method with fallback to '-' mnemonic."""
        range_obj = Range("m", (0, 1000), 1, "default")
        _mapper.add("-", "FT", [range_obj])

        result = _mapper.si_to_las_unit("UNKNOWN", "m")
        assert result == "FT"

    def test_las_to_si_diagnosis(self):
        """Test las_to_si_diagnosis method."""
        range_obj = Range("m", (0, 1000), 2, "depth measurement")
        _mapper.add("DEPTH", "FT", [range_obj])

        data = [10, 20, 30, 40, 50]

        with (
            patch(_remove_suffix) as mock_remove_suffix,
            patch(_quantiles_values) as mock_quantiles,
            patch(_count_nan) as mock_count_nan,
        ):
            mock_remove_suffix.return_value = "DEPTH"
            mock_quantiles.return_value = [10, 30, 50]
            mock_count_nan.return_value = 0

            result = _mapper.las_to_si_diagnosis("DEPTH", "FT", data)

            assert isinstance(result, dict)
            assert result["mnemonic"] == "DEPTH"
            assert result["las_unit"] == "FT"
            assert result["si_unit"] == "m"
            assert result["confidence"] == 2
            assert result["comment"] == "depth measurement"
            assert result["v_min"] == 10
            assert result["v_med"] == 30
            assert result["v_max"] == 50
            assert result["n_nan"] == 0

    def test_las_to_si_diagnosis_no_match(self):
        """Test las_to_si_diagnosis method with no matching range."""
        data = [10, 20, 30]

        with (
            patch(_remove_suffix) as mock_remove_suffix,
            patch(_quantiles_values) as mock_quantiles,
            patch(_count_nan) as mock_count_nan,
        ):
            mock_remove_suffix.return_value = "UNKNOWN"
            mock_quantiles.return_value = [10, 20, 30]
            mock_count_nan.return_value = 1

            result = _mapper.las_to_si_diagnosis("UNKNOWN", "UNKNOWN_UNIT", data)

            assert result["si_unit"] == ""
            assert result["confidence"] == 0
            assert result["comment"] == "- UNKNOWN_UNIT for UNKNOWN"

    def test_las_to_si(self):
        """Test las_to_si method."""
        range_obj = Range("m", (0, 1000), 1, "depth")
        _mapper.add("DEPTH", "FT", [range_obj])

        data = [10, 20, 30]

        with patch.object(_mapper, "las_to_si_diagnosis") as mock_diagnosis:
            mock_diagnosis.return_value = {"si_unit": "m"}

            result = _mapper.las_to_si("DEPTH", "FT", data)
            assert result == "m"
            mock_diagnosis.assert_called_once_with("DEPTH", "FT", data)
