import pytest
import ood
import ood.exceptions as e
import pozo.data, pozo.axes

index = [1, 2, 3, 4]
values = [0, 1, 1, 0]
index2 = [5, 6, 7, 8]
values2 = [2, 3, 4, 5]

e.NameConflictException.default_level = e.ErrorLevel.IGNORE
e.MultiParentException.default_level = e.ErrorLevel.IGNORE

d1 = pozo.data.Data(values, depth=index, mnemonic="md1")
d2 = pozo.data.Data(values, depth=index, name="d2")
d3 = pozo.data.Data(values2, depth=index, name="d3", mnemonic="md3")
d4 = pozo.data.Data(values2, depth=index, mnemonic="md4")
d5 = pozo.data.Data(values, depth=index2, mnemonic="md5")
d6 = pozo.data.Data(values, depth=index2, mnemonic="md6")
d7 = pozo.data.Data(values2, depth=index2, mnemonic="md7")
d8 = pozo.data.Data(values2, depth=index2, mnemonic="md8")


def test_axis():
    a = pozo.axes.Axis()
    assert isinstance(a, pozo.axes.Axis)
    assert a.get_data() == []
    with pytest.raises(ValueError):
        assert a.get_datum(None)
    assert a.pop_data() == []
    b = pozo.axes.Axis(d1)
    assert len(b.get_data()) ==1
    assert len(b) == 1
    assert b.get_datum(d1.get_name()) == d1
    assert b.get_datum(d1) == d1
    assert b.get_datum(d2) == None
    assert b.get_datum("md1") == d1
    assert b.get_datum('astoasi') == None
    assert b.get_datum(5) == None
    c = pozo.axes.Axis(*[d1, d2])
    d = pozo.axes.Axis(*[d1, d2], d3)
    e = pozo.axes.Axis(*[d4, d5], d6)
    assert e._count_dictionary() == 3
    assert len(e.get_data()) == 3
    assert e._count_dictionary() == len(e.get_data())
    assert e.get_data() == [d4, d5, d6]
    assert e.get_datum(d4) == d4
    assert e.get_datum(d1) == None
    assert e.get_datum(d2) == None
    assert e.get_datum("md1") == None
    assert e.get_datum('astoasi') == None
    assert e.get_datum(5) == None
    assert e.get_datum("md4") == d4
    assert e.get_datum("md5") == d5
    assert e.get_datum("md6") == d6



    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_data())
    with pytest.warns(UserWarning):
        e.add_data(*[d5, d1]) # d1 new
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_data())
    assert len(e.get_data()) == 4
    with pytest.warns(UserWarning):
        e.add_data(d1, d8, *[d2, d4]) #d2 d8 new
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_data())
    assert len(e.get_data()) == 6
    with pytest.warns(UserWarning):
        e.add_data(*c.get_data(), *d.get_data(), *e.get_data())
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_data())
    assert len(e.get_data()) == 7
    assert len(e.get_data()) != 6
    e.add_data()
    with pytest.raises(TypeError):
        e.add_data(None)
        e.add_data("whatever")
    assert e.get_data("md6")[0] == d6
    assert e.get_data("md6")[0] == d6
    assert e.get_data("md6", "md7") == [d6]
    assert e.get_data(d6, d7) == [d6]
    assert e.get_data(d6) == [d6]
    n = len(e.get_data())
    assert e.pop_data(d6) == [d6]
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_data())
    assert n == len(e.get_data()) + 1
    # assert e.pop_data(d6) == [] # pop is by default strict now
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_data())
    #assert e.pop_data(d6, d6, d6) == [] #by default strict
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_data())
    e.pop_data(*e.get_data())
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_data())
    assert len(e.get_data()) == 0
    with pytest.warns(UserWarning):
        e.add_data(*[d1,d2],*[d3,d4],*[d1,d4])
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_data())
    assert len(e.get_data()) == 4
    assert e.get_data(*[d1, d2, d3, d4]) == [d1, d2, d3, d4]
    assert e.get_data(*[d1, d2],*[ d3, d4, d5]) == [d1, d2, d3, d4]
    assert e.get_data(*["md1", d2, d3, d4]) == [d1, d2, d3, d4]
    assert e.get_datum(d1) == d1
    assert e.get_datum("md1") == d1
    d1.set_name("test")
    assert e.get_datum("test") == d1
    assert e.get_datum("md1") == None
