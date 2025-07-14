import pint

pint_map = (  # mapa de pint
    "gamma_API_unit = [Gamma_Ray_Tool_Response]  = gAPI",
    "porosity_unit = percent = pu",
    "of_1 = 100 * percent = fraction",
    "legacy_api_porosity_unit = [Legacy_API_Porosity_Unit] = puAPI",
)


# agrega a pint
def add_to_pint(registry: pint.registry.ApplicationRegistry) -> None:
    for definition in pint_map:
        registry.define(definition)
