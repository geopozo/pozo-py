import os
import warnings

import numpy as np
import pint  # noqa

import pozo

from .errors import MissingLasUnitWarning, MissingRangeError, UnitException

os.environ["PINT_ARRAY_PROTOCOL_FALLBACK"] = "0"  # from numpy/pint documentation


class RangeBoundaries:
    def __init__(self, boundaries, unit, confidence):
        if not isinstance(boundaries, tuple) or len(boundaries) not in {0, 2}:
            raise TypeError(
                "add_las_map ranges should contain a tuple with (min, max) or () catch-all"
            )

        self.boundaries = boundaries
        self.unit = unit
        self.confidence = confidence

    def is_within_range(self, min_val, max_val):
        if len(self.boundaries) == 0:
            return True
        elif min_val > self.boundaries[0] and max_val < self.boundaries[1]:
            return True
        return False


class LasUnitRegistry:
    def __init__(self, *, unit_registry):
        self.unit_registry = unit_registry
        self._mnemonic_to_units = {}
        self._units_to_mnemonic = {}

    def set_unit_registry(self, unit_registry):
        """Set a new unit registry."""
        self.unit_registry = unit_registry

    def parse(self, unit):
        """Parse a unit string using the current unit registry."""
        if not hasattr(self.unit_registry, "parse_units"):
            raise AttributeError("unit_registry does not have a 'parse_units' method")
        return self.unit_registry.parse_units(unit)

    def add_las_map(self, mnemonic, unit, ranges, confidence="- not indicated - LOW"):
        """Add a mapping between a mnemonic and a unit with associated ranges."""
        if not isinstance(ranges, list):
            ranges = (
                [RangeBoundaries((), ranges, confidence)]
                if not isinstance(ranges, RangeBoundaries)
                else [ranges]
            )

        for ra in ranges:
            if not isinstance(ra, RangeBoundaries):
                raise TypeError("All entries must be of type RangeBoundaries.")
            self.parse(ra.unit)

        self._mnemonic_to_units_mapper(mnemonic, unit, ranges)

    def resolve_SI_unit_to_las(self, mnemonic, unit):
        """Resolve a SI unit to its corresponding LAS unit for a given mnemonic."""
        unit = unit if isinstance(unit, pint.Unit) else self.parse(unit)
        mnemonic = pozo.deLASio(mnemonic)
        return self._si_unit_to_las_unit_mapper(mnemonic, unit)

    def resolve_las_unit(self, mnemonic, unit, data):
        """Resolve the appropriate LAS unit based on data range and mnemonic."""
        mnemonic = pozo.deLASio(mnemonic)
        max_val = np.nanmax(data)
        min_val = np.nanmin(data)
        ranges = self._ranges_for_unit_mapper(mnemonic, unit)

        if ranges:
            for ra in ranges:
                if ra.is_within_range(min_val, max_val):
                    return ra
            raise MissingRangeError(
                f"{unit} for {mnemonic} found but not in range: {ranges}."
            )
        return None

    def parse_unit_from_context(self, mnemonic, unit, data):
        try:
            resolved = self.resolve_las_unit(mnemonic, unit, data)
            if resolved is not None:
                return self._try_parse_unit(resolved.unit)
        except MissingRangeError as e:
            warnings.warn(str(e))

        if not unit or unit == "":
            raise UnitException("Empty unit not allowed- please map it")

        return self._try_parse_unit_with_fallback(unit, mnemonic)

    def _try_parse_unit(self, unit_str):
        try:
            return self.parse(unit_str)
        except Exception as e:
            warnings.warn(f"Couldn't parse unit: {e}", MissingLasUnitWarning)
            return None

    def _try_parse_unit_with_fallback(self, unit, mnemonic):
        try:
            return self._try_parse_unit(unit)
        except Exception as e:
            raise UnitException(
                f"'{unit}' for '{pozo.deLASio(mnemonic)}' not found."
            ) from e

    def _mnemonic_to_units_mapper(self, mnemonic, unit, ranges):
        if mnemonic not in self._mnemonic_to_units:
            self._mnemonic_to_units[mnemonic] = {}
            self._units_to_mnemonic[mnemonic] = {}

        self._mnemonic_to_units[mnemonic][unit] = ranges

        for ra in ranges:
            parsed_unit = ra.unit
            self._units_to_mnemonic[mnemonic][parsed_unit] = unit

    def _ranges_for_unit_mapper(self, mnemonic, unit):
        if (
            mnemonic in self._mnemonic_to_units
            and unit in self._mnemonic_to_units[mnemonic]
        ):
            return self._mnemonic_to_units[mnemonic][unit]
        if "-" in self._mnemonic_to_units and unit in self._mnemonic_to_units["-"]:
            return self._mnemonic_to_units["-"][unit]
        return None

    def _si_unit_to_las_unit_mapper(self, mnemonic, si_unit):
        if (
            mnemonic in self._units_to_mnemonic
            and si_unit in self._units_to_mnemonic[mnemonic]
        ):
            return self._units_to_mnemonic[mnemonic][si_unit]
        if "-" in self._units_to_mnemonic and si_unit in self._units_to_mnemonic["-"]:
            return self._units_to_mnemonic["-"][si_unit]
        return None
