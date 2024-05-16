import numpy as np

# get_interval has one parameter, this return dictionary with info about
# start, stop, step, size and sample_rate_consistent from the depth intervals
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
            start, stop, sample_rate_consistent, 0.0001
        )
        step = stop - start
        if step == 0:
            step = 0.0001
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
    return interval

# isClose has 4 parameters, this return a boolean value that verify the cosistent
# from the depth data
def isClose(n_1, n_2, sample_rate_consistent, percent):
    diff_percent = (abs(n_2 - n_1) / ((n_2 + n_1) / 2)) * 100
    if diff_percent > percent or sample_rate_consistent is False:
        sample_rate_consistent = False
    else:
        sample_rate_consistent = True
    return sample_rate_consistent

# hash_depth has one parameter, this return a hash from the depth data
def hash_depth(depth):
    if isinstance(depth, np.ndarray):
        return hash(depth.tobytes())
    elif isinstance(depth, (list, tuple)):
        depth_array = np.array(depth)
        return hash(depth_array.tobytes())
    else:
        raise ValueError("You must use for depth a list, tuple or an numpy array")
