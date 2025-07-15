"""Classes for units to units with conversion functions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pozo.utils import _lasio as lasio_utils
from pozo.utils import stats, types

if TYPE_CHECKING:
    from typing import Any, TypeAlias

    Numeric: TypeAlias = int | float
    RangeBoundary: TypeAlias = tuple[Numeric, Numeric] | tuple[()]


class Range:
    """Range to assign unit information."""

    boundaries: RangeBoundary
    unit: str
    confidence: int
    comment: str

    def __init__(
        self,
        las_unit: str,
        boundaries: RangeBoundary,
        confidence: int,
        comment: str,
    ) -> None:
        """Initialize the class range."""
        if not isinstance(boundaries, tuple) or len(boundaries) not in {0, 2}:
            raise TypeError(
                "boundaries should contain a tuple with (min, max) or () catch-all"
            )

        self.boundaries = boundaries
        self.unit = las_unit
        self.confidence = confidence
        self.comment = comment

    def is_within_range(
        self,
        min_val: Numeric,
        max_val: Numeric,
    ) -> bool:
        """
        Check if the given range is within set boundaries.

        Returns True if boundaries are undefined or the range fits within them.
        """
        return not self.boundaries or (
            min_val > self.boundaries[0] and max_val < self.boundaries[1]
        )


class LasSiMap:
    """Mapper from las_units to si_units with conversion functions."""

    def __init__(self) -> None:
        """Initialize the class LasSiMap."""
        self._las_to_ranges_by_mnemonic = {}  # las a si por mnemotecnica
        self._si_to_las_by_mnemonic = {}  # si a las por mnemotecnica

    def add(
        self,
        mnemonic: str,
        las_unit: str,
        ranges: str | list[Range] | tuple[Range],
        confidence: int = 0,
        comment: str = "- not indicated",
    ) -> None:
        """Add to the unit conversion dictionaries by classifying from mnemonics."""
        if not isinstance(ranges, (tuple, list)):
            ranges = (
                [Range(ranges, (), confidence, comment)]
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
    def _las_to_Range(  # noqa: N802 👈 ruff se queda de la 'R'
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

    def las_to_si_diagnosis(
        self,
        mnemonic: str,
        las_unit: str,
        data: list[Any],
    ) -> types.Diagnosis:
        """Convert a LAS unit to SI Diagnosis using mnemonic."""
        _range = self._las_to_Range(mnemonic, las_unit, data)
        [v_min, v_med, v_max] = stats.quantiles_values(data, [0, 0.5, 1])
        n_nan = stats.count_missing_values(data)

        if _range is not None:
            si_unit = _range.unit
            confidence = _range.confidence
            comment = _range.comment
        else:
            si_unit = ""
            confidence = 0
            comment = f"- {las_unit} for {lasio_utils.remove_lasio_suffix(mnemonic)}"

        diagnosis = types.Diagnosis(
            mnemonic=mnemonic,
            las_unit=las_unit,
            data=data,
            si_unit=si_unit,
            confidence=confidence,
            comment=comment,
            v_min=v_min,
            v_med=v_med,
            v_max=v_max,
            n_nan=n_nan,
        )
        return diagnosis

    def las_to_si(self, mnemonic: str, las_unit: str, data: list[Any]) -> str:
        """Convert a LAS unit to SI using mnemonic and diagnosis."""
        si_dict = self.las_to_si_diagnosis(mnemonic, las_unit, data)
        return si_dict["si_unit"]
