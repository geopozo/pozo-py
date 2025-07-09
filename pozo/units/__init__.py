import os
import re
import warnings

import numpy as np
from IPython.display import HTML, display
from lasio import CurveItem, LASFile
from pint import Unit, UnitRegistry, get_application_registry

import pozo

from . import las_si, si_pint
from ._table_utils import generate_html_table
from .errors import MissingLasUnitWarning, MissingRangeError, UnitException

os.environ["PINT_ARRAY_PROTOCOL_FALLBACK"] = "0"  # from numpy/pint documentation
from .units import LasSiMap

_delimiter = chr(0x1E)

las_map = LasSiMap()
las_si.add_to_las_map(las_map)

registry: UnitRegistry = get_application_registry()
Quantity = Q = registry.Quantity
si_pint.add_to_pint(registry)


def check_las(las: LASFile, HTML_out=True, div_id="") -> None:
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
                resolved = las_map.resolve_las_unit(
                    curve.mnemonic, curve.unit, curve.data
                )
                if resolved is not None:
                    pozo_match = resolved.unit
                    confidence = resolved.confidence
                parsed = parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)

                if resolved is None:
                    raise MissingLasUnitWarning(
                        "Parsed directly from LAS, probably wrong"
                    )
            except (
                MissingRangeError,
                UnitException,
                MissingLasUnitWarning,
            ) as e:
                confidence = f" - {str(e)} - NONE"

            desc_match = desc_wo_num.findall(curve.descr)
            desc = desc_match[0] if len(desc_match) > 0 else curve.descr

            v_min, v_med, v_max = map(str, np.nanquantile(curve.data, [0, 0.5, 1]))
            n_nan = np.count_nonzero(np.isnan(curve.data))

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
            html_output = generate_html_table(result, _delimiter)
            display(HTML(f'<div id="{div_id}">{html_output}</div>'))

        except Exception as e:
            display(str(e))
            display(HTML("<br>".join(result)))


def parse_unit_safe(unit: str) -> Unit | None:
    """
    Parse the unit by returning a Unit object from pint and catch the error if it occurs
    """
    try:
        return registry.parse_units(unit)
    except Exception as e:
        warnings.warn(f"Couldn't parse unit: {e}", MissingLasUnitWarning)
        return None


def parse_unit_from_context(mnemonic: str, unit: str, data: list) -> Unit | Exception:
    """
    Parses a unit string using context from mnemonic and data.

    Attempts to resolve the unit via LAS mappings first;
    Raises UnitException if the unit is empty or missing.
    """
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
    """
    Parses the unit from a CurveItem object and returns a Unit
    """
    return parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)


def parse_unit_to_las(mnemonic: str, unit: str | Unit) -> str:
    """
    Parse the unit returning the LAS value mapped from a mnemonic
    """
    unit = unit if isinstance(unit, Unit) else registry.parse_units(unit)
    mnemonic = pozo.deLASio(mnemonic)
    return las_map.get_las_unit(mnemonic, unit)
