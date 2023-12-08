import warnings
import pozo.ood.ordereddictionary as od
import pozo.axes, pozo.axes
import traceback

class Track(od.ObservingOrderedDictionary, od.ChildObserved):

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        for ar in args:
            self.add_axes(ar)

    # add_items
    def add_axes(self, *axes, **kwargs): # axis can take axes... and other axis?
        warn_off = kwargs.pop("warn_off", False)
        good_axes = []
        if len(axes) != len(set(axes)):
            axes = list(dict.fromkeys(x for x in axes).keys())
            if not warn_off: warnings.warn(f"Trying to add same axes twice or more, ignoring duplicated")
        for axis in axes:
            if not isinstance(axis, (pozo.axes.Axis, pozo.data.Data)):
                raise TypeError("Axis.add_axes() only accepts axes")
            elif self.has_axis(axis): #if if-elif reversed, user could, for example, pass None, has_axis is fine with that.
                if not warn_off: warnings.warn(f"Trying to add axes which is already present:  {axis.get_name()} {id(axis)}")
                continue
            if isinstance(axis, pozo.data.Data):
                good_axes.append(pozo.axes.Axis(axis, name=axis.get_name()))
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


