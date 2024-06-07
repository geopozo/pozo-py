datatypes = ["np", "pl", "xr", "pd", "list", "tuple"]

def pytest_generate_tests(metafunc):
    if "datatype" in metafunc.fixturenames:
        metafunc.parametrize("datatype", datatypes)
