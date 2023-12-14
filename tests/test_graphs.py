import pozo.data, pozo.axes, pozo.tracks, pozo.graphs
import ood
import ood.exceptions as e


def test_init():
    me = pozo.graphs.Graph()

# test detectors for different graph types (test las after migration)
