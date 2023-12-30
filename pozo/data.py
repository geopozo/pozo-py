import pint

import ood
import pozo.renderers as pzr
import pozo.themes as pzt
import pozo.units as pzu

class Data(ood.Observed, pzt.Themeable):
    def __init__(self, index, values, **kwargs): # Default Index?
        units = kwargs.pop('units', None)
        if len(index) != len(values):
            raise ValueError("Index and values have different length")
        self._mnemonic = kwargs.pop('mnemonic', None)
        if 'name' not in kwargs:
            if not self._mnemonic:
                raise ValueError("You must supply 'name'. Or 'mnemonic' will be used as 'name' if 'name' absent...")
            kwargs['name'] = self._mnemonic
        self.set_values(values, units = units, index=index)
        super().__init__(**kwargs) #od.ChildObserved sets name

        #are units being sent down propertly TODO
    def set_units(self, units): # TODO what do we do if units are not all same on axis # fail, ask user to put on separate axes
        if units is None: return
        if isinstance(units, str):
            units = pozo.ureg.parse_units(units)
        self._units = units
        self._values = pzu.Q(self._values)

    def get_units(self):
        return self._units


    def set_values(self, values, units=None, index=None, index_units=None):
        index_len = len(self._index) if not index else len(index)
        if index_len != len(values):
            raise ValueError("Index and values have different length.")
        self._values = values
        if units is not None: self._set_units(units)
        elif isinstance(values, pint.Quantity):
            self.set_units(values.units)
        if index is not None:
            self.set_index(index)
            #if index_units is not None: # TODO
            #refactor depth first

    def get_values(self):
        return self._values

    def set_index(self, index, values=None):
        values_len = len(self._values) if not values else len(values)
        if values_len != len(index):
            raise ValueError("Index and values have different length.")
        self._index = index
        if values: self.set_values(values)

    def get_index(self):
        return self._index

    def set_mnemonic(self, mnemonic):
        self._mnemonic = mnemonic
    def get_mnemonic(self):
        return self._mnemonic

    def get_named_tree(self):
        return  { "data" : {
            'name': self._name,
            'mnemonic': self._mnemonic,
            'length': len(self._values),
        } }
    def get_theme(self):
        context = { "type":"data",
                   "name": self._name,
                   "mnemonic": self._mnemonic,
                   }
        return self._get_theme(context=context)

