from pozo.exceptions import SelectorTypeError
from collections import namedtuple

# This is a selector, just like my modifiers for axis above/below, just like my has_axis
_Key_I = namedtuple('Key_I', 'key index')
class Key_I(_Key_I):
    pass
    def check_type(self):
        return isinstance(self[0], str) and isinstance(self[1], int)
    def enforce_type(self):
        if not self.check_type(): raise SelectorTypeError("Supplied Key_I must be tuple of (str, int)")
