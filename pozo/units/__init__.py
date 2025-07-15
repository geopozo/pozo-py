from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING

import pint  # type: ignore[import-untyped]

from pozo.units.las_si import config as las_si_config
from pozo.units.las_si import mapper as las_si_mapper
from pozo.units.si_pint import config as si_pint_config
from pozo.utils import _lasio, _table, display, stats, types

if TYPE_CHECKING:
    import lasio  # type: ignore[import-untyped]

os.environ["PINT_ARRAY_PROTOCOL_FALLBACK"] = "0"  # from numpy/pint documentation

# Conexión a LasSiMap
las_map = las_si_mapper.LasSiMap()
las_si_config.add_to_las_si_map(las_map)

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
) -> list[str] | None:
    """Check the data from the LAS file and print a table with the analysis."""

    def n0(s: str | pint.Unit | int | None) -> str:
        return "" if s is None else str(s)

    col_names = [
        "mnemonic",
        "las unit",
        "pozo mapping",
        "confidence",
        "parsed",
        "description",
        "min",
        "med",
        "max",
        "#NaN",
    ]

    result = [_delimiter.join(col_names)] if html else []
    for curve in las.curves:
        _range = None
        si_unit = None
        confidence = None
        parsed = None
        try:
            _range = las_map._las_to_Range(curve.mnemonic, curve.unit, curve.data)
            if _range is not None:
                si_unit = _range.unit
                confidence = _range.confidence
            parsed = parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)

        except UnitException as e:
            confidence = f" - {str(e)} - NONE"

        # TODO: lasio utilidad 👇
        desc_wo_num = re.compile(r"^(?:\s*\d+\s+)?(.*)$")
        desc_match = desc_wo_num.findall(curve.descr)
        desc = desc_match[0] if len(desc_match) > 0 else curve.descr

        [v_min, v_med, v_max] = stats.quantiles_values(
            curve.data,
            [0, 0.5, 1],
        )
        n_nan = stats.count_missing_values(curve.data)

        curve_data = dict(
            mnemonic=curve.mnemonic,
            las_unit=curve.unit,
            pozo_match=si_unit,
            confidence=confidence,
            parsed_unit=parsed,
            desc=desc,
            v_min=v_min,
            v_med=v_med,
            v_max=v_max,
            n_nan=n_nan,
        )
        if not html:
            result.append(curve_data)
            return result
        else:
            result.append(_delimiter.join([n0(x) for x in curve_data.values()]))

    try:
        html_output = _table.generate_html_table(result, _delimiter)
        display.show_content(
            f'<div id="{div_id}">{html_output}</div>',
            html=html,
        )

    except Exception as e:
        display.show_content(str(e))
        display.show_content("<br>".join(result), html=html)

    return None


def parse_unit_safe(
    unit: str
    | pint.Unit,  # esta api debe ser igual a lo de pint, si pint acepta pint.Unit, debe aceptar pint.Unit, o visceversa
) -> pint.Unit | None:
    """Parse the unit by returning a Unit object from pint and catch the error."""
    try:
        return registry.parse_units(unit)
    except pint.UndefinedUnitError:
        return None


class UnitException(Exception):
    """Raised when unit parsing fails."""

    pass


def parse_unit_from_context(
    mnemonic: str,
    las_unit: str,
    data: types.Array,
) -> pint.Unit | None:
    """
    Parse a unit string using context from mnemonic and data.

    Attempts to resolve the unit via LAS mappings first;
    Raises UnitException if the unit is empty or missing.
    """
    _range = las_map._las_to_Range(mnemonic, las_unit, data)

    return (
        parse_unit_safe(_range.unit)
        if _range is not None
        else parse_unit_safe(las_unit)
    )


def parse_unit_from_curve(curve: types.Curve) -> pint.Unit | None:
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
