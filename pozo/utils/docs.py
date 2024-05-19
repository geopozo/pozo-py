# doc() decorate allows us to use @doc(_("documentation")) so that we can use gettext with pydoc/docstrings
def doc(docstring):
    def decorate(obj):
        obj.__doc__ = docstring
        return obj
    return decorate


