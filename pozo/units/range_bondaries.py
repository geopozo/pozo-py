class RangeBoundaries:
    def __init__(self, boundaries, unit, confidence):
        if not isinstance(boundaries, tuple) or len(boundaries) not in {0, 2}:
            raise TypeError(
                "boundaries should contain a tuple with (min, max) or () catch-all"
            )

        self.boundaries = boundaries
        self.unit = unit
        self.confidence = confidence

    def is_within_range(self, min_val, max_val):
        return len(self.boundaries) == 0 or (
            min_val > self.boundaries[0] and max_val < self.boundaries[1]
        )
