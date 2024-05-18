import gettext
from pathlib import Path

import ood
import pint
import numpy as np

# This has to be defined as this, if we assign gettext directly to _,
# then when we change what is assigned to _, packages that imported _
# will still point to gettext. `from import as` is probably a regular assignment
# operator under the hood and therefore _ becomes a new variable contain a copy of the
# gettext.gettext reference. But this way _ is returning the variable (current_translator)
# that we control
# All of this can be moved into utilities eventually, remove no qa
current_translator = gettext.gettext
def _(string):
    global current_translator
    return current_translator(string)

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

locale_dir = Path(__file__).resolve().parents[0] / "locale"
es_translations = gettext.translation('pozo', localedir=locale_dir, languages=['es'])
en_translations = gettext.translation('pozo', localedir=locale_dir, languages=['en'])

# es() is a shortcut to set the language to spanish
def es(t = es_translations):
    global current_translator
    current_translator = t.gettext

# en is a shortcut to set the language to english
def en(t = en_translations):
    global current_translator
    current_translator = t.gettext

# doc() decorate allows us to use @doc(_("documentation")) so that we can use gettext with pydoc/docstrings
def doc(docstring):
    def decorate(obj):
        obj.__doc__ = docstring
        return obj
    return decorate

# PozoWarning is jsut a UserWarning but we can detect if we raise it with isinstance
class PozoWarning(UserWarning):
    pass

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
def is_scalar_number(value):
    number_types = (int, float,
                    np.float16, np.float32, np.float64,
                    np.int16, np.int32, np.int64)
    if isinstance(value, pint.Quantity):
        return is_scalar_number(value.magnitude)
    return isinstance(value, number_types)

# HasLog is a selector which will traverse through all children every generation of an object
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
