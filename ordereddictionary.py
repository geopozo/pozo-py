from collections import namedtuple

# Not sure if I should inherit these two. Maybe `from _____` is sufficient.
class SelectorError(IndexError, KeyError): # We wrap errors so we can detect if we sent them 
    pass
class SelectorTypeError(TypeError): # We wrap errors so we can detect if we sent them 
    pass

_Key_I = namedtuple('Key_I', 'key index')
class Key_I(_Key_I):
    pass
    def check_type(self):
        return isinstance(self[0], str) and isinstance(self[1], int)
    def enforce_type(self):
        if not self.check_type(): raise SelectorTypeError("Supplied Key_I must be tuple of (str, int)")

class ObservingOrderedDictionary():

    # Needs to accept a custom indexer
    def __init__(self, *args, **kwargs):
        self._items_ordered = []
        self._items_by_name = {}
        self._items_by_id = {}

        super().__init__(*args, **kwargs)

    def __iter__(self):
        self._iterator_index = 0
        return self

    def __next__(self):
        if self._iterator_index < len(self._items_ordered):
            ret = self._items_ordered[self._iterator_index]
            self._iterator_index += 1
            return ret
        raise StopIteration

    # Can throw regular IndexError if one value of the keys is out of order
    # Should it accept other selectors?
    def reorder(self, order):
        if ( not isinstance(order, list) or
            len(order) != len(set(order)) != len(self._items_ordered) or
            max(order) >= len(self._items_ordered) or
            min(order) < 0 or
            not all(isinstance(i, int) for i in order) ):
            raise SelectorError() from IndexError("Some/All of the indices supplied do not exist")
        self._items_ordered = [self._items_ordered[i] for i in order]

    # Can throw regular IndexError if one value is out of error
    # Should it accept other selectors
    def swap(self, item1, item2):
        if item1 < 0 or item1 >= len(self._items_ordered) or item2 < 0 or item1 >= len(self._items_ordered):
            raise SelectorError() from IndexError("The items to swap must be valid indices")
        self._items_ordered[item1], self._items_ordered[item2] = self._items_ordered[item2], self._items_ordered[item1]

    # Will throw IndexErrors if any number is out of range 
    def _enforce_index(self, index, target = None):
        if target is None:
            target = self._items_ordered
        if isinstance(index, int):
            if index < 0 or index >= len(target):
                raise SelectorError() from IndexError("The index supplied is out of range")
        elif isinstance(index, slice):
            self._enforce_index(index.start, target)
            self._enforce_index(index.stop, target)
        return True

    # Because we can't check to see if we've supplied a correct object type, we can only return true or false
    def has_item(self, selector):
        if id(selector) in self._items_by_id: return True
        try:
            self.get_item(selector)
            return True
        except (SelectorError, SelectorTypeError):
            return False

    # This should throw an error if name not in dictionary
    def _enforce_name(self, name):
        if name not in self._items_by_name:
            raise SelectorError(f"Name {name} does not seem to be valid.") from KeyError()
        return True

    # Throws key/index errors
    def _get_items_by_name(self, name):
        if isinstance(name, Key_I):
            name, index = name[0], name[1]
        else:
            index = slice(None)
        self._enforce_name(name)
        self._enforce_index(name[1], target = self._items_by_name[name])
        res = self._items_by_name[name][index]
        if not isinstance(res, list):
            return [res]
        return res

    # Throws key/index errors
    def _get_items_by_slice(self, indices):
        self._enforce_index(indices)
        return self._items_ordered[indices]

    # Throws key/index errors
    def _get_item_by_index(self, index):
        self._enforce_index(index)
        return self._items_ordered[index]

    # Can return an empty list if a) no selectors supplied or b) skip_bad=True. 
    # If selector makes no sense (4.5), will still throw error.
    def get_items(self, *selectors, **kwargs):
        cap = kwargs.get('_cap', 0)
        skip_bad = kwargs.get('skip_bad', False)
        items = []
        if not selectors or selectors[0] is None:
            ret = self._items_ordered
            del selectors
        for selector in selectors:
            if cap and len(items) >= cap: break
            if isinstance(selector, str):
                try:
                    items.extend(self._get_items_by_name(selector))
                except SelectorError as e:
                    if skip_bad: pass
                    else: raise e
            elif isinstance(selector, Key_I) and selector.check_type():
                try:
                    items.extend(self._get_items_by_name(selector))
                except SelectorError as e:
                    if skip_bad: pass
                    else: raise e
            elif isinstance(selector, int):
                try:
                    items.append(self._get_item_by_index(selector))
                except SelectorError as e:
                    if skip_bad: pass
                    else: raise e
            elif isinstance(selector, slice):
                try:
                    items.extend(self._get_items_by_slice(selector))
                except SelectorError as e:
                    if skip_bad: pass
                    else: raise e
            else:
                raise SelectorTypeError("Selectors must of type: str, Key_I(str, int), int, slice.")
        if cap and len(items) > cap: items = items[0:cap]
        return items

    def get_item(self, selector, match = 0, return_none = False):
        items = self.get_items(selector, _cap = match + 1, skip_bad = return_none)
        if len(items) <= match:
            if not return_none:
                raise SelectorError(f"Supplied match ({match}) >= len(results) ({len(items)})") from IndexError()
            return None
        return items[match]

    def _add_item_to_by_name(self, item, name=None):
        if name is None:
            name = item.get_name()
        if name in self._items_by_name:
            self._items_by_name[name].append(item)
        else:
            self._items_by_name[name] = [item]

    def _remove_item_from_by_name(self, item, name=None):
        if name is None:
            name=item.get_name()
        if name in self._items_by_name:
            self._items_by_name[name].remove(item)
            if len(self._items_by_name[name]) == 0:
                del self._items_by_name[name]

    def _count_dictionary(self):
        count = 0
        for v in self._items_by_name.values():
            count += len(v)
        return count

    def add_items(self, *items): # check to see if item is type childwithparent (and I am parent?)
        for item in items:
            if self.has_item(item):
                raise ValueError("Tried to add item that already exists.")
        for item in items:
            if isinstance(item, ChildObserved):
                item._register_parents(self)
            self._items_ordered.append(item)
            self._add_item_to_by_name(item)
            self._items_by_id[id(item)] = item

    def _child_update(self, child, **kwargs):
        oldname = kwargs.get('name', None)
        if oldname is not None and oldname in self._items_by_name:
            self._remove_item_from_by_name(child, name=oldname)
            self._add_item_to_by_name(child)

    def pop_items(self, *selectors):
        items = self.get_items(*selectors)
        for item in items:
           self._items_ordered.remove(item)
           self._remove_item_from_by_name(item)
           del self._items_by_id[id(item)]
        return items

class ChildObserved():

    def __init__(self, *args, **kwargs):
        self._name = kwargs.pop('name', "")
        self._parents_by_id = {}

        super().__init__(*args, **kwargs)

    def get_name(self):
        return self._name

    def set_name(self, name):
        if self._name == name: return
        old_name = self._name
        self._name = name
        self._notify_parents(name=old_name)

    def _register_parents(self, *parents):
        for parent in parents:
            if id(parent) in self._parents_by_id: continue
            if not isinstance(parent, ObservingOrderedDictionary):
                raise ValueError("All parents must inhert ObservingOrderedDictionary class")
            self._parents_by_id[id(parent)] = parent

    def _deregister_parents(self, *parents):
        for parent in parents:
            if id(parent) in self._parents_by_id:
                del self._parents_by_id[id(parent)]

    def _get_parents(self):
        return list(self._parents_by_id.values())

    def _notify_parents(self, **kwargs):
        map(lambda parent: parent._child_update(self, **kwargs), self._parents_by_id.values())

