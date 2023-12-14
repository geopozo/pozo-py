import warnings
import ood
import pozo
import traceback




class Axis(ood.Item):
    _type = "axis"
    _child_type = "data"

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        for ar in args:
            self.add_data(ar)

    # add_items
    def add_data(self, *data, **kwargs): # axis can take data... and other axis?
        for datum in data:
            if not isinstance(datum, pozo.Data):
                raise TypeError("Axis.add_data() only accepts data")
        super().add_items(*data, **kwargs)

    # get_items
    def get_data(self, *selectors, **kwargs): # TODO get by name or by actual
        return super().get_items(*selectors, **kwargs)

    # get_item
    def get_datum(self, selector, **kwargs):
        return super().get_item(selector, **kwargs)

    # pop items
    def pop_data(self,  *selectors):
        return super().pop_items(*selectors)

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

