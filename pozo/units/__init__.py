from .units import *

registry = LasRegistry()
Q = registry.Quantity # Overriding the registry and all this is a little weird

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

registry.add_las_map('DEPT', 'M'   , 'meter'                   , "HIGH")
registry.add_las_map('GR'  , 'GAPI', 'gAPI'                    , "HIGH")
registry.add_las_map('CGR' , 'GAPI', 'gAPI'                    , "HIGH")
registry.add_las_map('CALI', 'CM'  , 'centimeter'              , "HIGH")
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
import re
desc_wo_num = re.compile(r'^(?:\s*\d+\s+)?(.*)$')

def check_las(las, registry=registry):
    def n0(s): # If None, convert to ""
        return "" if s is None else str(s)
    d = chr(0X1e) # delimiter
    result = [f"mnemonic{d}las unit{d}pozo mapping{d}confidence{d}parsed{d}description"]
    for curve in las.curves:
        resolved = None
        pozo_match = None
        confidence = None
        try:
            resolved = registry.resolve_las_unit(curve.mnemonic, curve.unit, curve.data)
            if resolved is not None:
                pozo_match = resolved.unit
                confidence = resolved.confidence
            parsed = registry.parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)
        except (pint.UndefinedUnitError, MissingRangeError) as e:
            confidence = " - " + str(e) + " - NONE"
        find_desc = desc_wo_num.findall(curve.descr)
        desc = find_desc[0] if len(find_desc) > 0 else curve.descr
        result.append(d.join([n0(x) for x in [pozo.deLASio(curve.mnemonic),
                                             curve.unit,
                                             pozo_match,
                                             confidence,
                                             parsed,
                                             desc]
                              ]))
    try:
        display(HTML(pd.read_csv(StringIO("\n".join(result)), delimiter=d, na_filter=False).to_html()))
    except Exception as e:
        display(str(e))
        display(HTML("<br>".join(result)))

# Just a shorcut to make the API nice
def parse_unit_from_curve(curve, registry=registry):
    return registry.parse_unit_from_context(curve.mnemonic, curve.unit, curve.data)
