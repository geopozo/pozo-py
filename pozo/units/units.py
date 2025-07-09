import numpy as np

import pozo

from .errors import MissingRangeError
from .range_bondaries import RangeBoundaries


class LasMap:
    def __init__(self):
        self._mnemonic_to_units = {}
        self._units_to_mnemonic = {}

    def add(
        self,
        mnemonic: str,
        unit: str,
        ranges: str | tuple[RangeBoundaries],
        confidence: str = "- not indicated - LOW",
    ) -> None:
        if not isinstance(ranges, tuple):
            ranges = (
                [RangeBoundaries((), ranges, confidence)]
                if not isinstance(ranges, RangeBoundaries)
                else [ranges]
            )

        for range in ranges:
            if not isinstance(range, RangeBoundaries):
                raise TypeError("All entries must be of type RangeBoundaries.")

        if mnemonic not in self._mnemonic_to_units:
            self._mnemonic_to_units[mnemonic] = {}
            self._units_to_mnemonic[mnemonic] = {}

        self._mnemonic_to_units[mnemonic][unit] = ranges

        for range in ranges:
            parsed_unit = range.unit
            self._units_to_mnemonic[mnemonic][parsed_unit] = unit

    def resolve_las_unit(self, mnemonic: str, unit: str, data: list):
        mnemonic = pozo.deLASio(mnemonic)
        max_val = np.nanmax(data)
        min_val = np.nanmin(data)
        ranges = None
        if (
            mnemonic in self._mnemonic_to_units
            and unit in self._mnemonic_to_units[mnemonic]
        ):
            ranges: list[RangeBoundaries] = self._mnemonic_to_units[mnemonic][unit]
        elif unit in self._mnemonic_to_units["-"]:
            ranges = self._mnemonic_to_units["-"][unit]
        if ranges:
            for range in ranges:
                if range.is_within_range(min_val, max_val):
                    return range
            raise MissingRangeError(
                f"{unit} for {mnemonic} found but not in range: {ranges}."
            )
        return None

    def get_las_unit(self, mnemonic: str, unit: str) -> str:
        if (
            mnemonic in self._units_to_mnemonic
            and unit in self._units_to_mnemonic[mnemonic]
        ):
            return self._units_to_mnemonic[mnemonic][unit]
        if "-" in self._units_to_mnemonic and unit in self._units_to_mnemonic["-"]:
            return self._units_to_mnemonic["-"][unit]
        return None
