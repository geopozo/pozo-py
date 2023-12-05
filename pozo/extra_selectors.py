from pozo.exceptions import SelectorTypeError
from abc import ABC, abstractmethod

## Selectors use internal functions! They don't have to....


class Selector(ABC):

    @abstractmethod # this won't always throw an error!
    def process(self, ood):
        raise NotImplementedError("All classes that inherit Selector must implement process. If you're seeing this error, some selector you are using wasn't finished!")


class Name_I(Selector):
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.enforce_self_type()

    def check_self_type(self):
        return isinstance(self.name, str) and isinstance(self.index, (int, slice))
    def enforce_self_type(self):
        if not self.check_self_type(): raise SelectorTypeError("Supplied Name_I must be tuple of (str, int)")

    def process(self, ood, **kwargs):
        self.enforce_self_type()
        return ood.get_items(self.name, index = self.index, **kwargs)
