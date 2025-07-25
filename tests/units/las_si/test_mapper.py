import pytest

from pozo.units.las_si.mapper import Range


class TestRange:
    @pytest.mark.parametrize(
        ("unit", "boundaries", "min_val", "max_val", "confidence", "expected"),
        [
            ("of_1", (-0.5, 0.8), 0.2, 0.7, "decide by range", True),
            ("of_1", (-0.5, 0.8), -0.5, 0.8, "decide by range", False),
            ("pu", (-50, 80), 0, 79.9, "catch all, legacy unit", True),
            ("pu", (-50, 80), -100, 100, "decide by range, verify", False),
            ("puAPI", (), -1000, 1000, "catch all, ppm", True),
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
