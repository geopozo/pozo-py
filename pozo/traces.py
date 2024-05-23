import json
import pint
import numpy as np

from pozo.utils.language import _, _d
from pozo.utils.docs import doc # string gettext language import from __init__.py
from .drawable import Drawable, VersionedProperty
import pozo.units as pzu
@doc(_d("""class Trace: contains one drawable data array

Trace is a unit-aware pointer for a data and depth array. It also stores a mnemonic (name). It is not supposed to store data, but point to the data and then render that data into a graph later using the depth as the Y-axis. Depth and data must be the same shape at all times, they can be replaced together.

Data and its unit are versioned properties. That is, if you want to change the data without losing the original, you can use the functions as they are described below (new_version() etc). You can set the version with `mytrace.version =`. The depth and its unit are not versioned, only data and unit. It always starts at .version == 0.

Pozo attempts to be agnostic towards array type: series, nparrays, polars, pandas, lists are all accepted. pint.Quantity wrappers are often accepted as well.

***** Constructor: pozo.Trace(...)
Args:
    data (array): most types of arrays are accepted, including one wrapped in pint.Quantity
    **kwargs:
        mnemonic (str): REQUIRED: the name/mnemonic of the trace
        name (str): synonym for mnemonic, don't include both
        unit (str or pint.Unit): describes the data unit
        depth (array): another array that must be the same size as data, can also be pint.Quantity
        depth_unit (str or pint.Unit): describes the depth unit
        original_data (any): A pointer to where the original data was extracted from, useful if planning to re-output to a LAS file
"""))
class Trace(Drawable):

    _data = VersionedProperty()
    _unit = VersionedProperty()

    @doc(_d("""method set_name: set name/mnemonic of trace
Args:
    name (str): The name/mnemonic you'd like to set"""))
    def set_name(self, name):
        return self.set_mnemonic(name)

    @doc(_d("""method get_name: get name/mnemonic of trace
Returns:
    The name/mnemonic of the trace"""))
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
        self._unit = None
        self._depth_unit = None
        self.set_data(data, unit=unit, depth=depth, depth_unit=depth_unit)

    @doc(_d("""method find_nearest: retrieve index and actual value of depth closes to input

If you're looking for a value at 1000ft, but we only have a value at 998 ft and 1001 ft, will return 1001 ft and its index

Args:
    value (number): The depth value you are looking for
Returns:
    idx (number): The index of the value closest to what you're looking for
    value (number): The actual value at that index
"""))
    def find_nearest(self, value):
        array = np.asarray(self.get_depth()) # we're going to replace
        idx = np.nanargmin((np.abs(array - value)))
        return idx, array[idx]

    @doc(_d("""method set_data: set the data and optionally the unit, depth, and depth_unit
Args:
    data (array): the data to set
    unit (str of pint.Unit): the unit associated with the data
    depth (array): an array of depth values
    depth_unit: the unit associated with the depth"""))
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

    @doc(_d("""method get_data: returns the data
Args:
    slice_by_depth (tuple): accepts a tuple using slice syntax (:) of positive values to select by depth
    force_unit (boolean): will force wrap the return in a pint.Quantity if True (default False)
    clean (boolean): a hack to deal with poorly behaved renderers, will remove all non-finite values (default False)
Returns:
    the data"""))
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

    @doc(_d("""method set_depth: sets the depth
Args:
    depth (array): The depth to set
    depth_unit (str or pint.Unit): The depth's associated unit"""))
    def set_depth(self, depth, depth_unit=None):
        depth_unit = self._check_unit(depth_unit)
        if len(self._data) != len(depth):
            raise ValueError(_("`depth` and `data` have different lengths. data/depth: %d/%d") % (len(self._data), len(depth)))

        self._depth = depth
        if depth_unit is not None:
            self.set_depth_unit(depth_unit)
        elif isinstance(depth, pint.Quantity):
            self.set_depth_unit(depth.units)

    @doc(_d("""method get_depth: returns the depth array
Args:
    slice_by_depth (tuple): accepts a tuple using slice syntax (:) of positive values to select by depth
    force_unit (boolean): will force wrap the return in a pint.Quantity if True (default False)
    clean (boolean): a hack to deal with poorly behaved renderers, will remove depths where non-finite values in the data (default False)
Returns:
    depth array or slice"""))
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

    @doc(_d("""method set_unit: sets the unit associated with the data
Args:
    unit (str or pint.Unit): the unit to set"""))
    def set_unit(self, unit):
        unit = self._check_unit(unit) # TODO UNIT
        self._unit = unit

    @doc(_d("""method get_unit: gets the unit associated with the data
Returns:
    the unit exactly as it was set"""))
    def get_unit(self):
        return self._unit

    @doc(_d("""method set_depth_unit: sets the unit associated with the depth
Args:
    unit (str or pint.Unit): the unit to set"""))
    def set_depth_unit(self, unit):
        unit = self._check_unit(unit) # TODO UNIT
        self._depth_unit = unit

    @doc(_d("""method get_depth_unit: gets the unit associated with the depth
Returns:
    the unit exactly as it was set"""))
    def get_depth_unit(self):
        return self._depth_unit

    @doc(_d("""method convert_depth_unit: will convert the depth to the specified unit, example ft to meters

Since we cannot graph traces specified with different depth units, this can be used to make a permanent conversion.

It will also change the recorded unit.

Args:
    unit (str or pint.Unit): the target unit
"""))
    def convert_depth_unit(self, unit):
        unit = self._check_unit(unit) # TODO UNIT
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

    @doc(_d("""method convert_unit: a convenience function to change the unit of your data

Most Trace functions don't permanently change and/or create new data arrays: this one does.

Args:
    unit (str or pint.Unit): the target unit
"""))
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

    @doc(_d("""method set_mnemonic: set name/mnemonic of trace
Args:
    mnemonic (str): The name/mnemonic you'd like to set"""))
    def set_mnemonic(self, mnemonic):
        super().set_name(mnemonic)

    @doc(_d("""method get_mnemonic: get name/mnemonic of trace
Returns:
    The name/mnemonic of the trace"""))
    def get_mnemonic(self):
        return super().get_name()

    def _get_context(self):
        return {
            "type": "trace",
            "name": self._name,
            "mnemonic": self._name
        }
    @doc(_d("""method get_dict: return relevant properties of trace as key-value dictionary

Returns:
    A key-value dictionary"""))
    def get_dict(self):
        return {
            "trace": {
                "name/mnemonic": self._name,
                "length": len(self._data),
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
    @doc(_d("""method get_theme: return the stored theme with a context object

Returns:
    A theme object (pozo.themes.help()) with attached context for this trace."""))
    def get_theme(self):
        return self._get_theme(context=self._get_context())

    def __repr__(self):
        return json.dumps(self.get_dict(), indent=2)
