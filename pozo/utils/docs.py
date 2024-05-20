import abc
# doc() decorate allows us to use @doc(_("documentation")) so that we can use gettext with pydoc/docstrings
# it also gives a custom help() function since I don't like the structure of the built-in help()
def doc(docstring):
    def decorate(obj):
        obj.__doc__ = docstring
        if isinstance(obj, abc.ABCMeta):
            obj.help = classmethod(help_fn)
        else:
            obj.help = help_fn
        return obj
    return decorate

# help_fn can be assigned to any function or object to print its __doc__ attribute
def help_fn(self):
    print(self.__doc__)
