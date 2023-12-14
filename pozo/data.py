import ood

class Data(ood.Observed):
    def __init__(self, index, values, **kwargs): # Default Index?
        if len(index) != len(values):
            raise ValueError("Index and values have different length")
        self._mnemonic = kwargs.pop('mnemonic', None)
        if 'name' not in kwargs:
            if not self._mnemonic:
                raise ValueError("You must supply 'name'. Or 'mnemonic' will be used as 'name' if 'name' absent...")
            kwargs['name'] = self._mnemonic
        super().__init__(**kwargs) #od.ChildObserved sets name
        self._index = index
        self._values = values


    def set_values(self, values, index=None):
        index_len = len(self._index) if not index else len(index)
        if index_len != len(values):
            raise ValueError("Index and values have different length.")
        self._values = values
        if index: self.set_index(index)

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
