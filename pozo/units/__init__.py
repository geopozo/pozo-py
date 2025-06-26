import os

import pint

from .units import LasUnitRegistry

os.environ["PINT_ARRAY_PROTOCOL_FALLBACK"] = "0"  # from numpy/pint documentation

las_registry = LasUnitRegistry()
unit_registry = pint.UnitRegistry()
Quantity = Q = unit_registry.Quantity
