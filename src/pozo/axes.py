import ood
import pozo
import pozo.themes as pzt


class Axis(ood.Item, pzt.Themeable):

    def set_name(self, name):
        return super().set_name(name)

    def get_name(self):
        return super().get_name()

    _type = "axis"
    _child_type = "trace"

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        for ar in args:
            self.add_traces(ar)

    def _check_types(self, *traces):
        accepted_types = (pozo.Trace)
        raw_return = []
        for trace in traces:
            if isinstance(trace, list):
                raw_return.extend(self._check_types(*trace))
            elif not isinstance(trace, accepted_types):
                raise TypeError(f"Axis.add_traces() only accepts pozo.Trace, or a single list of pozo.Trace, not {type(trace)}")
            else:
                raw_return.append(trace)
        return raw_return

    def replace_traces(self, *traces, **kwargs):
       mnemonics = []
       for trace in traces:
           mnemonics.append(trace.get_mnemonic())
       self.pop_traces(*mnemonics, strict_index=False, exclude=kwargs.get('exclude', None))
       self.add_traces(*traces, **kwargs)

    # add_items
    def add_traces(self, *traces, **kwargs):
        good_traces = self._check_types(*traces)
        super().add_items(*good_traces, **kwargs)
        return good_traces

    # get_items
    def get_traces(self, *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        return super().get_items(*selectors, **kwargs)

    # get_item
    def get_trace(self, selector=0, **kwargs):
        selector = pozo.str_to_HasLog(selector)
        return super().get_item(selector, **kwargs)

    # pop items
    def pop_traces(self,  *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        return super().pop_items(*selectors, **kwargs)

    # what about whitelabelling all the other stuff
    def has_trace(self, selector):
        selector = pozo.str_to_HasLog(selector)
        return super().has_item(selector)

    def reorder_all_traces(self, order):
        order = pozo.str_to_HasLog(order)
        super().reorder_all_items(order)

    def move_traces(self, *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        super().move_items(*selectors, **kwargs)

    def get_named_tree(self):
        result = []
        for el in self.get_traces():
            result.append(el.get_named_tree())
        return { "axis" : { self.name: result } }

    def get_theme(self):
        mnemonics = []
        for d in self.get_traces():
            mnemonics.append(d.get_mnemonic())
        context = { "type":"axis",
                   "name": self._name,
                   "mnemonics": mnemonics,
                   }
        return self._get_theme(context=context)
