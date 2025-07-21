"""API to connect pint registry and LasSiMap."""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

os.environ["PINT_ARRAY_PROTOCOL_FALLBACK"] = "0"  # from numpy/pint documentation
import pint  # type: ignore[import-untyped]

from pozo.units.las_si import config as las_si_config
from pozo.units.las_si import mapper as las_si_mapper
from pozo.units.si_pint import config as si_pint_config
from pozo.utils import _lasio, _table, display, types

if TYPE_CHECKING:
    import lasio  # type: ignore[import-untyped]


# Conexión a LasSiMap
las_map = las_si_mapper.LasSiMap()
for unit_args in las_si_config.las_si_map:
    las_map.add(*unit_args)  # type: ignore[arg-type], para Pyright

# Conexión a pint
registry: pint.registry.ApplicationRegistry = pint.get_application_registry()
Quantity = Q = registry.Quantity
si_pint_config.add_to_pint(registry)


_delimiter = chr(0x1E)


def check_las(
    las: lasio.LASFile,
    *,
    html: bool = True,
    div_id: str = "",
) -> list[str | dict[str, str]] | None:
    """Check the data from the LAS file and print a table with the analysis."""

    def n0(s: str | pint.Unit | int | None) -> str:
        return "" if s is None else str(s)

    result: list[str | dict[str, str]] = []
    for i, curve in enumerate(las.curves):
        diagnosis = las_map.las_to_si_diagnosis(curve.mnemonic, curve.unit, curve.data)
        parsed = parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)
        descr = _lasio.remove_prefix_number(curve.descr)

        curve_data = {
            "mnemonic": curve.mnemonic,
            "las unit": curve.unit,
            "si unit": diagnosis.get("si_unit"),
            "pint unit": parsed,
            "confidence": diagnosis.get("confidence"),
            "comment:": diagnosis.get("comment"),
            "description": descr,
            "min": diagnosis.get("v_min"),
            "med": diagnosis.get("v_med"),
            "max": diagnosis.get("v_max"),
            "#NaN": diagnosis.get("n_nan"),
        }

        if i == 0 and html:
            result.append(_delimiter.join(curve_data.keys()))

        if not html:
            result.append(curve_data)
        else:
            result.append(_delimiter.join([n0(x) for x in curve_data.values()]))

    if not html:
        return result

    html_output = _table.colorize_html_table(result, _delimiter)
    display.show_html(
        f'<div id="{div_id}">{html_output}</div>',
        html=html,
    )

    return None


def parse_unit_safe(unit: str) -> pint.Unit | None:
    """Parse the unit by returning a Unit object from pint and catch the error."""
    try:
        return registry.parse_units(unit)
    except pint.UndefinedUnitError:
        return None


def parse_unit_from_context(
    mnemonic: str,
    las_unit: str,
    data: types.Array,
) -> pint.Unit | None:
    """Parse a unit string using context from mnemonic and data."""
    si_unit = las_map.las_to_si(mnemonic, las_unit, data)

    return (
        parse_unit_safe(si_unit) if si_unit is not None else parse_unit_safe(las_unit)
    )


def get_unit_from_curve(curve: types.Curve) -> pint.Unit | None:
    """Parse the unit from a Curve object and returns a Unit."""
    return parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)


def parse_unit_to_las(mnemonic: str, pint_unit: str | pint.Unit) -> str | None:
    """Parse the unit returning the LAS value mapped from a mnemonic."""
    mnemonic = _lasio.remove_lasio_suffix(mnemonic)
    pint_unit = (
        pint_unit
        if isinstance(pint_unit, pint.Unit)
        else registry.parse_units(pint_unit)
    )

    return las_map.si_to_las_unit(mnemonic, str(pint_unit))
