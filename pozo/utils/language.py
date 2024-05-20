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
