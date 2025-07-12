from typing import Any

from pozo.units import errors
from pozo.utils import _lasio as lasio_utils
from pozo.utils import stats


class Range:
    def __init__(self, boundaries, las_unit: str | tuple["Range"], confidence):
        if not isinstance(boundaries, tuple) or len(boundaries) not in {0, 2}:
            raise TypeError(
                "boundaries should contain a tuple with (min, max) or () catch-all"
            )
        # TODO: Chequeo de orden de rangos
        self.boundaries = boundaries
        self.unit = las_unit
        self.confidence = confidence

    def is_within_range(self, min_val, max_val):
        return not self.boundaries or (
            min_val > self.boundaries[0] and max_val < self.boundaries[1]
        )


class LasSiMap:
    def __init__(self):
        self._las_to_ranges_by_mnemonic = {}  # las a si por mnemotecnica
        self._si_to_las_by_mnemonic = {}  # si a las por mnemotecnica

    def set_default(self, mnemonic):
        self._las_to_ranges_by_mnemonic[mnemonic] = {}
        self._si_to_las_by_mnemonic[mnemonic] = {}

    def add(
        self,
        mnemonic: str,
        las_unit: str,
        ranges: str | tuple[Range] | list[Range],
        confidence: str = "- not indicated - LOW",
    ) -> None:
        if not isinstance(ranges, (tuple, list)):
            ranges = (
                [Range((), ranges, confidence)]
                if not isinstance(ranges, Range)
                else [ranges]
            )

        for range in ranges:
            if not isinstance(range, Range):
                raise TypeError("All entries must be of type RangeBoundaries.")

        if mnemonic not in self._las_to_ranges_by_mnemonic:
            self.set_default(mnemonic)

        self._las_to_ranges_by_mnemonic[mnemonic][las_unit] = ranges

        for range in ranges:
            self._si_to_las_by_mnemonic[mnemonic][range.unit] = las_unit

    # De las_unit a si_unit
    def las_to_Range(
        self,
        mnemonic: str,
        las_unit: str,
        data: list[Any],
    ) -> Range | None:
        mnemonic = lasio_utils.remove_lasio_suffix(mnemonic)
        max_val = stats.max_value(data)
        min_val = stats.min_value(data)

        if (
            ranges := self._las_to_ranges_by_mnemonic.get(mnemonic, {}).get(las_unit)
        ) is None:
            ranges = self._las_to_ranges_by_mnemonic.get("-", {}).get(las_unit, [])

        for range in ranges:
            if range.is_within_range(min_val, max_val):
                return range
        return None

    # De si a las_unit
    def si_to_las_unit(
        self,
        mnemonic: str,
        si_unit: str,
    ) -> str | None:
        if (
            mnemonic in self._si_to_las_by_mnemonic
            and si_unit in self._si_to_las_by_mnemonic[mnemonic]
        ):
            return self._si_to_las_by_mnemonic[mnemonic][si_unit]
        if (
            "-" in self._si_to_las_by_mnemonic
            and si_unit in self._si_to_las_by_mnemonic["-"]
        ):
            return self._si_to_las_by_mnemonic["-"][si_unit]
        return None
