import ood
import pint
import numpy as np

from .utils.language import _, _d, es, en
# nothing in config_info yet, but this import also sets some globals in ood
from .utils.configuration import config_info
import pozo.utils.docs as docs
from .traces import Trace
from .axes import Axis
from .tracks import Track
from .graphs import Graph
from .annotations import Note

import pozo.themes as themes
import pozo.renderers as renderers
import pozo.units as units
import pozo.utils as utils

__all__ = [es, en, Trace, Axis, Track, Graph, Note, themes, renderers, units, utils, config_info]

# PozoWarning is jsut a UserWarning but we can detect if we raise it with isinstance
class PozoWarning(UserWarning):
    pass

__doc__ = _d("""package pozo: the visualization engine, pozo

Para cambiar a español: `pozo.es()`

https://github.com/geopozo/pozo-demo is a good learning template and quickstart.

***** Description:

pozo creates a tree structure to describe your graph:

───Graph─┬─Track───Axis─┬─Trace: "CALI"
         │              └─Trace: "CGR"
         ├─Track─┬─Axis─┬─Trace: "RHOB"
         │       │      ├─Trace: "NPHI"
         │       │      ├─Trace: "LLD"
         │       │      └─Trace: "LLS"
         │       └─Axis───Trace: "ARP"
         └─Track───Axis───Trace: "RPA"

***** Highlighted sub-Objects:

    Main Objects:
                pozo.Graph              - The main object.
                pozo.Trace              - What stores data point and line data.

    Highlighted Items:
                pozo.themes.cangrejo    - A basic theme to jump-start styling. e.g. `myGraph.set_theme("cangrejo")`
                pozo.units.check_las()  - Print basic data analysis and sanitizing on your las files.
""")

docs.decorate_package(__name__)

# TODO: all this will be moved out in Neyberson's commit before release

# deLASio extracts the actual mnemonic from the kinverity1/lasio suffixed mnemonic
def deLASio(mnemonic):
    return mnemonic.split(":", 1)[0] if ":" in mnemonic else mnemonic

# is_array checks to see that the input is some type of array, even if wrapped by pint.Quantity.
# becareful, it can return false positives if they have a __len__ attribute
def is_array(value):
    if isinstance(value, str): return False
    if isinstance(value, pint.Quantity):
        return is_array(value.magnitude)
    return hasattr(value, "__len__")


# is_scalar_number use the input data to verify if is a number data
# will migrate to utils folder
def is_scalar_number(value):
    number_types = (int, float,
                    np.float16, np.float32, np.float64,
                    np.int16, np.int32, np.int64)
    if isinstance(value, pint.Quantity):
        return is_scalar_number(value.magnitude)
    return isinstance(value, number_types)

# HasLog is a Selector which will recurse through all children of an object
# and look for those that have a certain mnemonic
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

# verify_array_len is a shortcut to make sure all input data is the same shape
def verify_array_len(constant, data):
    if is_array(constant) and len(constant) != len(data): return False
    return True

# str_to_HasLog will pre-process selectors: a string selector in ood normally causes a name lookup,
# but this transforms it to a HasLog selector object. If you wanted a name, you could do {'name':'whatever'}
def str_to_HasLog(argument):
    if isinstance(argument, (list, tuple)):
        ret = []
        for selector in argument:
                ret.append(str_to_HasLog(selector)) # can't support nested lists, that's okay
        return ret
    elif isinstance(argument, str):
        return HasLog(argument)
    elif isinstance(argument, dict) and 'name' in argument:
        return argument['name']
    return argument
