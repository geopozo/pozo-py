from .data import Data
from .axes import Axis
from .tracks import Track
from .graphs import Graph

import pozo.themes as themes
import pozo.renderers as renderers
import pozo.units as units
import ood

def deLASio(mnemonic):
    return mnemonic.split(":", 1)[0] if ":" in mnemonic else mnemonic

# Error on dimensionless
#


class HasLog(ood.selectors.Selector):
    def __init__(self, mnemonic, prefix=''):
        self.mnemonic = mnemonic
        self.prefix = prefix
    def _process(self, parent):
        ret_items = []
        for item in parent.get_items():
            if hasattr(item, 'get_mnemonic'):
                if item.get_mnemonic() == self.mnemonic:
                    ret_items.append(item)
                    break
            if isinstance(item, ood.Observer):
                if item.has_item(HasLog(self.mnemonic, prefix='-' + self.prefix)):
                    ret_items.append(item)
                    break
        return ret_items
