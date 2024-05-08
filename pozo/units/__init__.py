import numpy as np
import pint
import warnings
from IPython.display import HTML, display
from io import StringIO
import pandas as pd

from .units import MissingRangeError, LasMapEntry
from .units import LasRegistry, UnitException, MissingLasUnitWarning
import re


registry = LasRegistry()
Quantity = Q = registry.Quantity # Overriding the registry and all this is a little weird

registry.define('gamma_API_unit = [Gamma_Ray_Tool_Response]  = gAPI')
registry.define("porosity_unit = percent = pu")
registry.define("of_1 = 100 * percent = fraction")
registry.define("legacy_api_porosity_unit = [Legacy_API_Porosity_Unit] = puAPI")

PU = [
        LasMapEntry((-50, 80), "pu", "decide by range - MEDIUM"),
        LasMapEntry((-.5, .8), "of_1", "decide by range - MEDIUM"),
        LasMapEntry((), "puAPI", "catch all, legacy unit - LOW"),
    ]
percent_general = [
        LasMapEntry((-100, 100), "percent", "decide by range, verify - LOW"),
        LasMapEntry((-1, 1), "of_1", "decide by range, verify - LOW"),
        LasMapEntry((), "ppm", "catch all, ppm - LOW" ),
    ]

registry.add_las_map('-',    'MM'  , 'millimeter'              , "decided without mnemonic- MEDIUM")
registry.add_las_map('-',    'M'   , 'meter'                   , "decided without mnemonic- MEDIUM")
registry.add_las_map('-',    'CM'  , 'centimeter'              , "decided without mnemonic- MEDIUM")
registry.add_las_map('-',    'GAPI', 'gAPI'                    , "decided without mnemonic- MEDIUM")
registry.add_las_map('-',    'DEG_C', 'celsius'                    , "decided without mnemonic- MEDIUM")
registry.add_las_map('-',    'DEG_F', 'fahrenheit'                    , "decided without mnemonic- MEDIUM")
registry.add_las_map('-',    'COUNTS/S', 'cps'                    , "decided without mnemonic- MEDIUM")
registry.add_las_map('-',    'CPS', 'cps'                    , "decided without mnemonic- MEDIUM")
registry.add_las_map('DEPT', 'M'   , 'meter'                   , "HIGH")
registry.add_las_map('DEPT', 'FT'  , 'feet'                    , "HIGH")
registry.add_las_map('DEPT', 'F'  ,  'feet'                    , "HIGH")
registry.add_las_map('GR'  , 'GAPI', 'gAPI'                    , "HIGH")
registry.add_las_map('GR'  , '',     'gAPI'                    , "HIGH")
registry.add_las_map('CGR' , 'GAPI', 'gAPI'                    , "HIGH")
registry.add_las_map('CALI', 'CM'  , 'centimeter'              , "HIGH")
registry.add_las_map('CALI', 'IN'  , 'inch'                    , "HIGH")
registry.add_las_map('DRHO', 'G/C3', 'gram / centimeter ** 3'  , "HIGH")
registry.add_las_map('RHOB', 'G/C3', 'gram / centimeter ** 3'  , "HIGH")
registry.add_las_map('DT'  , 'US/F', 'microsecond / foot'      , "HIGH")
registry.add_las_map('ILD' , 'OHMM', 'ohm * meter'             , "HIGH")
registry.add_las_map('LLS' , 'OHMM', 'ohm * meter'             , "HIGH")
registry.add_las_map('ILM' , 'OHMM', 'ohm * meter'             , "HIGH")
registry.add_las_map('LLD' , 'OHMM', 'ohm * meter'             , "HIGH")
registry.add_las_map('SFL' , 'OHMM', 'ohm * meter'             , "HIGH")
registry.add_las_map('SGR' , 'GAPI', 'gAPI'                    , "HIGH")
registry.add_las_map('SP'  , 'MV'  , 'millivolt'               , "HIGH")
registry.add_las_map('MSFL', 'OHMM', 'ohm * meter'             , "HIGH")
registry.add_las_map('NPHI', 'PU'  , PU)
registry.add_las_map('NPHI', 'PU%' , 'pu'                      , "HIGH")
registry.add_las_map('PEF' , ''    , percent_general)
registry.add_las_map('POTA', ''    , percent_general)
registry.add_las_map('THOR', ''    , percent_general)
registry.add_las_map('URAN', ''    , percent_general)

# TODO: Beginning of a database, has to go online
# mnemonics, synonyms (resolve- matching in theme,
# matching in recipe, matching for unit determination)
# relationships between mnemonics? tolerances? tools?
# annotating reg files w/ corrections that the file doesn't support
# versioning, searching
# also want it to point to posts

desc_wo_num = re.compile(r'^(?:\s*\d+\s+)?(.*)$')
red_low = re.compile(r'<td>(.+)?(?:LOW|NONE)(.+)?</td>')
orange_medium = re.compile(r'<td>(.+)?MEDIUM(.+)?</td>')

def check_las(las, registry=registry, HTML_out=True, divid=""):
    def n0(s): # If None, convert to ""
        return "" if s is None else str(s)
    # using the warnings like this kind sucks
    # they do need to be surpressed becuase i'm building a better view into the warnings anyway
    # with this function, but that resolved = on 87 w/ 91 = on 91 is really weird.
    # hate this interface
    # it has to be pulled twice because we need internal info for checklas
    with warnings.catch_warnings():
        warnings.simplefilter("default")
        warnings.filterwarnings("error", category=MissingLasUnitWarning)
        d = chr(0X1e) # delimiter
        col_names = f"mnemonic{d}las unit{d}pozo mapping{d}confidence{d}parsed{d}description{d}min{d}med{d}max{d}#NaN"
        result = [col_names] if HTML_out else []
        for curve in las.curves:
            resolved = None
            pozo_match = None
            confidence = None
            parsed = None
            try:
                resolved = registry.resolve_las_unit(curve.mnemonic, curve.unit, curve.data)
                if resolved is not None:
                    pozo_match = resolved.unit
                    confidence = resolved.confidence
                parsed = registry.parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)
                if resolved is None: raise MissingLasUnitWarning("Parsed directly from LAS, probably wrong")
            except (pint.UndefinedUnitError, MissingRangeError, UnitException, MissingLasUnitWarning) as e:
                confidence = " - " + str(e) + " - NONE"
            find_desc = desc_wo_num.findall(curve.descr)
            desc = find_desc[0] if len(find_desc) > 0 else curve.descr
            [v_min, v_med, v_max] = [str(x) for x in np.nanquantile(curve.data, [0, .5, 1])]
            curve_data = dict(
                    mnemonic = curve.mnemonic,
                    las_unit = curve.unit,
                    pozo_match = pozo_match,
                    confidence = confidence,
                    parsed_unit = parsed,
                    desc = desc,
                    v_min = v_min,
                    v_med = v_med,
                    v_max = v_max,
                    n_nan = np.count_nonzero(np.isnan(curve.data)))
            if not HTML_out: result.append(curve_data)
            else: result.append(d.join([n0(x) for x in curve_data.values()]))
        if not HTML_out: return result
        try:
            post_result = "\n".join(result)
            output = pd.read_csv(StringIO(post_result), delimiter=d, na_filter=False).to_html()
            for match in red_low.finditer(output):
                current_match = match.group()
                colored = "<td style=\"color:red\">" + current_match[4:]
                output = output.replace(current_match, colored)
            for match in orange_medium.finditer(output):
                current_match = match.group()
                colored = "<td style=\"color:#B95000\">" + current_match[4:]
                output = output.replace(current_match, colored)
            display(HTML('<div id="'+divid+'">'+output+'</div>'))
        except Exception as e:
            display(str(e))
            display(HTML("<br>".join(result)))

# Just a shorcut to make the API nice
def parse_unit_from_curve(curve, registry=registry):
    try:
        return registry.parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)
    except Exception as e:
        warnings.warn(f"Couldn't parse unit: {e}", MissingLasUnitWarning)
        return None
