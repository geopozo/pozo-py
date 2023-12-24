import pint
from io import StringIO
from IPython.core.display import HTML
import lasio

import pandas
import pozo

class WConf(str):
    def set_confidence(self, confidence):
        self._confidence = confidence
        return self
    def get_confidence(self):
        if hasattr(self, "_confidence"):
            return self._confidence
        return "LOW"

class LasRegistry(pint.UnitRegistry):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._mnemonic_units = {}


    def add_las_map(self, mnemonic, unit, p_unit, confidence="LOW"):
        self.parse_units(p_unit)
        if mnemonic not in self._mnemonic_units:
            self._mnemonic_units[mnemonic] = {}
        self._mnemonic_units[mnemonic][unit] = WConf(p_unit).set_confidence(confidence)


    def las_parse(self, mnemonic, unit, confidence="LOW"):
        if mnemonic in self._mnemonic_units and unit in self._mnemonic_units[mnemonic]:
            return self.parse_units(self._mnemonic_units[mnemonic][unit])
        else:
            try:
                if not unit or unit == "": raise pint.UndefinedUnitError("Disallow empty unit")
                return self.parse_units(unit)
            except pint.UndefinedUnitError as e:
                raise pint.UndefinedUnitError(f"{unit} for {mnemonic} not found. {str(e)}")

    def check_las(self, las):
        def n0(s): # If None, convert to ""
            return "" if s is None else str(s)
        d = chr(0X1e)
        result = [f"mnemonic{d}las unit{d}pozo mapping{d}confidence{d}parsed{d}description"]
        for curve in las.curves:
            mnemonic = pozo.deLASio(curve)
            pozo_match = None
            parsed = None
            if mnemonic in self._mnemonic_units and curve.unit in self._mnemonic_units[mnemonic]:
                pozo_match = self._mnemonic_units[mnemonic][curve.unit]
                confidence = pozo_match.get_confidence()
            else:
                confidence = "No pozo match- MEDIUM"
            try:
                parsed = self.las_parse(mnemonic, pozo_match) if pozo_match else self.las_parse(mnemonic, curve.unit)
            except pint.UndefinedUnitError as e:
                confidence = " - " + str(e) + " - NONE"
            result.append(d.join([n0(x) for x in [mnemonic,
                                             curve.unit,
                                             pozo_match,
                                             confidence,
                                             parsed,
                                             curve.descr]
                                  ]))
        try:
            display(HTML(pandas.read_csv(StringIO("\n".join(result)), delimiter=d, na_filter=False).to_html()))
        except Exception as e:
            display(str(e))
            display(HTML("<br>".join(result)))
