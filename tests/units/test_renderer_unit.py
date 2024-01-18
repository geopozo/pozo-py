import pytest
import pint
import pozo.data
import pozo.units as pzu
import pozo.renderers as pzr

def test_renderer():
    # Test Y Axis incompatibility
    data1 = pozo.Data(pzu.Q([1], "volts"), depth=pzu.Q([1], "meters"), name="voltage")
    data2 = pozo.Data(pzu.Q([2], "amperes"), depth=pzu.Q([2], "inches"), name="current")
    data_extra = pozo.Data([3], depth=[3], depth_unit="centimeters", name="extra")
    graph = pozo.Graph(data1, data2, data_extra)
    assert len(graph) == 3
    assert len(graph.all_data()) == 3

    renderer = pzr.Plotly()
    with pytest.raises(ValueError):
        renderer.get_layout(graph)

    # shouldn't have to do this
    # graph.get_track("current").get_axes()[0].pop_data()

    data3 = pozo.Data(pzu.Q([1], "volts"), depth=pzu.Q([1], "inches"), name="voltage2")
    data4 = pozo.Data(pzu.Q([2], "amperes"), depth=pzu.Q([1], "inches"), name="current2")
    graph2 = pozo.Graph(data3, data4)
    renderer.get_layout(graph2)

    # lets see if we can make the data homogenous
    for data in graph.all_data():
        data.convert_depth_unit("inches")
        if data.get_name() != "extra":
            assert isinstance(data.get_depth(), pint.Quantity)
        else:
            assert not isinstance(data.get_depth(), pint.Quantity)
            # TODO: there is a transformation here, list-->numpy

    renderer.get_layout(graph)
