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


class UnitMapper:
    def __init__(self):
        self._mnemonic_to_units = {}
        self._units_to_mnemonic = {}

    def register_mapping(self, mnemonic, unit, ranges):
        if mnemonic not in self._mnemonic_to_units:
            self._mnemonic_to_units[mnemonic] = {}
            self._units_to_mnemonic[mnemonic] = {}

        self._mnemonic_to_units[mnemonic][unit] = ranges

        for ra in ranges:
            parsed_unit = ra.unit
            self._units_to_mnemonic[mnemonic][parsed_unit] = unit

    def get_entries(self, mnemonic, unit):
        if (
            mnemonic in self._mnemonic_to_units
            and unit in self._mnemonic_to_units[mnemonic]
        ):
            return self._mnemonic_to_units[mnemonic][unit]
        if "-" in self._mnemonic_to_units and unit in self._mnemonic_to_units["-"]:
            return self._mnemonic_to_units["-"][unit]
        return None


# Namespace would be nicer and I could hide registries if this wasn't overriden
# But would the map be global?
# Or would we just use a default register like in init
class LasUnitRegistry(pint.UnitRegistry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.mapper = UnitMapper()

    def add_las_map(self, mnemonic, unit, ranges, confidence="- not indicated - LOW"):
        if not isinstance(ranges, list):
            ranges = (
                [RangeBoundaries((), ranges, confidence)]
                if not isinstance(ranges, RangeBoundaries)
                else [ranges]
            )

        for ra in ranges:
            if not isinstance(ra, RangeBoundaries):
                raise TypeError("All entries must be of type RangeBoundaries.")
            self.parse_units(ra.unit)

        self.mapper.register_mapping(mnemonic, unit, ranges)

    def resolve_SI_unit_to_las(self, mnemonic, unit):
        unit = unit if isinstance(unit, pint.Unit) else self.parse_units(unit)
        # TODO: looking up the dimension would be nice
        mnemonic = pozo.deLASio(mnemonic)
        if (
            mnemonic in self._units_to_mnemonic
            and unit in self._units_to_mnemonic[mnemonic]
        ):
            return self._units_to_mnemonic[mnemonic][unit]
        elif unit in self._units_to_mnemonic["-"]:
            return self._units_to_mnemonic["-"][unit]
        else:
            return None

    def resolve_las_unit(self, mnemonic, unit, data):
        mnemonic = pozo.deLASio(mnemonic)
        max_val = np.nanmax(data)
        min_val = np.nanmin(data)
        ranges = self.mapper.get_entries(mnemonic, unit)

        if ranges:
            for ra in ranges:
                if ra.is_within_range(min_val, max_val):
                    return ra
            raise MissingRangeError(
                f"{unit} for {mnemonic} found but not in range: {ranges}."
            )
        return None

    # this just gives you a result
    def parse_unit_from_context(self, mnemonic, unit, data):
        resolved = None
        try:
            resolved = self.resolve_las_unit(mnemonic, unit, data)
        except MissingRangeError as e:
            warnings.warn(str(e))
        if resolved is not None:
            try:
                return self.parse_units(resolved.unit)
            except Exception as e:
                warnings.warn(f"Couldn't parse unit: {e}", MissingLasUnitWarning)
                return None
        else:
            try:
                if not unit or unit == "":
                    raise UnitException("Empty unit not allowed- please map it")
                try:
                    return self.parse_units(unit)
                except Exception as e:
                    warnings.warn(f"Couldn't parse unit: {e}", MissingLasUnitWarning)
                    return None
            except pint.UndefinedUnitError as e:
                raise UnitException(
                    f"'{unit}' for '{pozo.deLASio(mnemonic)}' not found."
                ) from e


# we now don't get confidence from string
