# initialize axis in different formats
import pytest
import pozo

index = [1, 2, 3, 4]
values = [0, 1, 1, 0]
index2 = [5, 6, 7, 8]
values2 = [2, 3, 4, 5]

d1 = pozo.Data(index, values, mnemonic="md1")
d2 = pozo.Data(index, values, name="d2")
d3 = pozo.Data(index, values2, name="d3", mnemonic="md3")
d4 = pozo.Data(index, values2, mnemonic="md4")
d5 = pozo.Data(index2, values, mnemonic="md5")
d6 = pozo.Data(index2, values, mnemonic="md6")
d7 = pozo.Data(index2, values2, mnemonic="md7")
d8 = pozo.Data(index2, values2, mnemonic="md8")

def test_axis():
    a = pozo.Axis()
    assert isinstance(a, pozo.Axis)
    assert a.get_data() == []
    assert a.get_datum(None) == None
    assert a.remove_data() == []
    b = pozo.Axis(d1)
    assert len(b._data) == 1
    assert len(b._data_ordered) == 1
    assert len(b._data_by_id) == 1
    assert len(b.get_data()) ==1
    assert b.get_datum() == d1
    assert b.get_datum(d1) == d1
    assert b.get_datum(d2) == None
    assert b.get_datum("md1") == d1
    assert b.get_datum('astoasi') == None
    assert b.get_datum(5) == None
    c = pozo.Axis([d1, d2])
    d = pozo.Axis([d1, d2], d3)
    e = pozo.Axis([d4, d5], d6)
    assert e._len_dict() == 3
    assert len(e._data_ordered) == 3
    assert len(e._data_by_id) == 3
    assert len(e.get_data()) == 3
    assert e._len_dict() == len(e._data_ordered)
    assert e._len_dict() == len(e._data_by_id)
    assert e._len_dict() == len(e.get_data())
    assert e.get_data() == [d4, d5, d6]
    assert e.get_datum() == d4
    assert e.get_datum(d1) == None
    assert e.get_datum(d2) == None
    assert e.get_datum("md1") == None
    assert e.get_datum('astoasi') == None
    assert e.get_datum(5) == None
    assert e.get_datum("md4") == d4
    assert e.get_datum("md5") == d5
    assert e.get_datum("md6") == d6



    assert e._len_dict() == len(e._data_ordered)
    assert e._len_dict() == len(e._data_by_id)
    assert e._len_dict() == len(e.get_data())
    with pytest.warns(UserWarning):
        e.add_data([d5, d1]) # d1 new
    assert e._len_dict() == len(e._data_ordered)
    assert e._len_dict() == len(e._data_by_id)
    assert e._len_dict() == len(e.get_data())
    assert len(e.get_data()) == 4
    with pytest.warns(UserWarning):
        e.add_data(d1, d8, [d2, d4]) #d2 d8 new
    assert e._len_dict() == len(e._data_ordered)
    assert e._len_dict() == len(e._data_by_id)
    assert e._len_dict() == len(e.get_data())
    assert len(e.get_data()) == 6
    with pytest.warns(UserWarning):
        e.add_data(c, d, e)
    assert e._len_dict() == len(e._data_ordered)
    assert e._len_dict() == len(e._data_by_id)
    assert e._len_dict() == len(e.get_data())
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
    assert e.get_data(d6, d7, ignore_orphans=False) == [d6, d7]
    n = len(e.get_data())
    assert e.remove_data(d6) == [d6]
    assert e._len_dict() == len(e._data_ordered)
    assert e._len_dict() == len(e._data_by_id)
    assert e._len_dict() == len(e.get_data())
    assert n == len(e.get_data()) + 1
    assert e.remove_data(d6) == []
    assert e._len_dict() == len(e._data_ordered)
    assert e._len_dict() == len(e._data_by_id)
    assert e._len_dict() == len(e.get_data())
    assert e.remove_data(d6, d6, d6) == []
    assert e._len_dict() == len(e._data_ordered)
    assert e._len_dict() == len(e._data_by_id)
    assert e._len_dict() == len(e.get_data())
    e.remove_data(e.get_data())
    assert e._len_dict() == len(e._data_ordered)
    assert e._len_dict() == len(e._data_by_id)
    assert e._len_dict() == len(e.get_data())
    assert len(e.get_data()) == 0
    with pytest.warns(UserWarning):
        e.add_data([d1,d2],[d3,d4],[d1,d4])
    assert e._len_dict() == len(e._data_ordered)
    assert e._len_dict() == len(e._data_by_id)
    assert e._len_dict() == len(e.get_data())
    assert len(e.get_data()) == 4
    assert e.get_data([d1, d2, d3, d4]) == [d1, d2, d3, d4]
    assert e.get_data([d1, d2],[ d3, d4, d5]) == [d1, d2, d3, d4]
    assert e.get_data(["md1", d2, d3, d4]) == [d1, d2, d3, d4]
    assert e.get_data([d1, d2, d3], ["md4"], _cap=2) == [d1, d2]
    assert e.get_datum(d1) == d1
    assert e.get_datum("md1") == d1
    d1.set_name("test")
    assert e.get_datum("test") == d1
    assert e.get_datum("md1") == None
## todo: not reallly testing situations of multiple axes
