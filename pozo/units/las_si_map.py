from typing import Any

from pozo.utilities import lasio_utils, data_utils

from .errors import MissingRangeError
from .range_bondaries import RangeBoundaries


class LasSiMap:
    def __init__(self):
        self._mnemonic_to_si = {}
        self._si_to_mnemonic = {}

    def set_default(self, mnemonic):
        self._mnemonic_to_si[mnemonic] = {}
        self._si_to_mnemonic[mnemonic] = {}

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

        if mnemonic not in self._mnemonic_to_si:
            self.set_default(mnemonic)

        self._mnemonic_to_si[mnemonic][unit] = ranges

        for range in ranges:
            self._si_to_mnemonic[mnemonic][range.unit] = unit

    def resolve_las_unit(
        self,
        mnemonic: str,
        unit: str,
        data: list[Any],
    ) -> RangeBoundaries | None:
        mnemonic = lasio_utils.remove_lasio_suffix(mnemonic)
        max_val = data_utils.get_max_value(data)
        min_val = data_utils.get_min_value(data)
        ranges = None

        if (
            mnemonic in self._mnemonic_to_si
            and unit in self._mnemonic_to_si[mnemonic]
        ):
            ranges: list[RangeBoundaries] = self._mnemonic_to_si[mnemonic][unit]
        elif unit in self._mnemonic_to_si["-"]:
            ranges = self._mnemonic_to_si["-"][unit]

        if ranges:
            for range in ranges:
                if range.is_within_range(min_val, max_val):
                    return range
            raise MissingRangeError(
                f"{unit} for {mnemonic} found but not in range: {ranges}."
            )
        return None

    def get_las_unit(
        self,
        mnemonic: str,
        unit: str,
    ) -> str:
        if (
            mnemonic in self._si_to_mnemonic
            and unit in self._si_to_mnemonic[mnemonic]
        ):
            return self._si_to_mnemonic[mnemonic][unit]
        if "-" in self._si_to_mnemonic and unit in self._si_to_mnemonic["-"]:
            return self._si_to_mnemonic["-"][unit]
        return None
