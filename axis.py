import warnings
import pozo.ood.ordereddictionary as od
import pozo.data
import traceback




class Axis(od.ObservingOrderedDictionary):

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        for ar in args:
            self.add_data(ar)

    # add_items
    def add_data(self, *data, **kwargs): # axis can take data... and other axis?
        warn_off = kwargs.pop("warn_off", False)
        good_data = []
        if len(data) != len(set(data)):
            data = list(dict.fromkeys(x for x in data).keys())
            if not warn_off: warnings.warn(f"Trying to add same data twice or more, ignoring duplicated")
        for datum in data:
            if not isinstance(datum, pozo.data.Data):
                raise TypeError("Axis.add_data() only accepts data")
            elif self.has_datum(datum): #if if-elif reversed, user could, for example, pass None, has_datum is fine with that.
                if not warn_off: warnings.warn(f"Trying to add data which is already present:  {datum.get_name()} {id(datum)}")
                continue
            good_data.append(datum)
        super().add_items(*good_data, **kwargs)

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
        for el in self.data:
            result.append(el.get_named_tree())
        return { "axis" : { self.name: result } }

