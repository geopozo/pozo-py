import colour

default_color_list = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
default_theme = { "color": default_color_list, }

class Themeable():
    def __init__(self, *args, **kwargs):
        self._theme = kwargs.pop("theme", None)
        super().__init__(*args, **kwargs)

    def get_theme(self):
        return self._theme
    def set_theme(self, theme):
        self._theme = theme

class ColorWheel():
    def __init__(self, color_list=default_color_list.copy()):
        self._color_list = color_list
        self._i = 0

    def get_color(self):
        color = self._color_list[self._i % len(self._color_list)]
        self._i += 1
        return color

# We could override the indexer but it's a lot of work and I'm the only one who would see it for now
class ThemeList(list):
    def __init__(self, *iterable, **kwargs):
        self._theme_override = self._process_theme(kwargs.pop('theme_override', {}).copy())
        super().__init__()
        for it in iterable:
            self.add_theme(it)

    def _process_theme(self, theme):
        if theme is None or (isinstance(theme, dict) and len(theme) == 0): return None
        if theme is not None and not isinstance(theme, dict):
            raise TypeError("Can't add theme that is not a dict or None")
        if theme is not None and "color" in theme and isinstance(theme["color"], list):
            theme["color"] = ColorWheel(theme["color"])
        return theme

    def add_theme(self, theme):
        if theme is not None:
            theme = self._process_theme(theme.copy())
        super().append(theme)

    def get_key(self, key):
        if self._theme_override is not None and key in self._theme_override:
            return self._theme_override[key]
        for theme in reversed(self):
            if theme is not None and key in theme:
                return theme[key]
        return None

    def get_color(self):
        color = self.get_key("color")
        if color is None:
            raise ValueError("Couldn't find color in theme list. A fallback is hardcoded into the package, how did this happen?")
        elif isinstance(color, str):
            return colour.Color(color).hex_l
        elif isinstance(color, ColorWheel):
            return colour.Color(color.get_color()).hex_l
        elif isinstance(color, colour.Color):
            return color.hex_l

