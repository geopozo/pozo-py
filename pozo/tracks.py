import warnings
import ood
import pozo
import pozo.renderers as pzr
import pozo.themes as pzt
import traceback

class Track(ood.Item, pzt.Themeable):
    _type="track"
    _child_type="axis"
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        for ar in args:
            self.add_axes(ar)

    def _check_types(self, *axes):
        accepted_types = (pozo.Axis, pozo.Data)
        raw_return = []
        for axis in axes:
            if isinstance(axis, (list)):
                raw_return.extend(self._check_types(*axis))
            elif not isinstance(axis, accepted_types):
                raise TypeError(f"Axis.add_axes() only accepts axes, and data: pozo objects, not {type(axis)}")
            elif isinstance(axis, pozo.Data):
                raw_return.append(pozo.Axis(axis, name=axis.get_name()))
            else:
                raw_return.append(axis)
        return raw_return

    # add_items
    def add_axes(self, *axes, **kwargs):
        good_axes = self._check_types(*axes)
        super().add_items(*good_axes, **kwargs)
        return good_axes

    # get_items
    def get_axes(self, *selectors, **kwargs):
        return super().get_items(*selectors, **kwargs)

    # get_item
    def get_axis(self, selector, **kwargs):
        return super().get_item(selector, **kwargs)

    # pop items
    def pop_axes(self,  *selectors, **kwargs):
        return super().pop_items(*selectors, **kwargs)

    # what about whitelabelling all the other stuff
    def has_axis(self, selector):
        return super().has_item(selector)

    def reorder_all_axes(self, order):
        super().reorder_all_items(order)

    def move_axes(self, *selectors, **kwargs):
        super().move_items(*selectors, **kwargs)

    def get_data(self, *selectors, **kwargs):
        ret_data = []
        for axis in self.get_axes():
            ret_data.extend(axis.get_data(*selectors, **kwargs))
        return ret_data

    def get_theme(self):
        context = { "type":"track",
                   "name": self._name,
                   }
        return self._get_theme(context=context)
