from pozo.units.las_si import mapper

PU = (
    mapper.Range("of_1", (-0.5, 0.8), "decide by range - MEDIUM"),
    mapper.Range("pu", (-50, 80), "decide by range - MEDIUM"),
    mapper.Range("puAPI", (), "catch all, legacy unit - LOW"),
)
percent_general = (
    mapper.Range("of_1", (-1, 1), "decide by range, verify - LOW"),
    mapper.Range("percent", (-100, 100), "decide by range, verify - LOW"),
    mapper.Range("ppm", (), "catch all, ppm - LOW"),
)

# mapa de las_si
las_si_map = (
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
        las_map.add(*unit_args)  # type: ignore
