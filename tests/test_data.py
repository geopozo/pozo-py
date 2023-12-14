import pytest
import pozo.data

index = [1, 2, 3, 4]
values = [0, 1, 1, 0]
index2 = [5, 6, 7, 8]
values2 = [2, 3, 4, 5]

d1 = pozo.data.Data(index, values, mnemonic="md1")
d2 = pozo.data.Data(index, values, name="d2")
d3 = pozo.data.Data(index, values, name="d3", mnemonic="md3")
d4 = pozo.data.Data(index, values, mnemonic="md4")
d5 = pozo.data.Data(index, values, mnemonic="md5")
d6 = pozo.data.Data(index, values, mnemonic="md6")
d6 = pozo.data.Data(index, values, mnemonic="md7")
d7 = pozo.data.Data(index, values, mnemonic="md8")

def test_user_simulation():
    x = pozo.data.Data(index, values, mnemonic="DHO")
    assert isinstance(x, pozo.data.Data)
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
        y = pozo.data.Data(index, values)
    with pytest.raises(ValueError):
        x.set_values([1])
    with pytest.raises(ValueError):
        x.set_index([1])
    with pytest.raises(ValueError):
        x.set_index([1], values=[1,2])

def test_user_simulation2():
    ## Init
    first = pozo.data.Data([1], [2], name="test", mnemonic="test2")
    assert isinstance(first, pozo.data.Data)
    assert first.get_values() == [2]
    assert first.get_index() == [1]
    assert first.get_name() == "test"
    assert first.get_mnemonic() == "test2"
    second = pozo.data.Data([1], [2], name="test")
    assert isinstance(second, pozo.data.Data)
    assert second.get_values() == [2]
    assert second.get_index() == [1]
    assert second.get_name() == "test"
    assert second.get_mnemonic() is None
    second.set_mnemonic("test2")
    assert second.get_mnemonic() == "test2"
    second.set_name("test3")
    assert second.get_name() == "test3"
    third = pozo.data.Data([1], [2], mnemonic="test2")
    assert isinstance(third, pozo.data.Data)
    assert third.get_values() == [2]
    assert third.get_index() == [1]
    assert third.get_name() == "test2"
    assert third.get_mnemonic() == "test2"
    with pytest.raises(Exception):
        pozo.data.Data([1,2], [1], name="what")
    with pytest.raises(Exception):
        pozo.data.Data([1,2], [1, 2])

