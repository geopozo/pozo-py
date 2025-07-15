from typing import TYPE_CHECKING

from pozo.utils import _lasio as lasio_utils
from pozo.utils import stats

if TYPE_CHECKING:
    from typing import TypeAlias, Any

    Numeric: TypeAlias = int | float
    RangeBoundary: TypeAlias = tuple[Numeric, Numeric] | tuple[()]


class Range:
    boundaries: RangeBoundary
    unit: str
    confidence: str

    def __init__(self, las_unit: str, boundaries: RangeBoundary, confidence: str):
        if not isinstance(boundaries, tuple) or len(boundaries) not in {0, 2}:
            raise TypeError(
                "boundaries should contain a tuple with (min, max) or () catch-all"
            )

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

    def add(
        self,
        mnemonic: str,
        las_unit: str,
        ranges: str | list[Range] | tuple[Range],
        confidence: str = "- not indicated - LOW",
    ) -> None:
        if not isinstance(ranges, (tuple, list)):
            ranges = (
                [Range(ranges, (), confidence)]
                if not isinstance(ranges, Range)
                else [ranges]
            )

        for range in ranges:
            if not isinstance(range, Range):
                raise TypeError("All entries must be of type RangeBoundaries.")

        if mnemonic not in self._las_to_ranges_by_mnemonic:
            self._las_to_ranges_by_mnemonic.setdefault(mnemonic, {})
            self._si_to_las_by_mnemonic.setdefault(mnemonic, {})

        self._las_to_ranges_by_mnemonic[mnemonic][las_unit] = ranges

        for range in ranges:
            self._si_to_las_by_mnemonic[mnemonic][range.unit] = las_unit

    # De las_unit a range
    def _las_to_Range(
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
            las_unit := self._si_to_las_by_mnemonic.get(mnemonic, {}).get(si_unit)
        ) is None:
            las_unit = self._si_to_las_by_mnemonic.get("-", {}).get(si_unit)

        return las_unit
