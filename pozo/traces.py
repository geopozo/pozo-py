import json
import pint
import numpy as np

from .drawable import Drawable, VersionedProperty
import pozo.units as pzu
from . import _ as _
class Trace(Drawable):
    _data = VersionedProperty()
    _unit = VersionedProperty()

    def set_name(self, name):
        return self.set_mnemonic(name)

    def get_name(self):
        return self.get_mnemonic()

    def __len__(self):
        return len(self.get_data())

    def _check_unit(self, unit):
        if not unit: return None
        if isinstance(unit, str):
            return pzu.registry.parse_units(unit)
        elif not isinstance(unit, pint.Unit):
            raise pint.UndefinedUnitError(str(type(unit))) from TypeError(
                _("Unrecognized unit type: %s") % unit
            )
        return unit

    def __init__(self, data, **kwargs):
        self.original_data = kwargs.pop('original_data', None)
        unit = kwargs.pop('unit', None)
        depth = kwargs.pop('depth', None)
        depth_unit = kwargs.pop('depth_unit', None)
        if depth is None:
            raise ValueError(_("`depth` cannot be `None`, you must supply a depth"))
        if len(depth) != len(data):
            raise ValueError(_("`depth` and `data` have different lengths. data/depth: %d/%d") % (len(data), len(depth)))

        mnemonic = kwargs.pop("mnemonic", None)
        if 'name' in kwargs:
            if mnemonic:
                raise ValueError(_("`mnemonic` and `name` are the same thing, please specify only one"))
            mnemonic = kwargs.get('name', None)
        if not mnemonic:
            raise ValueError(
                _("You must supply `mnemonic` or `name` (not both)")
            )
        kwargs["name"] = mnemonic

        super().__init__(**kwargs)  # will init version logic before assining units that use it
        self.set_data(data, unit=unit, depth=depth, depth_unit=depth_unit)
        self._unit = None
        self._depth_unit = None

    def find_nearest(self, value):
        array = np.asarray(self.get_depth()) # we're going to replace
        idx = np.nanargmin((np.abs(array - value)))
        return idx, array[idx]

    def set_data(self, data, unit=None, depth=None, depth_unit=None):
        unit = self._check_unit(unit)
        depth_unit = self._check_unit(depth_unit)
        depth_len = len(depth) if depth is not None else len(self._depth)
        if depth_len != len(data):
            raise ValueError(_("`depth` and `data` have different lengths. data/depth: %d/%d") % (len(data), len(depth_len)))

        self._data = data
        if unit is not None:
            self.set_unit(unit)
        elif isinstance(data, pint.Quantity):
            self.set_unit(data.units)

        if depth is not None:
            self.set_depth(depth, depth_unit=depth_unit)

    def get_data(self, slice_by_depth=None, force_unit=False, clean=False):
        if not slice_by_depth or slice_by_depth == [None]:
            data = self._data
        else:
            data = self._data[
                slice(
                    *[
                        self.find_nearest(val)[0] if val is not None else val
                        for val in slice_by_depth
                    ]
                )
            ]
        if clean:
            data = data[np.isfinite(data)].copy() # bad
        if force_unit and not isinstance(data, pint.Quantity):
            return pzu.Quantity(data, self.get_unit())
        return data

    def set_depth(self, depth, depth_unit=None):
        depth_unit = self._check_unit(depth_unit)
        if len(self._data) != len(depth):
            raise ValueError(_("`depth` and `data` have different lengths. data/depth: %d/%d") % (len(self._data), len(depth)))

        self._depth = depth
        if depth_unit is not None:
            self.set_depth_unit(depth_unit)
        elif isinstance(depth, pint.Quantity):
            self.set_depth_unit(depth.units)

    def get_depth(self, slice_by_depth=None, force_unit=False, clean=False):
        if not slice_by_depth or slice_by_depth == [None]:
            depth = self._depth
        else:
            depth = self._depth[
                slice(
                    *[
                        self.find_nearest(val)[0] if val is not None else val
                        for val in slice_by_depth
                    ]
                )
            ]
        if clean:
            data = self.get_data(slice_by_depth=slice_by_depth) # cleans by NaN's in data- hate it
            depth = depth[np.isfinite(data)].copy()
        if force_unit and not isinstance(depth, pint.Quantity):
            return pzu.Quantity(depth, self.get_depth_unit())
        return depth

    def set_unit(self, unit):
        unit = self._check_unit(unit)
        self._unit = unit

    def get_unit(self):
        return self._unit

    def set_depth_unit(self, unit):
        unit = self._check_unit(unit)
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
            self.set_depth(self.get_depth().to(unit))
        else:
            self.set_depth(
                pzu.Q(self.get_depth(), self.get_depth_unit()).to(unit).magnitude
            )
        self.set_depth_unit(unit)

    def convert_unit(self, unit):
        unit = self._check_unit(unit)
        if unit == self.get_unit() or unit is None or self.get_unit() is None:
            return
        if isinstance(self.get_data(), pint.Quantity):
            self.set_data(self.get_data().to(unit))  # This would be another version
        else:
            self.set_data(
                pzu.Q(self.get_data(), self.get_unit()).to(unit).magnitude
            )
        self.set_unit(unit)

    def set_mnemonic(self, mnemonic):
        super().set_name(mnemonic)

    def get_mnemonic(self):
        return super().get_name()

    def _get_context(self):
        return {
            "type": "trace",
            "name": self._name,
            "mnemonic": self._name
        }

    def get_dict(self):
        return {
            "trace": {
                "name/mnemonic": self._name,
                "length": len(self._values),
                "type": type(self._data).__name__,
                "unit": str(self.get_unit()),
                "depth type": type(self._depth).__name__,
                "depth unit": str(self.get_depth_unit()),
                # "depth_hash": ??
                "context": self._get_context(),
                "theme": self.get_theme(),
                "versions": self.get_version_dict()
            }
        }

    def get_theme(self):
        return self._get_theme(context=self._get_context())

    def __repr__(self):
        return json.dumps(self.get_dict())
