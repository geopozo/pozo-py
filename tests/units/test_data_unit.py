import pytest
import pozo.traces
import pozo.units as pzu


def a_data(data=[1], depth=[1], unit=None, depth_unit=None):
    return pozo.traces.Trace(data, depth=depth, name="1", unit=unit, depth_unit=depth_unit)

def test_data_units():
    with pytest.raises(ValueError):
        pozo.traces.Trace([1], depth=None, name="!!!")
    meter = pzu.registry._ureg.meter
    a_meter = pzu.Q([1], "meter")

    assert meter == a_data(unit="meter").get_unit()
    assert meter == a_data(unit=meter).get_unit()
    assert None == a_data(unit=None).get_unit()# Proper constructor
    assert None == a_data(unit="meter").get_depth_unit()

    assert meter == a_data(data=a_meter).get_unit()
    test_data = a_data()
    test_data2 = a_data(data=a_meter)
    assert test_data2.get_unit() == meter
    test_data2.set_unit(None)
    assert test_data2.get_unit() == None
    assert test_data.get_unit() == None
    test_data.set_unit(meter)
    assert test_data.get_unit() == meter
    test_data.set_unit(None)
    assert test_data.get_unit() == None
    test_data.set_unit("meter")
    assert test_data.get_unit() == meter
    assert test_data.get_depth_unit() == None
    assert test_data2.get_depth_unit() == None
    assert test_data.get_data() == [1]
    assert test_data2.get_data() == a_meter

    assert meter == a_data(depth_unit="meter").get_depth_unit()
    assert meter == a_data(depth_unit=meter).get_depth_unit()
    assert None == a_data(depth_unit=None).get_depth_unit()# Proper constructor
    assert None == a_data(depth_unit="meter").get_unit()

    assert meter == a_data(depth=a_meter).get_depth_unit()
    test_data = a_data()
    test_data2 = a_data(depth=a_meter)
    assert test_data2.get_depth_unit() == meter
    test_data2.set_depth_unit(None)
    assert test_data2.get_depth_unit() == None
    assert test_data.get_depth_unit() == None
    test_data.set_depth_unit(meter)
    assert test_data.get_depth_unit() == meter
    test_data.set_depth_unit(None)
    assert test_data.get_depth_unit() == None
    test_data.set_depth_unit("meter")
    assert test_data.get_depth_unit() == meter
    assert test_data.get_unit() == None
    assert test_data2.get_unit() == None
    assert test_data.get_depth() == [1]
    assert test_data2.get_depth() == a_meter

# test rendered in other file
