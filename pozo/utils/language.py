import gettext
from pathlib import Path

# why the complexity?
# passing a function that changes a global allows us to use the same variable in all files/submodules
# otherwise submodules create their own variable when we try to import this one, and copy a reference to gettext into it,
# which we then can't change globally by changing our original variable because they made their own

current_translator = gettext.gettext
def _(string):
    global current_translator
    return current_translator(string)

# _d class is like _, except it makes sure it calls _ when the variable is accessed, not when it is assigned.
# this is useful since docs are generated at import time, but we may want to allow language to change at runtime
class _d(str):
    def __init__(self, string):
        self.gettext_key = string

    def __str__(self):
        return _(self.gettext_key)

    def __repr__(self):
        return _(self.gettext_key)

    def __eq__(self, lvalue):
        return lvalue == self.gettext_key

    def __json__(self):
        return _(self.gettext_key)



locale_dir = Path(__file__).resolve().parents[1] / "locale"
es_translations = gettext.translation('pozo', localedir=locale_dir, languages=['es'])
en_translations = gettext.translation('pozo', localedir=locale_dir, languages=['en'])

# es() is a shortcut to set the language to spanish
def es(t = es_translations):
    global current_translator
    current_translator = t.gettext

# en is a shortcut to set the language to english
def en(t = en_translations):
    global current_translator
    current_translator = t.gettext
