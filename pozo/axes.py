import warnings
import ood
import pozo
import pozo.renderers as pzr
import pozo.themes as pzt
import traceback


class Axis(ood.Item, pzt.Themeable):
    _type = "axis"
    _child_type = "data"

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        for ar in args:
            self.add_data(ar)

    # add_items
    def add_data(self, *data, **kwargs):
        accepted_types = (pozo.Data)
        good_data = []
        for datum in data:
            if isinstance(datum, list) and all(isinstance(item, accepted_types) for item in datum):
                good_data.extend(datum)
            elif not isinstance(datum, accepted_types):
                raise TypeError("Axis.add_data() only accepts pozo.Data, or a single list of pozo.Data")
            else:
                good_data.append(datum)
        super().add_items(*good_data, **kwargs)
        return good_data

    # get_items
    def get_data(self, *selectors, **kwargs):
        return super().get_items(*selectors, **kwargs)

    # get_item
    def get_datum(self, selector, **kwargs):
        return super().get_item(selector, **kwargs)

    # pop items
    def pop_data(self,  *selectors, **kwargs):
        return super().pop_items(*selectors, **kwargs)

    # what about whitelabelling all the other stuff
    def has_datum(self, selector):
        return super().has_item(selector)

    def reorder_all_data(self, order):
        super().reorder_all_items(order)

    def move_data(self, *selectors, **kwargs):
        super().move_items(*selectors, **kwargs)

    def get_named_tree(self):
        result = []
        for el in self.get_data():
            result.append(el.get_named_tree())
        return { "axis" : { self.name: result } }

    def get_theme(self):
        mnemonics = []
        for d in self.get_data():
            mnemonics.append(d.get_mnemonic())
        context = { "type":"axis",
                   "name": self._name,
                   "mnemonics": mnemonics,
                   }
        return self._get_theme(context=context)
