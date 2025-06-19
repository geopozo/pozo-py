import warnings
import pint
import numpy as np
from .drawable import Drawable, VersionedProperty
import pozo.units as pzu


class Trace(Drawable):
    _data = VersionedProperty()
    _unit = VersionedProperty()
    def set_name(self, name):
        warnings.warn("names are no longer used in pozo, use position. string selectors will search for mnemonics", DeprecationWarning)
        self.set_mnemonic(name)
        return super().set_name(name)

    def get_name(self):
        warnings.warn("names are no longer used in pozo, use position. string selectors will search for mnemonics", DeprecationWarning)
        return super().get_name()


    def __len__(self):
        return len(self.get_data())

    def __init__(self, data, **kwargs):

        self.original_data = None
        unit = kwargs.pop('unit', None)
        depth = kwargs.pop('depth', None)
        depth_unit = kwargs.pop('depth_unit', None)
        if depth is None:
            raise ValueError("`depth` cannot be None, you must supply a depth")
        if len(depth) != len(data):
            raise ValueError("Depth and values have different length")

        mnemonic = kwargs.pop("mnemonic", None)
        if 'name' in kwargs and mnemonic:
            raise ValueError("mnemonic and name are the same thing, please specify only one")
        elif 'name' in kwargs and not mnemonic:
            mnemonic = kwargs.get('name', None)
        if not mnemonic:
            raise ValueError(
                "You must supply 'mnemonic' as a name."
            )
        kwargs["name"] = mnemonic

        super().__init__(**kwargs)  # od.ChildObserved sets name
        self.set_data(data, unit=unit, depth=depth, depth_unit=depth_unit)
        self._unit = None
        self._depth_unit = None
        self._mnemonic = mnemonic

    def set_data(self, data, unit=None, depth=None, depth_unit=None):
        unit = self._check_unit(unit)
        depth_unit = self._check_unit(depth_unit)
        depth_len = len(depth) if depth is not None else len(self._depth)
        if depth_len != len(data):
            raise ValueError("Depth and values have different length.")

        self._data = data
        if unit is not None:
            self.set_unit(unit)
        elif isinstance(data, pint.Quantity):
            self.set_unit(data.units)
        # otherwise keeps old unit

        if depth is not None:
            self.set_depth(depth, depth_unit=depth_unit)  # this will set the depth unit

    def _find_nearest(self, value):
        # TODO: align units depth_range, assume same units, but check if pint
        array = np.asarray(self.get_depth())
        idx = np.nanargmin((np.abs(array - value)))
        # if array[idx] != value:
        #    raise ValueError(f"Tried to find value {value} in {self.get_name()} but the closest value was {array[idx]}")
        return idx

    def find_nearest(self, value):
        # TODO: align units depth_range, assume same units, but check if pint
        array = np.asarray(self.get_depth())
        idx = np.nanargmin((np.abs(array - value)))
        # if array[idx] != value:
        #    raise ValueError(f"Tried to find value {value} in {self.get_name()} but the closest value was {array[idx]}")
        return idx, array[idx]

    def get_data(self, slice_by_depth=None, force_unit=False, clean=False):
        if not slice_by_depth or slice_by_depth == [None]:
            data = self._data
        else:
            data = self._data[
                slice(
                    *[
                        self._find_nearest(val) if val is not None else val
                        for val in slice_by_depth
                    ]
                )
            ]
        if clean:
            data = data[np.isfinite(data)].copy()
        if force_unit:
            return pzu.Quantity(data, self.get_unit()) # we could be checking first TODO
        else: return data

    def set_depth(self, depth, depth_unit=None):
        depth_unit = self._check_unit(depth_unit)
        if len(self._data) != len(depth):
            raise ValueError(f"Depth and values have different length: data/depth: {len(self._data)}/{len(depth)}.")

        self._depth = depth
        if depth_unit is not None:
            self.set_depth_unit(depth_unit)
        elif isinstance(depth, pint.Quantity):
            self.set_depth_unit(depth.units)
        # else, keep old units

    def get_depth(self, slice_by_depth=None, force_unit=False, clean=False):
        if not slice_by_depth or slice_by_depth == [None]:
            depth = self._depth
        else:
            depth = self._depth[
                slice(
                    *[
                        self._find_nearest(val) if val is not None else val
                        for val in slice_by_depth
                    ]
                )
            ]
        if clean:
            data = self.get_data(slice_by_depth=slice_by_depth)
            depth = depth[np.isfinite(data)].copy()
        if force_unit:
            return pzu.Quantity(depth, self.get_depth_unit())
        else:
            return depth

    def _check_unit(
        self, unit
    ):  # Call this early, in set_data, in set_depth, in init()
        if isinstance(unit, str):
            return pzu.registry.parse_units(unit)
        elif not isinstance(unit, pint.Unit) and unit is not None:
            raise pint.UndefinedUnitError(str(type(unit))) from TypeError(
                f"Unrecognized unit type: {unit}"
            )
        return unit

    def set_unit(self, unit):
        if isinstance(unit, str):
            unit = pzu.registry.parse_units(unit)
        elif isinstance(unit, pint.Unit) or unit is None:
            pass
        else:
            raise pint.UndefinedUnitError(str(type(unit))) from TypeError(
                f"Unrecognized unit type: {unit}"
            )
        self._unit = unit

    def get_unit(self):
        return self._unit

    def set_depth_unit(self, unit):
        if isinstance(unit, str):
            unit = pzu.registry.parse_units(unit)
        elif isinstance(unit, pint.Unit) or unit is None:
            pass
        else:
            raise pint.UndefinedUnitError(str(type(unit))) from TypeError(
                f"Unrecognized unit type: {unit}"
            )
        self._depth_unit = unit

    def get_depth_unit(self):
        return self._depth_unit

    def convert_depth_unit(self, unit):
        unit = self._check_unit(unit)
        if (
            unit == self.get_depth_unit()
            or unit is None
            or self.get_depth_unit() is None
        ):
            return
        if isinstance(self.get_depth(), pint.Quantity):
            self.set_depth(self.get_depth().to(unit))  # This would be another version
        else:
            self.set_depth(
                pzu.Q(self.get_depth(), self.get_depth_unit()).to(unit).magnitude
            )  # This would be another version
        self.set_depth_unit(unit)

    # not tested
    def convert_unit(self, unit):
        unit = self._check_unit(unit)
        if unit == self.get_unit() or unit is None or self.get_unit() is None:
            return
        if isinstance(self.get_data(), pint.Quantity):
            self.set_data(self.get_data().to(unit))  # This would be another version
        else:
            self.set_data(
                pzu.Q(self.get_data(), self.get_unit()).to(unit).magnitude
            )  # This would be another version
        self.set_unit(unit)

    def set_mnemonic(self, mnemonic):
        super().set_name(mnemonic)
        self._mnemonic = mnemonic

    def get_mnemonic(self):
        return self._mnemonic

    def get_named_tree(self):
        return {
            "trace": {
                "name": self._name,
                "mnemonic": self._mnemonic,
                "length": len(self._values),
            }
        }

    def get_theme(self):
        context = {
            "type": "trace",
            "name": self._name,
            "mnemonic": self._mnemonic,
        }
        return self._get_theme(context=context)

    def __repr__(self):
        return f"{self.get_mnemonic()}: len: {len(self.get_data())} | unit: {self.get_unit()} | depth in: {self.get_depth_unit()} | id: {id(self)}"

class Data(Trace):
    def __init__(self, data, **kwargs):
        warnings.warn("pozo.Data is deprecated, use pozo.Trace", DeprecationWarning)
        super().__init__(self, data, **kwargs)
