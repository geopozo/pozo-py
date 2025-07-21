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
    ("DEPT", "M", "meter", 100, "Clear match."),
    ("DEPT", "FT", "feet", 100, "Clear match."),
    ("DEPT", "F", "feet", 100, "Clear match."),
    ("GR", "GAPI", "gAPI", 100, "Clear match."),
    ("GR", "", "gAPI", 100, "Clear match."),
    ("CGR", "GAPI", "gAPI", 100, "Clear match."),
    ("CALI", "CM", "centimeter", 100, "Clear match."),
    ("CALI", "IN", "inch", 100, "Clear match."),
    ("DRHO", "G/C3", "gram / centimeter ** 3", 100, "Clear match."),
    ("RHOB", "G/C3", "gram / centimeter ** 3", 100, "Clear match."),
    ("DT", "US/F", "microsecond / foot", 100, "Clear match."),
    ("ILD", "OHMM", "ohm * meter", 100, "Clear match."),
    ("LLS", "OHMM", "ohm * meter", 100, "Clear match."),
    ("ILM", "OHMM", "ohm * meter", 100, "Clear match."),
    ("LLD", "OHMM", "ohm * meter", 100, "Clear match."),
    ("SFL", "OHMM", "ohm * meter", 100, "Clear match."),
    ("SGR", "GAPI", "gAPI", 100, "Clear match."),
    ("SP", "MV", "millivolt", 100, "Clear match."),
    ("MSFL", "OHMM", "ohm * meter", 100, "Clear match."),
    ("NPHI", "PU", PU),
    ("NPHI", "PU%", "pu", 100, "Clear match."),
    ("PEF", "", percent_general),
    ("POTA", "", percent_general),
    ("THOR", "", percent_general),
    ("URAN", "", percent_general),
)


# agrega a las_map
def add_to_las_si_map(las_map: mapper.LasSiMap) -> None:
    """Add new units to las_si_map."""
    for unit_args in las_si_map:
        las_map.add(*unit_args)  # type: ignore

# es realmente necesario esto? no podemos ejecutar el bucle facilmente
# en __init__ y quitar una capa?
