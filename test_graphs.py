import pozo.data, pozo.axes, pozo.tracks, pozo.graphs
import pozo.ood.ordereddictionary as od
import pozo.ood.exceptions as e


def test_init():
    me = pozo.graphs.Graph()

# test detectors for different graph types (test las after migration)
