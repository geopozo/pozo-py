import ood
import pint
import numpy as np

ood.exceptions.NameConflictException.default_level = ood.exceptions.ErrorLevel.IGNORE
ood.exceptions.MultiParentException.default_level = ood.exceptions.ErrorLevel.IGNORE
from .traces import Trace # noqa
from .axes import Axis # noqa
from .tracks import Track # noqa
from .graphs import Graph # noqa
from .annotations import Note # noqa

import pozo.themes as themes # noqa
import pozo.renderers as renderers # noqa
import pozo.units as units # noqa

def get_interval(depth):
    if not isinstance(depth, (list, tuple, np.ndarray)):
        raise ValueError("You must use for depth a list, tuple or an numpy array")

    starts = np.array([])
    stops = np.array([])
    steps = np.array([])
    size = np.array([])
    sample_rate_consistent = True
    for i in range(len(depth) - 1):
        if depth[i] == depth[-1]:
            break
        start = depth[i]
        stop = depth[i + 1]
        step, sample_rate_consistent = isClose(
            start, stop, sample_rate_consistent, 0.0001, 0.0001
        )
        if sample_rate_consistent is False:
            starts = np.append(starts, start)
            stops = np.append(stops, stop)
            steps = None
        else:
            starts = np.append(starts, start)
            stops = np.append(stops, stop)
            steps = np.append(steps, step)
        size = np.append(size, stop - step)
    interval = {"start": starts, "stop": stops, "step": steps, "size": size}
    interval["sample_rate_consistent"] = (
        False if sample_rate_consistent is False else True
    )
    if isinstance(depth, np.ndarray):
        depth_hash = hash(depth.tobytes())
    else:
        depth_array = np.array(depth)
        depth_hash = hash(depth_array.tobytes())
    return interval, depth_hash

def isClose(n_1, n_2, sample_rate_consistent, default, percent):
    diff_percent = (abs(n_2 - n_1) / ((n_2 + n_1) / 2)) * 100
    step = n_2 - n_1
    if diff_percent > percent or sample_rate_consistent is False:
        sample_rate_consistent = False
    else:
        sample_rate_consistent = True

    if step == 0:
        step = default
    return step, sample_rate_consistent
