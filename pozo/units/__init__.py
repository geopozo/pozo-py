import os
import warnings

from lasio import CurveItem
from pint import Unit, UnitRegistry, get_application_registry

import pozo

from . import LasMap, registry_config
from .errors import MissingLasUnitWarning, MissingRangeError, UnitException

os.environ["PINT_ARRAY_PROTOCOL_FALLBACK"] = "0"  # from numpy/pint documentation

las_map = LasMap()
registry: UnitRegistry = get_application_registry()
Quantity = Q = registry.Quantity

registry_config.registry_mapping(las_map)
registry_config.registry_defines(registry)


def check_las(data):
    pass


def parse_unit_safe(unit: str):
    try:
        return registry.parse_units(unit)
    except Exception as e:
        warnings.warn(f"Couldn't parse unit: {e}", MissingLasUnitWarning)
        return None


def _try_parse_unit_with_fallback(unit: str, mnemonic: str) -> Unit:
    try:
        return registry.parse_units(unit)
    except Exception as e:
        raise UnitException(
            f"'{unit}' for '{pozo.deLASio(mnemonic)}' not found."
        ) from e


def parse_unit_from_curve(curve: CurveItem) -> Unit:
    try:
        resolved = las_map.resolve_las_unit(curve.mnemonic, curve.unit, curve.data)
        if resolved is not None:
            return registry.parse_units(resolved.unit)
    except MissingRangeError as e:
        warnings.warn(str(e))

    if not curve.unit or curve.unit == "":
        raise UnitException("Empty unit not allowed- please map it")

    return _try_parse_unit_with_fallback(curve.unit, curve.mnemonic)


def parse_unit_to_las(mnemonic: str, unit: str | Unit):
    unit = unit if isinstance(unit, Unit) else registry.parse_units(unit)
    mnemonic = pozo.deLASio(mnemonic)
    return las_map.get_las_unit(mnemonic, unit)
