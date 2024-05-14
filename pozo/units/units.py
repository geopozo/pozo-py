import os
import warnings

import numpy as np
import pozo
os.environ['PINT_ARRAY_PROTOCOL_FALLBACK'] = "0" # from numpy/pint documentation
import pint # noqa

class MissingLasUnitWarning(UserWarning):
    pass

class UnitException(Exception):
    pass

class MissingRangeError(Exception):
    pass

class LasMapEntry():
    def  __init__(self, boundries, unit, confidence):
        if not isinstance(boundries, tuple) or not (len(boundries) == 0 or len(boundries) == 2):
            raise TypeError("add_las_map ranges should contain a tuple with (min, max) or () catch-all")
        self.boundries = boundries
        self.unit = unit
        self.confidence = confidence

    def check(self, min_val, max_val):
        if len(self.boundries) == 0:
            return True
        elif min_val > self.boundries[0] and max_val < self.boundries[1]:
            return True
        return False

# Namespace would be nicer and I could hide registries if this wasn't overriden
# But would the map be global?
# Or would we just use a default registery like in init
class LasRegistry(pint.UnitRegistry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mnemonic_units = {}
        self._reverse_mnemonic_units = {}

    def add_las_map(self, mnemonic, unit, ranges, confidence="- not indicated - LOW"):
        if not isinstance(ranges, list):
            if not isinstance(ranges, LasMapEntry):
                ranges = [LasMapEntry((), ranges, confidence)]
            else:
                ranges = [ranges]
        for ra in ranges:
            if not isinstance(ra, LasMapEntry):
                raise TypeError("Improperly formated map for LasMap, should be type LasMapEntry")
            self.parse_units(ra.unit) # Can't check in LasMapEntry because don't have registry
        if mnemonic not in self._mnemonic_units:
            self._mnemonic_units[mnemonic] = {}
            self._reverse_mnemonic_units[mnemonic] = {}
        self._mnemonic_units[mnemonic][unit] = ranges
        for ra in ranges:
            self._reverse_mnemonic_units[mnemonic][self.parse_units(ra.unit)] = unit # doesn't this override

    def resolve_SI_unit_to_las(self, mnemonic, unit):
        unit = unit if isinstance(unit, pint.Unit) else self.parse_units(unit)
        # TODO: looking up the dimension would be nice
        mnemonic = pozo.deLASio(mnemonic)
        if mnemonic in self._reverse_mnemonic_units and unit in self._reverse_mnemonic_units[mnemonic]:
            return self._reverse_mnemonic_units[mnemonic][unit]
        elif unit in self._reverse_mnemonic_units["-"]:
            return self._reverse_mnemonic_units["-"][unit]
        else: return None


    def resolve_las_unit(self, mnemonic, unit, data):
        mnemonic = pozo.deLASio(mnemonic)
        # unit = unit
        max_val = np.nanmax(data)
        min_val = np.nanmin(data)
        ranges = None
        if mnemonic in self._mnemonic_units and unit in self._mnemonic_units[mnemonic]:
            ranges = self._mnemonic_units[mnemonic][unit]
        elif unit in self._mnemonic_units["-"]:
            ranges = self._mnemonic_units["-"][unit]
        if ranges:
            for ra in ranges:
                if ra.check(min_val, max_val):
                    return ra
            raise MissingRangeError(f"{unit} for {mnemonic} found but not in range: {ranges}.")
        return None

    def parse_unit_from_context(self, mnemonic, unit, data): # this just gives you a result
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
                if not unit or unit == "": raise UnitException("Empty unit not allowed- please map it")
                try:
                    return self.parse_units(unit)
                except Exception as e:
                    warnings.warn(f"Couldn't parse unit: {e}", MissingLasUnitWarning)
                    return None
            except pint.UndefinedUnitError as e:
                raise UnitException(f"'{unit}' for '{pozo.deLASio(mnemonic)}' not found.") from e

# we now don't get confidence from string

