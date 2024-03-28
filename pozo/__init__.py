import ood

ood.exceptions.NameConflictException.default_level = ood.exceptions.ErrorLevel.IGNORE
ood.exceptions.MultiParentException.default_level = ood.exceptions.ErrorLevel.IGNORE
from .traces import Trace # noqa
from .axes import Axis # noqa
from .tracks import Track # noqa
from .graphs import Graph # noqa

import pozo.themes as themes # noqa
import pozo.renderers as renderers # noqa
import pozo.units as units # noqa

def deLASio(mnemonic):
    return mnemonic.split(":", 1)[0] if ":" in mnemonic else mnemonic

# Error on dimensionless
#


class HasLog(ood.selectors.Selector):
    def __init__(self, mnemonic):
        self.mnemonic = mnemonic
    def _process(self, parent):
        ret_items = []
        for item in parent.get_items():
            if hasattr(item, 'get_mnemonic'):
                if item.get_mnemonic() == self.mnemonic:
                    ret_items.append(item)
                    break
            if isinstance(item, ood.Observer):
                if item.has_item(self):
                    ret_items.append(item)
                    break
        return ret_items
