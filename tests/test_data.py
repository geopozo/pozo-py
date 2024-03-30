import pytest
import pozo.traces

index = [1, 2, 3, 4]
values = [0, 1, 1, 0]
index2 = [5, 6, 7, 8]
values2 = [2, 3, 4, 5]

d1 = pozo.traces.Trace(values, depth=index, mnemonic="md1")
d2 = pozo.traces.Trace(values, depth=index, mnemonic="d2")
d3 = pozo.traces.Trace(values, depth=index, name="d3")
d4 = pozo.traces.Trace(values, depth=index, mnemonic="md4")
d5 = pozo.traces.Trace(values, depth=index, mnemonic="md5")
d6 = pozo.traces.Trace(values, depth=index, mnemonic="md6")
d6 = pozo.traces.Trace(values, depth=index, mnemonic="md7")
d7 = pozo.traces.Trace(values, depth=index, mnemonic="md8")

def test_user_simulation():
    x = pozo.traces.Trace(values, depth=index, mnemonic="DHO")
    assert isinstance(x, pozo.traces.Trace)
    assert x.get_name() == "DHO"
    x.set_name("NAME")
    assert x.get_name() == "NAME"
    assert x.get_mnemonic() == "NAME"
    x.set_mnemonic("TEST")
    assert x.get_mnemonic() == "TEST"
    assert x.get_data() == values
    assert x.get_depth() == index
    x.set_data(values2)
    x.set_depth(index2)
    assert x.get_data() == values2
    assert x.get_depth() == index2
    # Error
    with pytest.raises(ValueError):
        y = pozo.traces.Trace(values, depth=index)
    with pytest.raises(ValueError):
        x.set_data([1])
    with pytest.raises(ValueError):
        x.set_depth([1])
    with pytest.raises(ValueError):
        x.set_data([1,2], depth=[1])

def test_user_simulation2():
    ## Init
    first = pozo.traces.Trace([2], depth=[1], name="test")
    assert isinstance(first, pozo.traces.Trace)
    assert first.get_data() == [2]
    assert first.get_depth() == [1]
    assert first.get_name() == "test"
    assert first.get_mnemonic() == "test"
    second = pozo.traces.Trace([2], depth=[1], name="test")
    assert isinstance(second, pozo.traces.Trace)
    assert second.get_data() == [2]
    assert second.get_depth() == [1]
    assert second.get_name() == "test"
    assert second.get_mnemonic() == "test"
    second.set_mnemonic("test2")
    assert second.get_mnemonic() == "test2"
    second.set_name("test3")
    assert second.get_name() == "test3"
    third = pozo.traces.Trace([2], depth=[1], mnemonic="test2")
    assert isinstance(third, pozo.traces.Trace)
    assert third.get_data() == [2]
    assert third.get_depth() == [1]
    assert third.get_name() == "test2"
    assert third.get_mnemonic() == "test2"
    with pytest.raises(Exception):
        pozo.traces.Trace([1], depth=[1,2], name="what")
    with pytest.raises(Exception):
        pozo.traces.Trace([1, 2], depth=[1,2])

