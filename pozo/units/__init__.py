import os

from pint import UnitRegistry, get_application_registry, set_application_registry

from .registry_config import registry_defines, registry_mapping
from .units import LasMap

os.environ["PINT_ARRAY_PROTOCOL_FALLBACK"] = "0"  # from numpy/pint documentation

las_map = LasMap()
registry: UnitRegistry = get_application_registry()
Quantity = Q = registry.Quantity

registry_mapping(las_map)
registry_defines(registry)


def check_las(data):
    pass


def parse_unit_from_curve(curve):
    pass


def set_unit_registry(registry: UnitRegistry):
    set_application_registry(registry)
