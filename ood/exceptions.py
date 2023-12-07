class SelectorError(IndexError, KeyError): # We wrap errors so we can detect if we sent them
    pass
class SelectorTypeError(TypeError): # We wrap errors so we can detect if we sent them
    pass
