"""Mapper from las_units to si_units with conversion functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pozo.utils import _lasio as lasio_utils
from pozo.utils import stats

if TYPE_CHECKING:
    from typing import Any, TypeAlias

    Numeric: TypeAlias = int | float
    RangeBoundary: TypeAlias = tuple[Numeric, Numeric] | tuple[()]


class Range:
    boundaries: RangeBoundary
    unit: str
    confidence: str

    def __init__(
        self,
        las_unit: str,
        boundaries: RangeBoundary,
        confidence: str,
    ) -> None:
        if not isinstance(boundaries, tuple) or len(boundaries) not in {0, 2}:
            raise TypeError(
                "boundaries should contain a tuple with (min, max) or () catch-all"
            )

        self.boundaries = boundaries
        self.unit = las_unit
        self.confidence = confidence

    def is_within_range(
        self,
        min_val: Numeric,
        max_val: Numeric,
    ) -> bool:
        return not self.boundaries or (
            min_val > self.boundaries[0] and max_val < self.boundaries[1]
        )


class LasSiMap:
    def __init__(self) -> None:
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

        for _range in ranges:
            if not isinstance(_range, Range):
                raise TypeError("All entries must be of type RangeBoundaries.")

        las_to_ranges = self._las_to_ranges_by_mnemonic.setdefault(mnemonic, {})
        si_to_las = self._si_to_las_by_mnemonic.setdefault(mnemonic, {})

        las_to_ranges[las_unit] = ranges

        for _range in ranges:
            si_to_las[_range.unit] = las_unit

    # De las_unit a range
    def _las_to_Range(
        self,
        mnemonic: str,
        las_unit: str,
        data: list[Any],
    ) -> Range | None:
        """Convert a LAS unit to a Range using a mnemonic."""
        mnemonic = lasio_utils.remove_lasio_suffix(mnemonic)
        max_val = stats.max_value(data)
        min_val = stats.min_value(data)

        if (
            ranges := self._las_to_ranges_by_mnemonic.get(mnemonic, {}).get(las_unit)
        ) is None:
            ranges = self._las_to_ranges_by_mnemonic.get("-", {}).get(las_unit, [])

        for _range in ranges:
            if _range.is_within_range(min_val, max_val):
                return _range
        return None

    # De si a las_unit
    def si_to_las_unit(
        self,
        mnemonic: str,
        si_unit: str,
    ) -> str | None:
        """Convert an SI unit to a LAS unit using a mnemonic."""
        if (
            las_unit := self._si_to_las_by_mnemonic.get(mnemonic, {}).get(si_unit)
        ) is None:
            las_unit = self._si_to_las_by_mnemonic.get("-", {}).get(si_unit)

        return las_unit
