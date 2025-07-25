import pytest

from pozo.units.las_si.mapper import LasSiMap, Range


class TestRange:
    @pytest.mark.parametrize(
        ("unit", "boundaries", "min_val", "max_val", "expected"),
        [
            ("of_1", (-0.5, 0.8), 0.2, 0.7, True),
            ("of_1", (-0.5, 0.8), -0.5, 0.8, False),
            ("pu", (-50, 80), 0, 79.9, True),
            ("pu", (-50, 80), -100, 100, False),
            ("puAPI", (), -1000, 1000, True),
        ],
    )
    def test_is_within_range(self, unit, boundaries, min_val, max_val, expected):
        r = Range(unit, boundaries, 50, "decide by range")
        assert isinstance(r.boundaries, tuple)
        assert r.is_within_range(min_val, max_val) == expected

    @pytest.mark.parametrize(
        "invalid_boundary",
        [(10,), "invalid", [10, 20], (10, 20, 30)],
    )
    def test_range_init_invalid_boundaries(self, invalid_boundary):
        with pytest.raises(TypeError):
            Range("m", invalid_boundary, 1, "fail")


class TestLasSiMap:
    @pytest.fixture
    def las_si_map(self):
        return LasSiMap()

    @pytest.mark.parametrize(
        ("mnemonic", "unit", "ranges", "expected_unit"),
        [
            ("GR", "API", (Range("gAPI", (0, 150), 90, "Gamma Ray"),), "gAPI"),
            ("GR", "API", "gAPI", "gAPI"),
        ],
    )
    def test_add_valid_ranges(self, las_si_map, mnemonic, unit, ranges, expected_unit):
        las_si_map.add(mnemonic, unit, ranges)
        assert mnemonic in las_si_map.las_to_ranges_by_mnemonic
        assert (
            las_si_map.las_to_ranges_by_mnemonic[mnemonic][unit][0].unit
            == expected_unit
        )

    @pytest.mark.parametrize(
        ("mnemonic", "unit", "ranges", "data"),
        [("GR", "API", (Range("gAPI", (0, 100), 90, "Gamma"),), [10, 20, 30])],
    )
    def test_las_to_si_diagnosis(self, las_si_map, mnemonic, unit, ranges, data):
        las_si_map.add(mnemonic, unit, ranges)

        result = las_si_map.las_to_si_diagnosis(mnemonic, unit, data)

        assert result["mnemonic"] == "GR"
        assert result["las_unit"] == "API"
        assert result["si_unit"] == "gAPI"
        assert result["confidence"] == 90
        assert result["comment"] == "Gamma"
        assert result["n_nan"] == 0
        assert result["v_min"] == "10.0"
        assert result["v_med"] == "20.0"
        assert result["v_max"] == "30.0"

    def test_si_to_las_unit_default_and_fallback(self, las_si_map):
        las_si_map.add("GR", "GAPI", "gAPI")
        las_si_map.add("-", "GAPI", "gAPI")
        assert las_si_map.si_to_las_unit("GR", "gAPI") == "GAPI"
        assert las_si_map.si_to_las_unit("XYZ", "gAPI") == "GAPI"

    @pytest.mark.parametrize(
        ("ranges", "expected"),
        [((Range("gAPI", (0, 100), 90, "Gamma"),), "gAPI"), ("gAPI", "gAPI")],
    )
    def test_las_to_si(self, las_si_map, ranges, expected):
        if ranges:
            las_si_map.add("GR", "GAPI", ranges)
        result = las_si_map.las_to_si("GR", "GAPI", [5, 10, 15])
        assert result == expected
