import os
import re
import warnings

import lasio  # type: ignore
import pint  # type: ignore

from pozo.units.las_si import config as las_si_config
from pozo.units.las_si import mapper as las_si_mapper
from pozo.units.si_pint import config as si_pint_config
from pozo.utils import _lasio, _table, display, stats, types

os.environ["PINT_ARRAY_PROTOCOL_FALLBACK"] = "0"  # from numpy/pint documentation

# Conexión a LasSiMap
las_map = las_si_mapper.LasSiMap()
las_si_config.add_to_las_si_map(las_map)

# Conexión a pint
registry: pint.registry.ApplicationRegistry = pint.get_application_registry()
Quantity = Q = registry.Quantity
si_pint_config.add_to_pint(registry)

_delimiter = chr(0x1E)


class MissingLasUnitWarning(UserWarning):
    """Warning for unresolved LAS units."""

    pass


def check_las(las: lasio.LASFile, HTML_out=True, div_id="") -> list[str] | None:
    """
    Check the data from the LAS file and print a table with the analysis.
    """

    def n0(s):
        return "" if s is None else str(s)

    with warnings.catch_warnings():
        warnings.simplefilter("default")
        warnings.filterwarnings("error", category=MissingLasUnitWarning)

        desc_wo_num = re.compile(r"^(?:\s*\d+\s+)?(.*)$")
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

        result = [_delimiter.join(col_names)] if HTML_out else []
        for curve in las.curves:
            resolved = None
            pozo_match = None
            confidence = None
            parsed = None
            try:
                resolved = las_map.las_to_Range(curve.mnemonic, curve.unit, curve.data)
                if resolved is not None:
                    pozo_match = resolved.unit
                    confidence = resolved.confidence
                parsed = parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)

                if resolved is None:
                    raise MissingLasUnitWarning(
                        "Parsed directly from LAS, probably wrong"
                    )
            except (
                UnitException,
                MissingLasUnitWarning,
            ) as e:
                confidence = f" - {str(e)} - NONE"

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
                pozo_match=pozo_match,
                confidence=confidence,
                parsed_unit=parsed,
                desc=desc,
                v_min=v_min,
                v_med=v_med,
                v_max=v_max,
                n_nan=n_nan,
            )
            if not HTML_out:
                # Tengo mis dudas sobre 👇 esa solución del pato agrega el casteo
                result.append(str(curve_data))
                return result
            else:
                result.append(_delimiter.join([n0(x) for x in curve_data.values()]))

        try:
            html_output = _table.generate_html_table(result, _delimiter)
            display.show_content(
                f'<div id="{div_id}">{html_output}</div>',
                html=HTML_out,
            )

        except Exception as e:
            display.show_content(str(e))
            display.show_content("<br>".join(result), html=HTML_out)

    return None


def parse_unit_safe(
    unit: str | tuple[las_si_mapper.Range] | pint.Unit | None,
) -> pint.Unit | None:
    """
    Parse the unit by returning a Unit object from pint and catch the error if it occurs
    """
    try:
        return registry.parse_units(unit)
    except Exception as e:
        warnings.warn(f"Couldn't parse unit: {e}", MissingLasUnitWarning)
        return None


class UnitException(Exception):
    """Raised when unit parsing fails."""

    pass


def parse_unit_from_context(
    mnemonic: str,
    si_unit: str | pint.Unit | None,
    data: types.Array,
) -> pint.Unit | None:
    """
    Parses a unit string using context from mnemonic and data.

    Attempts to resolve the unit via LAS mappings first;
    Raises UnitException if the unit is empty or missing.
    """

    resolved = las_map.las_to_Range(mnemonic, si_unit, data)

    if resolved is not None:
        return parse_unit_safe(resolved.unit)
    else:
        try:
            if not si_unit:
                raise UnitException("Empty unit not allowed- please map it")
            return parse_unit_safe(si_unit)
        except Exception as e:
            raise UnitException(
                f"'{si_unit}' for '{_lasio.remove_lasio_suffix(mnemonic)}' not found."
            ) from e


def parse_unit_from_curve(curve: types.Curve) -> pint.Unit | None:
    """
    Parses the unit from a Curve object and returns a Unit
    """
    return parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)


def parse_unit_to_las(mnemonic: str, pint_unit: str | pint.Unit | None) -> str | None:
    """
    Parse the unit returning the LAS value mapped from a mnemonic
    """
    mnemonic = _lasio.remove_lasio_suffix(mnemonic)
    pint_unit = (
        pint_unit
        if isinstance(pint_unit, pint.Unit)
        else registry.parse_units(pint_unit)
    )
    return las_map.si_to_las_unit(mnemonic, pint_unit)
