import pytest
import ood
import ood.selectors as s
import ood.exceptions as e
import pozo.data, pozo.axes, pozo.tracks

index = [1, 2, 3, 4]
values = [0, 1, 1, 0]
index2 = [5, 6, 7, 8]
values2 = [2, 3, 4, 5]

e.NameConflictException.default_level = e.ErrorLevel.IGNORE
e.MultiParentException.default_level = e.ErrorLevel.IGNORE

d1 = pozo.data.Data(index, values, mnemonic="md1")
d2 = pozo.data.Data(index, values, name="d2")
d3 = pozo.data.Data(index, values2, name="d3", mnemonic="md3")
d4 = pozo.data.Data(index, values2, mnemonic="md4")
d5 = pozo.data.Data(index2, values, mnemonic="md5")
d6 = pozo.data.Data(index2, values, mnemonic="md6")
d7 = pozo.data.Data(index2, values2, mnemonic="md7")
d8 = pozo.data.Data(index2, values2, mnemonic="md8")
a1 = pozo.axes.Axis()
a2 = pozo.axes.Axis()
a3 = pozo.axes.Axis(d8)
a4 = pozo.axes.Axis(name="I have a name")
a5 = pozo.axes.Axis()
a6 = pozo.axes.Axis()
a7 = pozo.axes.Axis()
a8 = pozo.axes.Axis()


def test_user_simulation():

    wdata = pozo.tracks.Track(d1, d2, d3, d4, d5, d6, d7, d8, a1, a2, a3, a4)
    assert wdata.get_axes(a1) == [a1]
    assert wdata.get_axes("unnamed") == [a1, a2, a3]
    assert wdata.get_axes(s.Has_Children(d1)) == wdata.get_axes("md1")
    assert wdata.get_axes(s.Has_Children(d8)) == [wdata.get_axis("md8"), wdata.get_axis(a3)]
    a = pozo.tracks.Track()
    assert isinstance(a, pozo.tracks.Track)
    assert a.get_axes() == []
    with pytest.raises(ValueError):
        a.get_axis(None)
    assert a.pop_axes() == []
    b = pozo.tracks.Track(a1)
    assert len(b.get_axes()) ==1
    assert len(b) == 1
    assert b.get_axis(a1.get_name()) == a1
    assert b.get_axis(a1) == a1
    assert b.get_axis(a2) == None
    assert b.get_axis('astoasi') == None
    assert b.get_axis(5) == None
    c = pozo.tracks.Track(*[a1, a2])
    d = pozo.tracks.Track(*[a1, a2], a3)
    e = pozo.tracks.Track(*[a4, a5], a6)
    assert e._count_dictionary() == 3
    assert len(e.get_axes()) == 3
    assert e._count_dictionary() == len(e.get_axes())
    assert e.get_axes() == [a4, a5, a6]
    assert e.get_axis(a4) == a4
    assert e.get_axis(a1) == None
    assert e.get_axis(a2) == None
    assert e.get_axis('astoasi') == None
    assert e.get_axis(5) == None

    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_axes())
    with pytest.warns(UserWarning):
        e.add_axes(*[a5, a1]) # a1 new
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_axes())
    assert len(e.get_axes()) == 4
    with pytest.warns(UserWarning):
        e.add_axes(a1, a8, *[a2, a4]) #a2 a8 new
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_axes())
    assert len(e.get_axes()) == 6
    with pytest.warns(UserWarning):
        e.add_axes(*c.get_axes(), *d.get_axes(), *e.get_axes())
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_axes())
    assert len(e.get_axes()) == 7
    assert len(e.get_axes()) != 6
    e.add_axes()
    with pytest.raises(TypeError):
        e.add_axes(None)
        e.add_axes("whatever")
    assert e.get_axes(a6, a7) == [a6]
    assert e.get_axes(a6) == [a6]
    n = len(e.get_axes())
    assert e.pop_axes(a6) == [a6]
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_axes())
    assert n == len(e.get_axes()) + 1
    #assert e.pop_axes(a6) == [] # by default strict
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_axes())
    #assert e.pop_axes(a6, a6, a6) == [] # by default strict
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_axes())
    e.pop_axes(*e.get_axes())
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_axes())
    assert len(e.get_axes()) == 0
    with pytest.warns(UserWarning):
        e.add_axes(*[a1,a2],*[a3,a4],*[a1,a4])
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_axes())
    assert len(e.get_axes()) == 4
    assert e.get_axes(*[a1, a2, a3, a4]) == [a1, a2, a3, a4]
    assert e.get_axes(*[a1, a2],*[ a3, a4, a5]) == [a1, a2, a3, a4]
    assert e.get_axis(a1) == a1
    a1.set_name("test")
    assert e.get_axis("test") == a1
