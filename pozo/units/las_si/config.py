from pozo.units.las_si import mapper

PU = (
    mapper.RangeBoundaries((-50, 80), "pu", "decide by range - MEDIUM"),
    mapper.RangeBoundaries((-0.5, 0.8), "of_1", "decide by range - MEDIUM"),
    mapper.RangeBoundaries((), "puAPI", "catch all, legacy unit - LOW"),
)
percent_general = (
    mapper.RangeBoundaries((-100, 100), "percent", "decide by range, verify - LOW"),
    mapper.RangeBoundaries((-1, 1), "of_1", "decide by range, verify - LOW"),
    mapper.RangeBoundaries((), "ppm", "catch all, ppm - LOW"),
)


las_si_map = (  # mapa de las_si
    ("-", "MM", "millimeter", "decided without mnemonic- MEDIUM"),
    ("-", "M", "meter", "decided without mnemonic- MEDIUM"),
    ("-", "CM", "centimeter", "decided without mnemonic- MEDIUM"),
    ("-", "GAPI", "gAPI", "decided without mnemonic- MEDIUM"),
    ("-", "DEG_C", "celsius", "decided without mnemonic- MEDIUM"),
    ("-", "DEG_F", "fahrenheit", "decided without mnemonic- MEDIUM"),
    ("-", "COUNTS/S", "cps", "decided without mnemonic- MEDIUM"),
    ("-", "CPS", "cps", "decided without mnemonic- MEDIUM"),
    ("DEPT", "M", "meter", "HIGH"),
    ("DEPT", "FT", "feet", "HIGH"),
    ("DEPT", "F", "feet", "HIGH"),
    ("GR", "GAPI", "gAPI", "HIGH"),
    ("GR", "", "gAPI", "HIGH"),
    ("CGR", "GAPI", "gAPI", "HIGH"),
    ("CALI", "CM", "centimeter", "HIGH"),
    ("CALI", "IN", "inch", "HIGH"),
    ("DRHO", "G/C3", "gram / centimeter ** 3", "HIGH"),
    ("RHOB", "G/C3", "gram / centimeter ** 3", "HIGH"),
    ("DT", "US/F", "microsecond / foot", "HIGH"),
    ("ILD", "OHMM", "ohm * meter", "HIGH"),
    ("LLS", "OHMM", "ohm * meter", "HIGH"),
    ("ILM", "OHMM", "ohm * meter", "HIGH"),
    ("LLD", "OHMM", "ohm * meter", "HIGH"),
    ("SFL", "OHMM", "ohm * meter", "HIGH"),
    ("SGR", "GAPI", "gAPI", "HIGH"),
    ("SP", "MV", "millivolt", "HIGH"),
    ("MSFL", "OHMM", "ohm * meter", "HIGH"),
    ("NPHI", "PU", PU),
    ("NPHI", "PU%", "pu", "HIGH"),
    ("PEF", "", percent_general),
    ("POTA", "", percent_general),
    ("THOR", "", percent_general),
    ("URAN", "", percent_general),
)


# agrega a las_map
def add_to_las_si_map(las_map: mapper.LasSiMap) -> None:
    for unit_args in las_si_map:
        las_map.add(*unit_args)
