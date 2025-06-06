from .units import LasUnitRegistry, RangeBoundaries


PU = [
    RangeBoundaries((-50, 80), "pu", "decide by range - MEDIUM"),
    RangeBoundaries((-0.5, 0.8), "of_1", "decide by range - MEDIUM"),
    RangeBoundaries((), "puAPI", "catch all, legacy unit - LOW"),
]
percent_general = [
    RangeBoundaries((-100, 100), "percent", "decide by range, verify - LOW"),
    RangeBoundaries((-1, 1), "of_1", "decide by range, verify - LOW"),
    RangeBoundaries((), "ppm", "catch all, ppm - LOW"),
]


def registry_defines(registry: LasUnitRegistry):
    registry.define("gamma_API_unit = [Gamma_Ray_Tool_Response]  = gAPI")
    registry.define("porosity_unit = percent = pu")
    registry.define("of_1 = 100 * percent = fraction")
    registry.define("legacy_api_porosity_unit = [Legacy_API_Porosity_Unit] = puAPI")


def registry_mapping(registry: LasUnitRegistry):
    registry.add_las_map("-", "MM", "millimeter", "decided without mnemonic- MEDIUM")
    registry.add_las_map("-", "M", "meter", "decided without mnemonic- MEDIUM")
    registry.add_las_map("-", "CM", "centimeter", "decided without mnemonic- MEDIUM")
    registry.add_las_map("-", "GAPI", "gAPI", "decided without mnemonic- MEDIUM")
    registry.add_las_map("-", "DEG_C", "celsius", "decided without mnemonic- MEDIUM")
    registry.add_las_map("-", "DEG_F", "fahrenheit", "decided without mnemonic- MEDIUM")
    registry.add_las_map("-", "COUNTS/S", "cps", "decided without mnemonic- MEDIUM")
    registry.add_las_map("-", "CPS", "cps", "decided without mnemonic- MEDIUM")
    registry.add_las_map("DEPT", "M", "meter", "HIGH")
    registry.add_las_map("DEPT", "FT", "feet", "HIGH")
    registry.add_las_map("DEPT", "F", "feet", "HIGH")
    registry.add_las_map("GR", "GAPI", "gAPI", "HIGH")
    registry.add_las_map("GR", "", "gAPI", "HIGH")
    registry.add_las_map("CGR", "GAPI", "gAPI", "HIGH")
    registry.add_las_map("CALI", "CM", "centimeter", "HIGH")
    registry.add_las_map("CALI", "IN", "inch", "HIGH")
    registry.add_las_map("DRHO", "G/C3", "gram / centimeter ** 3", "HIGH")
    registry.add_las_map("RHOB", "G/C3", "gram / centimeter ** 3", "HIGH")
    registry.add_las_map("DT", "US/F", "microsecond / foot", "HIGH")
    registry.add_las_map("ILD", "OHMM", "ohm * meter", "HIGH")
    registry.add_las_map("LLS", "OHMM", "ohm * meter", "HIGH")
    registry.add_las_map("ILM", "OHMM", "ohm * meter", "HIGH")
    registry.add_las_map("LLD", "OHMM", "ohm * meter", "HIGH")
    registry.add_las_map("SFL", "OHMM", "ohm * meter", "HIGH")
    registry.add_las_map("SGR", "GAPI", "gAPI", "HIGH")
    registry.add_las_map("SP", "MV", "millivolt", "HIGH")
    registry.add_las_map("MSFL", "OHMM", "ohm * meter", "HIGH")
    registry.add_las_map("NPHI", "PU", PU)
    registry.add_las_map("NPHI", "PU%", "pu", "HIGH")
    registry.add_las_map("PEF", "", percent_general)
    registry.add_las_map("POTA", "", percent_general)
    registry.add_las_map("THOR", "", percent_general)
    registry.add_las_map("URAN", "", percent_general)
