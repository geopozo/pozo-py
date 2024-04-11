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

class PozoWarning(UserWarning):
    pass

# These are all utility functions
def deLASio(mnemonic):
    return mnemonic.split(":", 1)[0] if ":" in mnemonic else mnemonic

# is_array use the input data to verify if is pint data or other type that has
# __len__ and return a boolean. Be careful with this, it will return true for Pozo objects.
def is_array(value):
    if isinstance(value, str): return False
    if isinstance(value, pint.Quantity):
        return is_array(value.magnitude)
    return hasattr(value, "__len__")


# is_scalar_number use the input data to verify if is a number data
def is_scalar_number(value):
    number_types = (int, float,
                    np.float16, np.float32, np.float64,
                    np.int16, np.int32, np.int64)
    if isinstance(value, pint.Quantity):
        return is_scalar_number(value.magnitude)
    return isinstance(value, number_types)

class HasLog(ood.selectors.Selector):
    def __init__(self, mnemonic):
        self.mnemonic = mnemonic
    def _process(self, parent):
        ret_items = []
        for item in parent.get_items():
            if hasattr(item, 'get_mnemonic'):
                if item.get_mnemonic() == self.mnemonic:
                    ret_items.append(item)
            if isinstance(item, ood.Observer):
                if item.has_item(self):
                    ret_items.append(item)
        return ret_items
    def __repr__(self):
        return f"HasLog({self.mnemonic})"

# verify_array_len use three inputs to verify the lenght in the data
def verify_array_len(constant, data):
    if is_array(constant) and len(constant) != len(data): return False
    return True

def str_to_HasLog(argument):
    if isinstance(argument, (list, tuple)):
        ret = []
        for selector in argument:
                ret.append(str_to_HasLog(selector))
        return ret
    elif isinstance(argument, str):
        return HasLog(argument)
    elif isinstance(argument, dict) and 'name' in argument:
        return argument['name']
    return argument
