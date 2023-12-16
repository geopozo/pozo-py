default_color_list = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
default_theme = { "color": default_color_list, }

class Themer():
    def __init__(self, *args, **kwargs):
        self._theme = kwargs.pop("theme", None)
        super().__init__(*args, **kwargs)

    def get_theme(self):
        return self._theme
    def set_theme(self, theme):
        self._theme = theme

class Renderer():
    pass

class ColorWheel():
    def __init__(self, color_list=default_color_list.copy()):
        self._color_list = color_list
        self.restart_counter()
    def restart_counter(self):
        self._i = 0
    def get_color(self):
        color = self._color_list[self._i % len(self._color_list)]
        self._i += 1
        return color

# We could override the indexer but it's a lot of work and I'm the only one who would see it for now
class ThemeList(list):
    def __init__(self, *iterable):
        super().__init__()
        for it in iterable:
            self.add_theme(it)
    def add_theme(self, theme):
        if theme is not None:
            theme = theme.copy()
            if theme and "color" in theme and isinstance(theme["color"], list):
                theme["color"] = ColorWheel(theme["color"])
        super().append(theme)
    def get_key(self, key):
        for theme in reversed(self):
            if theme is not None and key in theme:
                return theme[key]
        return None

    def get_color(self):
        color = self.get_key("color")
        if color is None:
            raise ValueError("Couldn't find color in theme list. A fallback is hardcoded into the package, how did this happen?")
        elif isinstance(color, str):
            return color
        elif isinstance(color, ColorWheel):
            return color.get_color()
        # also check for color object (python)

# These imports we want in this name space, but they use the stuff above!
from .plotly import Plotly
