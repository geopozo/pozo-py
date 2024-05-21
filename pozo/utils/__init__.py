from .array import (
    is_array,
    is_close,
    is_scalar_number,
    hash_array,
    isfinite,
    isnan,
    linspace,
    append,
    count_nonzero,
    max,
    min,
    nanquantile,
    summarize_array,
)


# These are all utility functions
# Taken by the principal __ini__.py
def deLASio(mnemonic):
    return mnemonic.split(":", 1)[0] if ":" in mnemonic else mnemonic
