from abc import ABC, abstractmethod
from pozo.ood.exceptions import SelectorTypeError
import pozo.ood.ordereddictionary as od

class Selector(ABC):

    @abstractmethod # this won't always throw an error!
    def _process(self, ood):
        raise NotImplementedError("All classes that inherit Selector must implement process. If you're seeing this error, some selector you are using wasn't finished!")


class Name_I(Selector): # untested
    def __init__(self, name, index):
        self.name = name
        self.index = index
        self.enforce_self_type()

    def check_self_type(self):
        return isinstance(self.name, str) and isinstance(self.index, (int, slice))
    def enforce_self_type(self):
        if not self.check_self_type(): raise SelectorTypeError("Supplied Name_I must be tuple of (str, int)")

    def _process(self, ood):
        self.enforce_self_type()
        return ood._get_items_by_name(self.name, index = self.index)

class Has_Children(Selector): # untested
    def __init__(self, *sub_selectors):
        self.sub_selectors = sub_selectors
    def _process(self, ood):
        ret_items = []
        for item in ood.get_items():
            if isinstance(item, od.ObservingOrderedDictionary):
                for selector in self.sub_selectors:
                    if item.has_item(selector):
                        ret_items.append(item)
                        break
        return ret_items
