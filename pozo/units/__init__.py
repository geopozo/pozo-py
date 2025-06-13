import re
import warnings
from io import StringIO

import numpy as np
import pandas as pd
import pint
from IPython.display import HTML, display

from . import registry_config
from .units import (
    LasUnitRegistry,
    MissingLasUnitWarning,
    MissingRangeError,
    UnitException,
)

registry = LasUnitRegistry()
Quantity = Q = registry.unit_registry.Quantity

registry_config.registry_defines(registry)
registry_config.registry_mapping(registry)

_delimiter = chr(0x1E)


def _apply_color_styling(html_str: str, pattern: re.Pattern, color: str):
    for match in pattern.finditer(html_str):
        current_match = match.group()
        colored = f'<td style="color:{color}">' + current_match[4:]
        html_str = html_str.replace(current_match, colored)
    return html_str


def _generate_html_table(data):
    red_low = re.compile(r"<td>(.+)?(?:LOW|NONE)(.+)?</td>")
    orange_medium = re.compile(r"<td>(.+)?MEDIUM(.+)?</td>")
    post_result = "\n".join(data)

    output = pd.read_csv(StringIO(post_result), delimiter=_delimiter, na_filter=False)
    html_output = output.to_html()
    html_output = _apply_color_styling(html_output, red_low, "red")
    html_output = _apply_color_styling(html_output, orange_medium, "#B95000")

    return html_output


def check_las(las, registry=registry, HTML_out=True, div_id=""):
    def n0(s):  # If None, convert to ""
        return "" if s is None else str(s)

    # using the warnings like this kind sucks
    # they do need to be surpressed becuase i'm building a better view into the warnings anyway
    # with this function, but that resolved = on 87 w/ 91 = on 91 is really weird.
    # hate this interface
    # it has to be pulled twice because we need internal info for checklas
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
                resolved = registry.resolve_las_unit(
                    curve.mnemonic, curve.unit, curve.data
                )
                if resolved is not None:
                    pozo_match = resolved.unit
                    confidence = resolved.confidence
                parsed = registry.parse_unit_from_context(
                    curve.mnemonic, curve.unit, curve.data
                )

                if resolved is None:
                    raise MissingLasUnitWarning(
                        "Parsed directly from LAS, probably wrong"
                    )
            except (
                pint.UndefinedUnitError,
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
            html_output = _generate_html_table(result)
            display(HTML(f'<div id="{div_id}">{html_output}</div>'))

        except Exception as e:
            display(str(e))
            display(HTML("<br>".join(result)))


# Just a shortcut to make the API nice
def parse_unit_from_curve(curve, registry=registry):
    try:
        return registry.parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)
    except Exception as e:
        warnings.warn(f"Couldn't parse unit: {e}", MissingLasUnitWarning)
        return None


def parse(unit):
    """
    Parses a unit string using the current unit registry.

    Returns the parsed unit object, or None if parsing fails.
    """
    return registry.parse_unit(unit)
