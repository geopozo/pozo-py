import pytest
import pozo


index = [1, 2, 3, 4]
values = [0, 1, 1, 0]
index2 = [5, 6, 7, 8]
values2 = [2, 3, 4, 5]

def test_data_examples():
    d1 = pozo.Data(index, values, mnemonic="md1")
    d2 = pozo.Data(index, values, name="d2")
    d3 = pozo.Data(index, values, name="d3", mnemonic="md3")
    d4 = pozo.Data(index, values, mnemonic="md4")
    d5 = pozo.Data(index, values, mnemonic="md5")
    d6 = pozo.Data(index, values, mnemonic="md6")
    d6 = pozo.Data(index, values, mnemonic="md7")
    d7 = pozo.Data(index, values, mnemonic="md8")

def test_data():
    x = pozo.Data(index, values, mnemonic="DHO")
    assert isinstance(x, pozo.Data)
    assert x.get_name() == "DHO"
    x.set_name("NAME")
    assert x.get_name() == "NAME"
    assert x.get_mnemonic() == "DHO"
    x.set_mnemonic("TEST")
    assert x.get_mnemonic() == "TEST"
    assert x.get_values() == values
    assert x.get_index() == index
    x.set_values(values2)
    x.set_index(index2)
    assert x.get_values() == values2
    assert x.get_index() == index2
    # Error
    with pytest.raises(ValueError):
        y = pozo.Data(index, values)
    with pytest.raises(ValueError):
        x.set_values([1])
    with pytest.raises(ValueError):
        x.set_index([1])
    with pytest.raises(ValueError):
        x.set_index_values([1], [1,2])

        # check setting both name and mnemonic
        # check setting just name
        # check setting color
        # check sending in wrong types
        # check changing name works on integration

    axis = pozo.Axis()
    x = pozo.Data(index, values, mnemonic="mnemonic")
    assert len(x._axes_by_id) == 0
    x._register_axes(axis)
    assert len(x._axes_by_id) == 1
    assert x._axes_by_id[id(axis)] == axis
    x._deregister_axes(axis)
    assert len(x._axes_by_id) == 0
    # Chaos
    try:
        x.set_infex_values("hello", [1])
        x.set_values(x)
        pozo.Data(index, values, "2323", "203910", "0239")
        assert False
    except:
        assert True
