"""LAS unit to SI unit configuration file."""

from pozo.units.las_si import mapper

PU = (
    mapper.Range("of_1", (-0.5, 0.8), 50, "decide by range"),
    mapper.Range("pu", (-50, 80), 50, "decide by range"),
    mapper.Range("puAPI", (), 25, "catch all, legacy unit"),
)
percent_general = (
    mapper.Range("of_1", (-1, 1), 25, "decide by range, verify"),
    mapper.Range("percent", (-100, 100), 25, "decide by range, verify"),
    mapper.Range("ppm", (), 25, "catch all, ppm"),
)

# mapa de las_si
las_si_map = (
    ("-", "MM", "millimeter", 50, "decided without mnemonic"),
    ("-", "M", "meter", 50, "decided without mnemonic"),
    ("-", "CM", "centimeter", 50, "decided without mnemonic"),
    ("-", "GAPI", "gAPI", 50, "decided without mnemonic"),
    ("-", "DEG_C", "celsius", 50, "decided without mnemonic"),
    ("-", "DEG_F", "fahrenheit", 50, "decided without mnemonic"),
    ("-", "COUNTS/S", "cps", 50, "decided without mnemonic"),
    ("-", "CPS", "cps", 50, "decided without mnemonic"),
    ("DEPT", "M", "meter", 100, "HIGH"),
    ("DEPT", "FT", "feet", 100, "HIGH"),
    ("DEPT", "F", "feet", 100, "HIGH"),
    ("GR", "GAPI", "gAPI", 100, "HIGH"),
    ("GR", "", "gAPI", 100, "HIGH"),
    ("CGR", "GAPI", "gAPI", 100, "HIGH"),
    ("CALI", "CM", "centimeter", 100, "HIGH"),
    ("CALI", "IN", "inch", 100, "HIGH"),
    ("DRHO", "G/C3", "gram / centimeter ** 3", 100, "HIGH"),
    ("RHOB", "G/C3", "gram / centimeter ** 3", 100, "HIGH"),
    ("DT", "US/F", "microsecond / foot", 100, "HIGH"),
    ("ILD", "OHMM", "ohm * meter", 100, "HIGH"),
    ("LLS", "OHMM", "ohm * meter", 100, "HIGH"),
    ("ILM", "OHMM", "ohm * meter", 100, "HIGH"),
    ("LLD", "OHMM", "ohm * meter", 100, "HIGH"),
    ("SFL", "OHMM", "ohm * meter", 100, "HIGH"),
    ("SGR", "GAPI", "gAPI", 100, "HIGH"),
    ("SP", "MV", "millivolt", 100, "HIGH"),
    ("MSFL", "OHMM", "ohm * meter", 100, "HIGH"),
    ("NPHI", "PU", PU),
    ("NPHI", "PU%", "pu", 100, "HIGH"),
    ("PEF", "", percent_general),
    ("POTA", "", percent_general),
    ("THOR", "", percent_general),
    ("URAN", "", percent_general),
)


# agrega a las_map
def add_to_las_si_map(las_map: mapper.LasSiMap) -> None:
    for unit_args in las_si_map:
        las_map.add(*unit_args)  # type: ignore
