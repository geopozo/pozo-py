import ood
import pozo
import pozo.themes as pzt

class Track(ood.Item, pzt.Themeable):

    def set_name(self, name):
        return super().set_name(name)

    def get_name(self):
        return super().get_name()

    _type="track"
    _child_type="axis"
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.note_dict = {}
        self.note_list = []
        for ar in args:
            self.add_axes(ar)

    def _check_types(self, *axes):
        accepted_types = (pozo.Axis, pozo.Trace)
        raw_return = []
        for axis in axes:
            if isinstance(axis, (list)):
                raw_return.extend(self._check_types(*axis))
            elif not isinstance(axis, accepted_types):
                raise TypeError(f"Axis.add_axes() only accepts axes, and traces: pozo objects, not {type(axis)}")
            elif isinstance(axis, pozo.Trace):
                raw_return.append(pozo.Axis(axis, name=axis.get_name()))
            else:
                raw_return.append(axis)
        return raw_return

    def replace_axes(self, *axes, **kwargs):
       mnemonics = []
       for axis in axes:
           for trace in axis.get_traces():
               mnemonics.append(trace.get_mnemonic())
       self.pop_axes(*mnemonics, strict_index=False, exclude=kwargs.get('exclude', None))
       self.add_axes(*axes, **kwargs)

    # add_items
    def add_axes(self, *axes, **kwargs):
        good_axes = self._check_types(*axes)
        super().add_items(*good_axes, **kwargs)
        return good_axes

    # get_items
    def get_axes(self, *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        return super().get_items(*selectors, **kwargs)

    # get_item
    def get_axis(self, selector=0, **kwargs):
        selector = pozo.str_to_HasLog(selector)
        return super().get_item(selector, **kwargs)

    # pop items
    def pop_axes(self, *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        return super().pop_items(*selectors, **kwargs)

    # what about whitelabelling all the other stuff
    def has_axis(self, selector):
        selector = pozo.str_to_HasLog(selector)
        return super().has_item(selector)

    def reorder_all_axes(self, order):
        order = pozo.str_to_HasLog(order)
        super().reorder_all_items(order)

    def move_axes(self, *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        super().move_items(*selectors, **kwargs)

    def get_traces(self, *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        ret_traces = []
        for axis in self.get_axes():
            ret_traces.extend(axis.get_traces(*selectors, **kwargs))
        return ret_traces

    def get_trace(self, selector=0, **kwargs):
        ret = self.get_traces(selector, **kwargs)
        if len(ret) == 0: return None
        return ret[0]

    def get_theme(self):
        context = { "type":"track",
                   "name": self._name,
                   }
        return self._get_theme(context=context)
