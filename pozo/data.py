import pint

import ood
import pozo.renderers as pzr
import pozo.themes as pzt
import pozo.units as pzu

class Data(ood.Observed, pzt.Themeable):

    def __init__(self, index, values, **kwargs): # Default Index?
        unit = kwargs.pop('unit', None)
        if len(index) != len(values):
            raise ValueError("Index and values have different length")
        self._mnemonic = kwargs.pop('mnemonic', None)
        if 'name' not in kwargs:
            if not self._mnemonic:
                raise ValueError("You must supply 'name'. Or 'mnemonic' will be used as 'name' if 'name' absent...")
            kwargs['name'] = self._mnemonic
        self.set_values(values, unit = unit, index=index)
        super().__init__(**kwargs) #od.ChildObserved sets name

    # In render, check unit
    def set_unit(self, unit):
        if unit is None: return
        if isinstance(unit, str):
            unit = pozo.ureg.parse_units(unit)
        self._unit = unit

    def get_unit(self):
        return self._unit


    def set_values(self, values, unit=None, index=None, index_unit=None):
        index_len = len(index) if index is not None else len(self._index)
        if index_len != len(values):
            raise ValueError("Index and values have different length.")
        self._values = values
        if unit is not None: self.set_unit(unit)
        elif isinstance(values, pint.Quantity):
            self.set_unit(values.unit)
        if index is not None:
            self.set_index(index)
            #if index_unit is not None: # TODO
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

