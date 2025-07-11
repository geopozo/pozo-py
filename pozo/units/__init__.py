import os
import re
import warnings

import pint
from lasio import LASFile

from pozo.units import errors
from pozo.units.las_si import las_si_config, las_si_map
from pozo.units.si_pint import si_pint_config
from pozo.utils import _table, display, lasio_utils, stats, types

os.environ["PINT_ARRAY_PROTOCOL_FALLBACK"] = "0"  # from numpy/pint documentation

_delimiter = chr(0x1E)

las_map = las_si_map.LasSiMap()
las_si_config.add_to_las_si_map(las_map)

registry: pint.UnitRegistry = pint.get_application_registry()
Quantity = Q = registry.Quantity
si_pint_config.add_to_pint(registry)


def check_las(las: LASFile, HTML_out=True, div_id="") -> None:
    """
    Check the data from the LAS file and print a table with the analysis.
    """

    def n0(s):
        return "" if s is None else str(s)

    with warnings.catch_warnings():
        warnings.simplefilter("default")
        warnings.filterwarnings("error", category=errors.MissingLasUnitWarning)

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
                resolved = las_map.get_las_unit_to_si_unit_range(
                    curve.mnemonic, curve.unit, curve.data
                )
                if resolved is not None:
                    pozo_match = resolved.unit
                    confidence = resolved.confidence
                parsed = parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)

                if resolved is None:
                    raise errors.MissingLasUnitWarning(
                        "Parsed directly from LAS, probably wrong"
                    )
            except (
                errors.MissingRangeError,
                errors.UnitException,
                errors.MissingLasUnitWarning,
            ) as e:
                confidence = f" - {str(e)} - NONE"

            desc_match = desc_wo_num.findall(curve.descr)
            desc = desc_match[0] if len(desc_match) > 0 else curve.descr

            [v_min, v_med, v_max] = stats.get_string_quantiles(
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
                result.append(curve_data)
            else:
                result.append(_delimiter.join([n0(x) for x in curve_data.values()]))

        if not HTML_out:
            return result

        try:
            html_output = _table.generate_html_table(result, _delimiter)
            display.show_content(f'<div id="{div_id}">{html_output}</div>', html=True)

        except Exception as e:
            display.show_content(str(e))
            display.show_content("<br>".join(result), html=True)


def parse_unit_safe(unit: str) -> pint.Unit | None:
    """
    Parse the unit by returning a Unit object from pint and catch the error if it occurs
    """
    try:
        return registry.parse_units(unit)
    except Exception as e:
        warnings.warn(f"Couldn't parse unit: {e}", errors.MissingLasUnitWarning)
        return None


def parse_unit_from_context(
    mnemonic: str,
    si_unit: str,
    data: types.Array,
) -> pint.Unit | Exception:
    """
    Parses a unit string using context from mnemonic and data.

    Attempts to resolve the unit via LAS mappings first;
    Raises UnitException if the unit is empty or missing.
    """
    try:
        resolved = las_map.get_las_unit_to_si_unit_range(mnemonic, si_unit, data)
    except errors.MissingRangeError as e:
        warnings.warn(str(e))
    if resolved is not None:
        return parse_unit_safe(resolved.unit)
    else:
        try:
            if not si_unit:
                raise errors.UnitException("Empty unit not allowed- please map it")
            return parse_unit_safe(si_unit)
        except Exception as e:
            raise errors.UnitException(
                f"'{si_unit}' for '{lasio_utils.remove_lasio_suffix(mnemonic)}' not found."
            ) from e


def parse_unit_from_curve(curve: types.Curve) -> pint.Unit | Exception:
    """
    Parses the unit from a Curve object and returns a Unit
    """
    return parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)


def parse_unit_to_las(mnemonic: str, pint_unit: str | pint.Unit | None) -> str:
    """
    Parse the unit returning the LAS value mapped from a mnemonic
    """
    pint_unit = (
        pint_unit
        if isinstance(pint_unit, pint.Unit)
        else registry.parse_units(pint_unit)
    )
    mnemonic = lasio_utils.remove_lasio_suffix(mnemonic)
    return las_map.get_si_unit_to_las_unit(mnemonic, pint_unit)
