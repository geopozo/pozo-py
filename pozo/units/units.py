from .range_bondaries import RangeBoundaries


class LasMap:
    def __init__(self):
        self.mnemonic_to_units = {}
        self.units_to_mnemonic = {}

    def add_las_map(self, mnemonic, unit, ranges, confidence="- not indicated - LOW"):
        if not isinstance(ranges, tuple):
            ranges = (
                [RangeBoundaries((), ranges, confidence)]
                if not isinstance(ranges, RangeBoundaries)
                else [ranges]
            )

        for ra in ranges:
            if not isinstance(ra, RangeBoundaries):
                raise TypeError("All entries must be of type RangeBoundaries.")

        if mnemonic not in self.mnemonic_to_units:
            self.mnemonic_to_units[mnemonic] = {}
            self.units_to_mnemonic[mnemonic] = {}

        self.mnemonic_to_units[mnemonic][unit] = ranges

        for ra in ranges:
            parsed_unit = ra.unit
            self.units_to_mnemonic[mnemonic][parsed_unit] = unit

    def resolve_las_unit(self, mnemonic, unit, data):
        pass

    def get_las_unit(self, mnemonic, unit):
        if (
            mnemonic in self.units_to_mnemonic
            and unit in self.units_to_mnemonic[mnemonic]
        ):
            return self.units_to_mnemonic[mnemonic][unit]
        if "-" in self.units_to_mnemonic and unit in self.units_to_mnemonic["-"]:
            return self.units_to_mnemonic["-"][unit]
        return None
