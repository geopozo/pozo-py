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

    # This is good because we should pop these
    # But its weird that we need this or subclasses
    # won't accept keywords (even if __new__ has the
    # right signature.
    def __init__(self, *args, **kwargs):
        level = kwargs.pop("level", None)
        kind = kwargs.pop("kind", "item")
        formatted_message = self.message.format(kind=kind)
        super().__init__(formatted_message, *args, **kwargs)

    def __new__(cls, *args, level=None, kind="item"):
        try:
            formatted_message = cls.message.format(kind=kind)
        except AttributeError:
            raise NotImplementedError("AdjustableException is a baseclass and must be inherited by a default class that specifies both default_level and message")
        if level is None:
            level = cls.default_level
        if level == ErrorLevel.IGNORE or not level:
            return None
        elif level == ErrorLevel.ERROR or level is True or hasattr(cls, "no_warn"): #No_warn not tested
            if hasattr(cls, "no_warn") and level == ErrorLevel.WARN:
                warnings.warn("This level is set to WARN but the situation is 'yes' or 'no', so warn means no.") # Not tested
            # is traceback caught raise or at declaration?
            return super().__new__(cls, formatted_message, *args)
        elif level == ErrorLevel.WARN:
            warnings.warn(formatted_message)
            return None
        return None

class StrictIndexException(AdjustableException):
    default_level = ErrorLevel.IGNORE
    message = "Invalid key or index."

class NameConflictException(AdjustableException):
    default_level = ErrorLevel.ERROR
    no_warn = True # Not tested
    message = "Can't add >1 {kind} with same name."

class MultiParentException(AdjustableException):
    default_level = ErrorLevel.ERROR
    no_warn = True # Not tested
    message = "{kind} can only have one parent."

class RedundantAddException(AdjustableException):
    default_level = ErrorLevel.WARN
    message = "Trying to add duplicate {kind}."
