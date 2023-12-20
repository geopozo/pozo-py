import pozo.themes as pzt


default_color_list = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
default_theme = { "color": default_color_list, }

class ColorWheel(pzt.DynamicTheme):
    def __init__(self, color_list=default_color_list, per=None, context=None, each=False):
        self._color_list=color_list
        self._each = each
        if per is None and context is not None and "type" in context:
            if context["type"] == "axis":
                self._per = "data"
            else:
                self._per = "axis"
        elif per is None:
            self._per= "axis"
        else:
            self._per = per
        self._current_color = color_list[0]
        self._i = 0
        super().__init__()

    def get_current_color(self):
        return self._current_color

    def resolve(self, key, contexts):
        if len(contexts) >= 1 and "type" in contexts[-1]: # so, it has no context, and it just wrotes
            if isinstance(self._per, str) and contexts[-1]["type"] == self._per:
                pass
            elif isinstance(self._per, tuple) and contexts[-1]["type"] in self._per:
                pass
            else:
                return self._current_color
        elif not self._each:
            raise ValueError("ColorWheel doesn't know whether not to iterate because it lacks context information. Please set each=True in constructor to just iterate freely")
        color = self._color_list[self._i % len(self._color_list)]
        self._current_color = color
        self._i += 1
        return color

