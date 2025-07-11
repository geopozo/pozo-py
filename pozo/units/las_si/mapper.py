from typing import Any

from pozo.units import errors
from pozo.utils import _lasio as lasio_utils
from pozo.utils import stats


class RangeBoundaries:
    def __init__(
        self, boundaries, las_unit: str | tuple["RangeBoundaries"], confidence
    ):
        if not isinstance(boundaries, tuple) or len(boundaries) not in {0, 2}:
            raise TypeError(
                "boundaries should contain a tuple with (min, max) or () catch-all"
            )

        self.boundaries = boundaries
        self.unit = las_unit
        self.confidence = confidence

    def is_within_range(self, min_val, max_val):
        return len(self.boundaries) == 0 or (
            min_val > self.boundaries[0] and max_val < self.boundaries[1]
        )


class LasSiMap:
    def __init__(self):
        self._las_to_si_by_mnemonic = {}  # las a si por mnemotecnica
        self._si_to_las_by_mnemonic = {}  # si a las por mnemotecnica

    def set_default(self, mnemonic):
        self._las_to_si_by_mnemonic[mnemonic] = {}
        self._si_to_las_by_mnemonic[mnemonic] = {}

    def add(
        self,
        mnemonic: str,
        las_unit: str,
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

        if mnemonic not in self._las_to_si_by_mnemonic:
            self.set_default(mnemonic)

        self._las_to_si_by_mnemonic[mnemonic][las_unit] = ranges

        for range in ranges:
            self._si_to_las_by_mnemonic[mnemonic][range.unit] = las_unit

    def get_las_unit_to_si_unit_range(
        self,
        mnemonic: str,
        las_unit: str,
        data: list[Any],
    ) -> RangeBoundaries | None:
        mnemonic = lasio_utils.remove_lasio_suffix(mnemonic)
        max_val = stats.get_max_value(data)
        min_val = stats.get_min_value(data)
        ranges = None

        if (
            mnemonic in self._las_to_si_by_mnemonic
            and las_unit in self._las_to_si_by_mnemonic[mnemonic]
        ):
            ranges: list[RangeBoundaries] = self._las_to_si_by_mnemonic[mnemonic][
                las_unit
            ]
        elif las_unit in self._las_to_si_by_mnemonic["-"]:
            ranges = self._las_to_si_by_mnemonic["-"][las_unit]

        if ranges:
            for range in ranges:
                if range.is_within_range(min_val, max_val):
                    return range
            raise errors.MissingRangeError(
                f"{las_unit} for {mnemonic} found but not in range: {ranges}."
            )
        return None

    def get_si_unit_to_las_unit(
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
