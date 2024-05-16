import ood
import pozo.themes as pzt
import warnings
# test versions
# do some string and object representations of everything
# do some tests (fix themes)
# do help
# render this
# separate renderer into renderTrace and renderInterval
# write about mira geoscience
# think more about versions and copies

class VersionedProperty:
    def __set_name__(self, owner, name):
        if type(owner) == str(Drawable):
            raise AttributeError(f"{name} must be a member of a class inheriting pozo.drawable.Drawable, not {owner}. Is type {type(owner)}.")
        self._private_name = "_" + name
        self._name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return AttributeError(f"{self._name} can only be accessed from instantiated ojects, not classes")
        return getattr(obj, self._private_name)[obj.version]

    def __set__(self, obj, value):
        if id(self) not in obj._versioned_properties: obj._versioned_properties[id(self)] = self
        temp = getattr(obj, self._private_name, None)
        if temp is None:
            temp = [value]
            setattr(obj, self._private_name, temp)
        else:
            temp[obj.version] = value

    def __delete__(self, obj):
        raise AttributeError(f"Can't delete {self._name}, please use {obj.__name__}.remove_version().")

    def new_version(self, obj, copy=True, deep=True, index=-1):
        if deep: copy = False
        if index == -1:
            index = obj._latest_version
        temp = getattr(obj, self._private_name, None)
        if temp is None:
            temp = [None]
            setattr(obj, self._private_name, temp)
        if deep and hasattr(temp[max(index-1, 0)], "deepcopy"):
            temp.insert(index, temp[max(index-1, 0)].deepcopy())
        if copy and hasattr(temp[max(index-1, 0)], "copy"):
            temp.insert(index, temp[max(index-1, 0)].copy())
        else:
            temp.insert(index, None)
            if deep or copy:
                warnings.warn(f"{self._name} was asked for a copy but it contains no native .copy() method, new version is None")

    def remove_version(self, obj, version):
        temp = getattr(obj, self._private_name, None)
        if temp is None: return
        temp.pop(version)

class Drawable(ood.Observed, pzt.Themeable):
    def __init__(self, *args, **kwargs):
        self.version = 0
        self._latest_version = 0
        self._versioned_properties = {}
        super().__init__(*args, **kwargs)

    @property # makes it read only
    def latest_version(self):
        return self._latest_version

    def new_version(self, copy=False, deep=True):
        self._latest_version += 1
        self.version = self._latest_version
        for prop in self._versioned_properties.values():
            prop.new_version(self, copy=copy, deep=deep)

    def insert_version(self, copy=False, deep=True):
        self._latest_version += 1
        self.version += 1
        for prop in self._versioned_properties.values():
            prop.new_version(self, copy=copy, deep=deep, index=self.version)

    def remove_version(self, version=None):
        if self._latest_version == 0: raise RuntimeError("Cannot pop last version")
        if version > self._latest_version: return None
        self._latest_version -= 1
        if version < self.version:
            self.version = self.version-1
        self.version = min(max(self.version, 0), self._latest_version)
        for prop in self._versioned_properties.values():
            prop.remove_version(self, version)

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
