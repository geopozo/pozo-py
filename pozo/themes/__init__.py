import copy
import colour
import json

import pozo.themes.mnemonic_tables as tables
from pozo.utils.language import _d, _
import pozo.utils.docs as docs

# ThemeValues will get english description, it just serves as the checker to see if a theme value is allowed
ThemeValues = dict(
               color=_d("Can be a single color value or list of color values from colour package"),
               track_width=_d("A number in pixels"),
               force=_d("If true, will force show the item even if it has no children"),
               hidden=_d("If true, will not show the item"),
               range=_d("Set's the default min and max x value for this item"),
               range_unit=_d("Specifies the units of range"),
               scale=_d("Can be log or linear"),
               fill=_d("a plotly fill description EXPERIMENTAL"),
               fillcolor=_d("color of the fill EXPERIMENTAL"),
               cross_axis_fill=_d("a fill between two separate axes EXPERIMENTAL")
               )

__doc__ = _d("""package theme: a theme engine for pozo

    The theme package provides several theme objects, which can be attached to pozo graphs, tracks, axes, and traces (.set_theme()) to provide information about styling during rendering. Regular dictionaries can be theme objects, and their possible keys are described here. Other theme objects are described in their own documentation.

""")

def _help():
    return _("Possible theme keys:\n") + json.dumps(ThemeValues, indent=4)

docs.decorate_package(__name__)

class Theme(): # Meant to be inherited
    def __init__(self, *args, **kwargs):
        self._context = {}
        super().__init__(*args, **kwargs)

    def set_context(self, data):
        if data is None: data = {}
        if not isinstance(data, dict):
            raise TypeError("Cannot assing context which is not a dict (or None)")
        self._context = data

    def get_context(self):
        return self._context

    def resolve(self, key, contexts):
            raise NotImplementedError("Every Theme inheriter must supply a resolve(self, key, context)")

class ThemeDict(Theme, dict): # Basically a dict
    def __init__(self, *args, **kwargs):
        for arg in args:
            if isinstance(arg, dict):
                for key in arg.keys():
                    if key not in ThemeValues:
                        raise KeyError(f"{key} is not a valid key. See pozo.themes.help()")
            else:
                raise ValueError("Can only pass dictionary like in pozo.themes.help() to constructor")
        super().__init__(*args, **kwargs)


    def update(self, *args, **kwargs):
        for arg in args:
            for key in arg.keys():
                if key not in ThemeValues:
                    raise KeyError(f"{key} is not a valid key. See pozo.themes.help()")
        super().update(*args, **kwargs)

    def __setitem__(self, k, v):
        if k not in ThemeValues:
            raise KeyError(f"{k} is not a valid key. See pozo.themes.help()")
        super().__setitem__(k, v)

    def deepcopy(self):
        return copy.deepcopy(self)

    def __repr__(self):
        return str(json.dumps(self, indent=2))

    def resolve(self, key, contexts=None):
        if key not in self:
            return None
        return self[key]

class DynamicTheme(Theme): # Meant to be inherited
    def resolve(self, key, contexts):
        raise NotImplementedError("Dynamic themes must implement get_value(self, key, args)")

# Themeable is meant to be an abstract class. Therefor it doesn't have a public doc.
class Themeable():
    def __init__(self, *args, **kwargs):
        self.set_theme(kwargs.pop("theme", {}))
        super().__init__(*args, **kwargs)
    @docs.doc(_d("""method set_theme sets the theme of object

Args:
    theme (Theme or dict): The theme you'd like to set"""))
    def set_theme(self, theme):
        if isinstance(theme, str):
            if theme not in themes:
                raise ValueError(f"{theme} is not a built-in theme, options are: {', '.join(list(themes.keys()))}")
            theme = themes[theme]
        if isinstance(theme, dict) and not isinstance(theme, ThemeDict):
            self._theme = ThemeDict(theme)
        elif isinstance(theme, Theme):
            self._theme = theme
        elif theme is None:
            self._theme = ThemeDict({})
        else:
            raise TypeError(f"Theme was not a dict, ThemeDict, or DynamicTheme, was {type(theme)}")

    def _get_theme(self, context={}):
        self._theme.set_context(context)
        return self._theme

    # You may override this
    @docs.doc(_d("""method get_theme returns a context-less theme definition

Returns:
    A theme, no context attached"""))
    def get_theme(self):
        return self._get_theme()

# Above are inheritables
from pozo.themes.theme_tools import * # should it be relative?
# Below is implementations
themes = {'cangrejo': MnemonicDictionary(tables.cangrejo)}
cangrejo = MnemonicDictionary(tables.cangrejo)

# ThemeList also has a theme, which is considered an override!
class ThemeStack(Themeable):
    def __init__(self, *args, **kwargs):
        local_default_theme = kwargs.pop("default", default_theme)
        self._contexts_vertical = [] # parallel con _list
        self._list = [local_default_theme] if local_default_theme else [] # the themes
        self._shadow_objects = {} # if themes have things that are initialized when they're added
        for arg in args:
            self.append(arg)
        super().__init__(*[], **kwargs)

    def append(self, theme):
        if isinstance(theme, Theme):
            self._list.append(theme)
            self._contexts_vertical.append(theme.get_context()) # but why not just traverse this at get time
        else:
            raise TypeError(f"Found a theme which isn't any type of valid theme: {type(theme)} {theme}")

    def pop(self, index = -1):
        self._contexts_vertical.pop(index)
        return self._list.pop(index)

    def __contains__(self, key):
        try:
            self.__getitem__(key)
        except KeyError:
            return False
        return True

    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError(f"Key must be string, not {type(key)} | value:{key}")
        # print(f'\ngetitem() Trying to get theme: {key}')

        contexts_horizontal = []
        eventual_value = self.get_theme() # Self-theme, override
        eventual_value = self._check_shortcut(eventual_value, key, contexts_horizontal) # something that translates to themelike
        # print(f'Override: {eventual_value}')
        while True: # do-while loop using break
            contexts_horizontal.append(eventual_value.get_context())
            eventual_value = eventual_value.resolve(key, self._contexts_vertical)
            # print(f'Override resolved to: {eventual_value}')
            eventual_value = self._check_shortcut(eventual_value, key, contexts_horizontal) # something that translates to themelike
            # print(f'Above shortcutted to: {eventual_value}')
            if not isinstance(eventual_value, Theme):
                break
        if eventual_value is None:
            contexts_horizontal.clear()
            for eventual_value in reversed(self._list):
                # print(f'Value from list of length {len(self._list)}: {eventual_value}')
                while True:# do-while loop using break
                    contexts_horizontal.append(eventual_value.get_context())
                    eventual_value = eventual_value.resolve(key, self._contexts_vertical)
                    # print(f'Override resolved to: {eventual_value}')
                    eventual_value = self._check_shortcut(eventual_value, key, contexts_horizontal)
                    # print(f'Above shortcutted to: {eventual_value}')
                    if not isinstance(eventual_value, Theme):
                        break
                if eventual_value is not None:
                   break
        # print(f'Final result: {eventual_value}')
        return self._process_output(eventual_value, key)

    # Take not-themes and return themes. Can't take a regular dict, which is sorta problematic.
    def _check_shortcut(self, value, key, contexts):
        context = contexts[-1] if len(contexts) else []
        if value is None:
            return None
        may_be_key = (id(value), id(context))
        if may_be_key in self._shadow_objects:
            return self._shadow_objects[may_be_key]
        elif key == "color" and isinstance(value, list):
            value = ColorWheel(value, context=context)
        elif key == "place_holder" and isinstance(value, "placeholder"): # never happen, put other shortcuts here
            value = "place_holder"
        else:
            return value # just send back what we got, do nothing
        self._shadow_objects[may_be_key] = value
        return value

    def _process_output(self, value, key):
        if value is None:
            raise KeyError(f"{key} does not exist in this theme, and there is no default")
        if key == "color":
            if not isinstance(value, colour.Color):
                return colour.Color(value).hex_l
            else:
                return value.hex_l
        elif key == "range_unit" and value is False:
            return None
        return value

