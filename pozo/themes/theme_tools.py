import pozo.themes as pzt
import pozo.units as pzu


default_color_list = ['#636EFA', '#EF553B', '#00CC96', '#AB63FA', '#FFA15A', '#19D3F3', '#FF6692', '#B6E880', '#FF97FF', '#FECB52']
default_theme = pzt.ThemeDict({ "color": default_color_list, "track_width": 200 })
#
class MnemonicDictionary(pzt.DynamicTheme):
    def __init__(self, mnemonic_table, registry=pzu.registry):
        if not isinstance(mnemonic_table, dict): raise ValueError("menmonic_table must be dictionary")
        for key, value in mnemonic_table.items():
            if "range_unit" in value:
                pzu.registry.parse_units(value["range_unit"]) # just checking to see if its working
        self._lut = mnemonic_table # renderer will have to do conversons

    def resolve(self, key, contexts):
        mnemonic = None
        for context in contexts:
            if "mnemonic" in context:
                mnemonic = context["mnemonic"]
            elif "mnemonics" in context and len(context["mnemonics"]) >= 1:
                    mnemonic = context["mnemonics"][0]
        if mnemonic is None or mnemonic not in self._lut:
            if '-' in self._lut and key in self._lut['-']: return self._lut['-'][key]
            return None
        if key in self._lut[mnemonic]:
            return self._lut[mnemonic][key]
        if '-' in self._lut and key in self._lut['-']: return self._lut['-'][key]
        return None

    def get_dictionary(self):
        return self._lut

    def set_mnemonic(self, mnemonic, dictionary):
        self._lut[mnemonic] = dictionary

    def get_mnemonic(self, mnemonic):
        if mnemonic not in self._lut: return None
        return self._lut[mnemonic]

    def set_value(self, mnemonic, key, value):
        if mnemonic not in self._lut: self._lut[mnemonic] = {}
        self._lut[mnemonic][key] = value

    def set_fallback(self, key, value):
        self.set_value('-', key, value)

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
        self._current_context = None
        self._i = 0
        super().__init__()

    def get_current_color(self):
        return self._current_color

    # ColorWheel is really married to graphs. Think about this during documentation.
    def resolve(self, key, contexts):
        if not self._each:
            for context in contexts:
                if "type" in context and (context["type"] == self._per or context["type"] in self._per):
                    if self._current_context is None:
                        self._current_context = id(context)
                    elif id(context) != self._current_context:
                        self._current_context = id(context)
                        color = self._color_list[self._i % len(self._color_list)]
                        self._current_color = color
                    else: # same context, do nothing
                        continue
                    self._i += 1
                    break
        else:
            color = self._color_list[self._i % len(self._color_list)]
            self._current_color = color
            self._i += 1
        return self._current_color

