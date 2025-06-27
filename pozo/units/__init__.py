import os
import warnings

from lasio import CurveItem
from pint import Unit, UnitRegistry, get_application_registry

import pozo

from .errors import MissingLasUnitWarning, MissingRangeError, UnitException
from .units import LasMap
from . import registry_config

os.environ["PINT_ARRAY_PROTOCOL_FALLBACK"] = "0"  # from numpy/pint documentation

las_map = LasMap()
registry: UnitRegistry = get_application_registry()
Quantity = Q = registry.Quantity

registry_config.registry_mapping(las_map)
registry_config.registry_defines(registry)


def check_las(data):
    pass


def parse_unit_safe(unit: str) -> Unit | None:
    try:
        return registry.parse_units(unit)
    except Exception as e:
        warnings.warn(f"Couldn't parse unit: {e}", MissingLasUnitWarning)
        return None


def parse_unit_from_context(mnemonic: str, unit: str, data) -> Unit | Exception:
    try:
        resolved = las_map.resolve_las_unit(mnemonic, unit, data)
    except MissingRangeError as e:
        warnings.warn(str(e))
    if resolved is not None:
        return parse_unit_safe(resolved.unit)
    else:
        try:
            if not unit or unit == "":
                raise UnitException("Empty unit not allowed- please map it")
            return parse_unit_safe(unit)
        except Exception as e:
            raise UnitException(
                f"'{unit}' for '{pozo.deLASio(mnemonic)}' not found."
            ) from e


def parse_unit_from_curve(curve: CurveItem) -> Unit | Exception:
    return parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)


def parse_unit_to_las(mnemonic: str, unit: str | Unit) -> str:
    unit = unit if isinstance(unit, Unit) else registry.parse_units(unit)
    mnemonic = pozo.deLASio(mnemonic)
    return las_map.get_las_unit(mnemonic, unit)
