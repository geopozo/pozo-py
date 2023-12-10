from enum import Enum
import warnings

class SelectorError(IndexError, KeyError): # We wrap errors so we can detect if we sent them
    pass
class SelectorTypeError(TypeError): # We wrap errors so we can detect if we sent them
    pass
class NameConflictError(ValueError):
    pass

class ErrorLevel(Enum):
    IGNORE = 0 # if False
    ERROR = 1 # if True
    WARN = 2

class AdjustableException(Exception):
    def __init__(self, thing="item", *args, **kwargs):
        try:
            self.formatted_message = self.message.format(thing=thing)
        except AttributeError:
            raise NotImplementedError("AdjustableException is a baseclass and must be inherited by a default class that specifies both default_level and message")
        super().__init__(self.formatted_message, *args, **kwargs)

    def notify(self, level=None):
        if level is None:
            level = self.default_level
        if level == ErrorLevel.IGNORE or not level:
            pass
        elif level == ErrorLevel.ERROR or level is True or hasattr(self, "no_warn"): #No_warn not tested
            if hasattr(self, "no_warn"):
                warnings.warn("This level is set to WARN but the situation is 'yes' or 'no', so warn means no.") # Not tested
            raise self
        elif level == ErrorLevel.WARN:
            warnings.warn(self.formatted_message)

class StrictIndexException(AdjustableException): 
    default_level = ErrorLevel.IGNORE
    message = "Invalid key or index."

class NameConflictException(AdjustableException):
    default_level = ErrorLevel.ERROR
    no_warn = True # Not tested
    message = "Can't add >1 {thing} with same name."

class MultiParentException(AdjustableException):
    default_level = ErrorLevel.ERROR
    no_warn = True # Not tested
    message = "{thing} can only have one parent."

class RedundantAddException(AdjustableException):
    default_level = ErrorLevel.WARN
    message = "Trying to add duplicate {thing}."
