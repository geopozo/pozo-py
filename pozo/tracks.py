import warnings
import ood
import pozo
import traceback

class Track(ood.Item):
    _type="track"
    _child_type="axis"
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        for ar in args:
            self.add_axes(ar)

    # add_items
    def add_axes(self, *axes, **kwargs): # axis can take axes... and other axis?
        good_axes = []
        for axis in axes:
            if not isinstance(axis, (pozo.Axis, pozo.Data)):
                raise TypeError("Axis.add_axes() only accepts axes, and data: pozo objects")
            if isinstance(axis, pozo.Data):
                good_axes.append(pozo.Axis(axis, name=axis.get_name()))
            else:
                good_axes.append(axis)
        super().add_items(*good_axes, **kwargs)

    # get_items
    def get_axes(self, *selectors, **kwargs): # TODO get by name or by actual
        return super().get_items(*selectors, **kwargs)

    # get_item
    def get_axis(self, selector, **kwargs):
        return super().get_item(selector, **kwargs)

    # pop items
    def pop_axes(self,  *selectors):
        return super().pop_items(*selectors)

    # what about whitelabelling all the other stuff
    def has_axis(self, selector):
        return super().has_item(selector)

    def reorder_all_axes(self, order):
        super().reorder_all_items(order)

    def move_axes(self, *selectors, **kwargs):
        super().move_items(*selectors, **kwargs)

    def get_named_tree(self):
        result = []
        for el in self.get_axes():
            result.append(el.get_named_tree())
        return { "axis" : { self.name: result } }


