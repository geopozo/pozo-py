import pytest

from pozo.units.las_si import mapper
from pozo.units.las_si.config import add_to_las_si_map, las_si_map

simple_units = [
    unit_tuple
    for unit_tuple in las_si_map
    if len(unit_tuple) == 5 and isinstance(unit_tuple[2], str)
]


class TestAddToLasSiMap:
    @pytest.mark.parametrize(
        ("mnemonic", "las_unit", "si_unit", "confidence", "comment"), simple_units
    )
    def test_add_to_las_si_map_valid_args(
        self, mnemonic, las_unit, si_unit, confidence, comment
    ):
        las_map = mapper.LasSiMap()
        add_to_las_si_map(las_map)

        assert mnemonic in las_map.las_to_ranges_by_mnemonic
        assert las_unit in las_map.las_to_ranges_by_mnemonic[mnemonic]
        assert mnemonic in las_map.si_to_las_by_mnemonic
        assert si_unit in las_map.si_to_las_by_mnemonic[mnemonic]
        assert las_unit in las_map.las_to_ranges_by_mnemonic[mnemonic]

        ranges = las_map.las_to_ranges_by_mnemonic[mnemonic][las_unit]
        assert len(ranges) == 1
        assert ranges[0].unit == si_unit
        assert ranges[0].confidence == confidence
        assert ranges[0].comment == comment

    def test_add_to_las_si_map_empty_map(self):
        las_map = mapper.LasSiMap()
        initial_las_count = len(las_map.las_to_ranges_by_mnemonic)
        initial_si_count = len(las_map.si_to_las_by_mnemonic)

        add_to_las_si_map(las_map)

        assert len(las_map.las_to_ranges_by_mnemonic) > initial_las_count
        assert len(las_map.si_to_las_by_mnemonic) > initial_si_count

    def test_add_to_las_si_map_with_ranges(self):
        las_map = mapper.LasSiMap()
        add_to_las_si_map(las_map)

        assert "NPHI" in las_map.las_to_ranges_by_mnemonic
        assert "PU" in las_map.las_to_ranges_by_mnemonic["NPHI"]
        ranges = las_map.las_to_ranges_by_mnemonic["NPHI"]["PU"]
        assert len(ranges) == 3
        assert ranges[0].unit == "of_1"
        assert ranges[1].unit == "pu"
        assert ranges[2].unit == "puAPI"

    def test_add_to_las_si_map_multiple_ranges(self):
        las_map = mapper.LasSiMap()
        add_to_las_si_map(las_map)

        ranges = las_map.las_to_ranges_by_mnemonic["NPHI"]["PU"]
        assert len(ranges) == 3
        assert ranges[0].unit == "of_1"
        assert ranges[1].unit == "pu"
        assert ranges[2].unit == "puAPI"

        assert las_map.si_to_las_by_mnemonic["NPHI"]["of_1"] == "PU"
        assert las_map.si_to_las_by_mnemonic["NPHI"]["pu"] == "PU%"
        assert las_map.si_to_las_by_mnemonic["NPHI"]["puAPI"] == "PU"

        assert las_map.si_to_las_by_mnemonic["NPHI"]["of_1"] == "PU"
        assert las_map.si_to_las_by_mnemonic["NPHI"]["pu"] == "PU%"
        assert las_map.si_to_las_by_mnemonic["NPHI"]["puAPI"] == "PU"
