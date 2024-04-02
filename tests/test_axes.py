import pytest
import ood
import ood.exceptions as e
import pozo.traces, pozo.axes

index = [1, 2, 3, 4]
values = [0, 1, 1, 0]
index2 = [5, 6, 7, 8]
values2 = [2, 3, 4, 5]

e.NameConflictException.default_level = e.ErrorLevel.IGNORE
e.MultiParentException.default_level = e.ErrorLevel.IGNORE

d1 = pozo.traces.Trace(values, depth=index, mnemonic="md1")
d2 = pozo.traces.Trace(values, depth=index, mnemonic="d2")
d3 = pozo.traces.Trace(values2, depth=index, name="d3") # no maky sensy
d4 = pozo.traces.Trace(values2, depth=index, mnemonic="md4")
d5 = pozo.traces.Trace(values, depth=index2, mnemonic="md5")
d6 = pozo.traces.Trace(values, depth=index2, mnemonic="md6")
d7 = pozo.traces.Trace(values2, depth=index2, mnemonic="md7")
d8 = pozo.traces.Trace(values2, depth=index2, mnemonic="md8")


def test_axis():
    a = pozo.axes.Axis()
    assert isinstance(a, pozo.axes.Axis)
    assert a.get_traces() == []
    with pytest.raises(ValueError):
        assert a.get_trace(None)
    assert a.pop_traces() == []
    b = pozo.axes.Axis(d1)
    assert len(b.get_traces()) ==1
    assert len(b) == 1
    assert b.get_trace(d1.get_name()) == d1
    assert b.get_trace(d1) == d1
    assert b.get_trace(d2) == None
    assert b.get_trace("md1") == d1
    assert b.get_trace('astoasi') == None
    assert b.get_trace(5) == None
    c = pozo.axes.Axis(*[d1, d2])
    d = pozo.axes.Axis(*[d1, d2], d3)
    e = pozo.axes.Axis(*[d4, d5], d6)
    assert e._count_dictionary() == 3
    assert len(e.get_traces()) == 3
    assert e._count_dictionary() == len(e.get_traces())
    assert e.get_traces() == [d4, d5, d6]
    assert e.get_trace(d4) == d4
    assert e.get_trace(d1) == None
    assert e.get_trace(d2) == None
    assert e.get_trace("md1") == None
    assert e.get_trace('astoasi') == None
    assert e.get_trace(5) == None
    assert e.get_trace("md4") == d4
    assert e.get_trace("md5") == d5
    assert e.get_trace("md6") == d6



    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_traces())
    with pytest.warns(UserWarning):
        e.add_traces(*[d5, d1]) # d1 new
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_traces())
    assert len(e.get_traces()) == 4
    with pytest.warns(UserWarning):
        e.add_traces(d1, d8, *[d2, d4]) #d2 d8 new
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_traces())
    assert len(e.get_traces()) == 6
    with pytest.warns(UserWarning):
        e.add_traces(*c.get_traces(), *d.get_traces(), *e.get_traces())
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_traces())
    assert len(e.get_traces()) == 7
    assert len(e.get_traces()) != 6
    e.add_traces()
    with pytest.raises(TypeError):
        e.add_traces(None)
        e.add_traces("whatever")
    assert e.get_traces("md6")[0] == d6
    assert e.get_traces("md6")[0] == d6
    assert e.get_traces("md6", "md7") == [d6]
    assert e.get_traces(d6, d7) == [d6]
    assert e.get_traces(d6) == [d6]
    n = len(e.get_traces())
    assert e.pop_traces(d6) == [d6]
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_traces())
    assert n == len(e.get_traces()) + 1
    # assert e.pop_traces(d6) == [] # pop is by default strict now
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_traces())
    #assert e.pop_traces(d6, d6, d6) == [] #by default strict
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_traces())
    e.pop_traces(*e.get_traces())
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_traces())
    assert len(e.get_traces()) == 0
    with pytest.warns(UserWarning):
        e.add_traces(*[d1,d2],*[d3,d4],*[d1,d4])
    assert e._count_dictionary() == len(e)
    assert e._count_dictionary() == len(e.get_traces())
    assert len(e.get_traces()) == 4
    assert e.get_traces(*[d1, d2, d3, d4]) == [d1, d2, d3, d4]
    assert e.get_traces(*[d1, d2],*[ d3, d4, d5]) == [d1, d2, d3, d4]
    assert e.get_traces(*["md1", d2, d3, d4]) == [d1, d2, d3, d4]
    assert e.get_trace(d1) == d1
    assert e.get_trace("md1") == d1
    d1.set_name("test")
    #assert e.get_trace("test") == d1 # maybe this comes back after set_name set to equal set_mnemonic
    #assert e.get_trace("md1") == None
