import warnings
import pint
import numpy as np
import ood
import pozo.themes as pzt
import pozo.units as pzu


class Trace(ood.Observed, pzt.Themeable):

    def set_name(self, name):
        warnings.warn("names are no longer used in pozo, use position. string selectors will search for mnemonics", DeprecationWarning)
        self.set_mnemonic(name)
        return super().set_name(name)

    def get_name(self):
        warnings.warn("names are no longer used in pozo, use position. string selectors will search for mnemonics", DeprecationWarning)
        return super().get_name()


    def __len__(self):
        return len(self.get_data())

    def _check_version(self):
        if self.version >= len(self.__data): raise IndexError(f"trace version is set to {self.version} which doesn't exist")

    @property
    def _data(self):
        self._check_version()
        return self.__data[self.version]
    @_data.setter
    def _data(self, data):
        self._check_version()
        self.__data[self.version] = data

    @property
    def _unit(self):
        self._check_version()
        return self.__unit[self.version]
    @_unit.setter
    def _unit(self, unit):
        self._check_version()
        self.__unit[self.version] = unit

    @property
    def note(self):
        self._check_version()
        return self.__note[self.version]
    @note.setter
    def note(self, note):
        self._check_version()
        self.__note[self.version] = note

    # only increments current version if you're on the last one
    def new_version(self, note="", copy=True):
        if copy:
            self.__data.append(self._data.copy())
            self.__unit.append(self._unit.copy())
        else:
            self.__data.append(None)
            self.__unit.append(None)
        self.__note.append(note)
        if self.version == len(self.__data) - 2: self.version += 1

    def latest_version(self):
        return len(self.__data) - 1

    def pop_version(self, version=None):
        if not version:
            self._check_version()
            version = self.version
        elif version >= len(self.__data): raise KeyError(f"Cannot pop version {version} because it doesn't exist")
        if len(self.__data) == 1: raise ValueError("You cannot pop the version if there is only one")

        if version == self.version:
            self.version -= 1 if self.version > 0 else 0
        self.__data.pop(version)
        self.__unit.pop(version)
        self.__note.pop(version)

    # list all versions
    def list_version(self):
        return [
                { 'version': i,
                 'data': d[0],
                 'unit': d[1],
                 'note': d[2]
                 } for i, d in enumerate(zip(self.__data, self.__unit, self.__note))
                ]

    # change versions (semi permanently)
    # get data and unit w/ a version

    def __init__(self, data, **kwargs):
        self.version = 0
        self.__data = [[]]
        self.__unit = [None]
        self.__note = ["original"]

        self.original_data = None
        unit = kwargs.pop('unit', None)
        depth = kwargs.pop('depth', None)
        depth_unit = kwargs.pop('depth_unit', None)
        self._unit = None
        self._depth_unit = None
        if depth is None:
            raise ValueError("`depth` cannot be None, you must supply a depth")
        if len(depth) != len(data):
            raise ValueError("Depth and values have different length")

        self._mnemonic = kwargs.pop("mnemonic", None)
        if 'name' in kwargs and self._mnemonic:
            raise ValueError("mnemonic and name are the same thing, please specify only one")
        elif 'name' in kwargs and not self._mnemonic:
            self._mnemonic = kwargs.get('name', None)
        if not self._mnemonic:
            raise ValueError(
                "You must supply 'mnemonic' as a name."
            )
        kwargs["name"] = self._mnemonic

        self.set_data(data, unit=unit, depth=depth, depth_unit=depth_unit)
        super().__init__(**kwargs)  # od.ChildObserved sets name

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
