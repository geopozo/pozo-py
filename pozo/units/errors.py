class MissingLasUnitWarning(UserWarning):
    """Warning for unresolved LAS units."""

    pass


class UnitException(Exception):
    """Raised when unit parsing fails."""

    pass


class MissingRangeError(Exception):
    """Raised when no matching range is found for LAS data."""

    pass
