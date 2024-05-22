import abc
import sys
from functools import partial
from .language import _

indent = "    "

# generate_directory loops through an object and prints a one-line help for subobjects with .help()
def generate_directory(obj):
    directory = _("\n***** sub-Object Directory (all have .help()):\n\n") # run at calltime, no need for _d
    empty = True
    for subobj_name in dir(obj):
        subobj = getattr(obj, subobj_name)
        if hasattr(subobj, "help") and hasattr(subobj, "__doc__") and subobj.__doc__:
            empty = False
            # the str() forces it to render language before .partition
            directory += indent + str(subobj.__doc__).partition('\n')[0]
            if directory[-2:-1] != "\n": directory += "\n"
    if empty: return ""
    return directory


# doc() decorate allows us to use @doc(_d("documentation")) so that we can use gettext with pydoc/docstrings
# it also gives a custom help() function since I don't like the structure of the built-in help()
def doc(docstring):
    def decorate(obj):
        obj.__doc__ = docstring
        if isinstance(obj, abc.ABCMeta):
            obj.help = classmethod(help_fn)
        elif callable(obj):
            obj.help = partial(help_fn, obj)
        else:
            obj.help = help_fn
        return obj
    return decorate

# help_fn can be assigned to any function or object to print its __doc__ attribute
def help_fn(self):
    print(self.__doc__)
    if hasattr(self, "_help") and callable(self._help):
        self._help()
    print(generate_directory(self))

def decorate_package(string, fn=None):
    package = sys.modules[string]
    package.help = partial(help_fn, package)
