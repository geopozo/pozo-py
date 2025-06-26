import os

import pint

from .units import LasMap

os.environ["PINT_ARRAY_PROTOCOL_FALLBACK"] = "0"  # from numpy/pint documentation

las_map = LasMap()
unit_registry = pint.UnitRegistry()
Quantity = Q = unit_registry.Quantity


def check_las(data):
    pass


def parse_unit_from_curve(curve):
    pass


def set_unit_registry(new_registry):
    global unit_registry
    unit_registry = new_registry
