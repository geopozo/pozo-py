from pozo.exceptions import SelectorTypeError, SelectorError
import pozo.extra_selectors as s
# Not sure if I should inherit these two. Maybe `from _____` is sufficient.


## We need to keep track whether or not the output is sorted or not
## It will generally by sorted if a) there is only one selector b) the selector is not a dictionary
## We need to start store _items_by_id w/ position
## Changing and swapping position needs to reflect their change

class ObservingOrderedDictionary():

    # Needs to accept a custom indexer
    def __init__(self, *args, **kwargs):
        self._strict_index = kwargs.pop('strict_index', "True")
        self._items_ordered = []
        self._items_by_name = {}
        self._items_by_id = {}

        super().__init__(*args, **kwargs)

    def set_strict(self):
        self._strict_index = True
    def unset_strict(self):
        self._strict_index = False

    def __len__(self):
        return len(self._items_ordered)

    def __iter__(self):
        self._iterator_index = 0
        return self

    def __next__(self):
        if self._iterator_index < len(self._items_ordered):
            ret = self._items_ordered[self._iterator_index]
            self._iterator_index += 1
            return ret
        raise StopIteration

    def _add_item_to_by_name(self, item, name=None): # do we have verify this?
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

    def _child_update(self, child, **kwargs):
        oldname = kwargs.get('name', None)
        if oldname is not None and oldname in self._items_by_name:
            self._remove_item_from_by_name(child, name=oldname)
            self._add_item_to_by_name(child)

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

    # Will throw IndexErrors if any number is out of range
    def _enforce_index(self, index, **kwargs): # TODO, this needs to allow negatives
        target = kwargs.get("target", None)
        strict_index = kwargs.get("strict_index", self._strict_index)
        if target is None:
            target = self._items_ordered
        if isinstance(index, int):
            if index < 0 or index >= len(target):
                if strict_index: raise SelectorError() from IndexError("The index supplied is out of range")
                return False
        elif isinstance(index, slice):
            if index.start is not None:
                if not self._enforce_index(index.start, **kwargs): return False
            if index.stop is not None:
                if not self._enforce_index(index.stop-1, **kwargs): return False
        return True

    def _count_dictionary(self): #TODO, check to make sure no overlapping items
        count = 0
        for v in self._items_by_name.values():
            count += len(v)
        return count

    # This should throw an error if name not in dictionary
    def _enforce_key(self, name, **kwargs):
        strict_index = kwargs.get("strict_index", self._strict_index)
        if name not in self._items_by_name:
            if strict_index: raise SelectorError(f"Name {name} does not seem to be valid.") from KeyError()
            return False
        return True

    # Throws key/index errors
    def _get_items_by_name(self, name, **kwargs):
        if isinstance(name, s.Key_I):
            name, index = name[0], name[1]
        else:
            index = slice(None)
        self._enforce_key(name, **kwargs)
        self._enforce_index(index, **kwargs)
        items = self._items_by_name[name][index]
        if not isinstance(items, list):
            return [items]
        return items

    # Throws key/index errors
    def _get_items_by_slice(self, indices, **kwargs):
        self._enforce_index(indices, **kwargs)
        return self._items_ordered[indices]

    # Throws key/index errors
    def _get_item_by_index(self, index, **kwargs):
        self._enforce_index(index, **kwargs)
        return self._items_ordered[index]

    # Can return an empty list if a) no selectors supplied or b) skip_bad=True.
    # If selector makes no sense (4.5), will still throw error.
    def get_items(self, *selectors, **kwargs):
        cap = kwargs.get('_cap', 0)
        items = []
        if not selectors or selectors[0] is None:
            items = self._items_ordered
            selectors = []
        for selector in selectors:
            if cap and len(items) >= cap: break
            if isinstance(selector, str):
                items.extend(self._get_items_by_name(selector, **kwargs))
            elif isinstance(selector, s.Key_I) and selector.check_type():
                items.extend(self._get_items_by_name(selector, **kwargs))
            elif isinstance(selector, int):
                items.append(self._get_item_by_index(selector, **kwargs))
            elif isinstance(selector, slice):
                items.extend(self._get_items_by_slice(selector, **kwargs))
            else:
                raise SelectorTypeError("Selectors must of type: str, int, slice or a class from package selectors.")
        if cap and len(items) > cap: items = items[0:cap]
        resulting_items_by_id = {}
        for item in items:
            if id(item) not in resulting_items_by_id:
                resulting_items_by_id[id(item)] = item
        sorted_items = []
        for ref_item in self._items_ordered:
            if id(ref_item) in resulting_items_by_id:
                sorted_items.append(ref_item)
        return sorted_items

    def get_item(self, selector, match = 0, return_none = False):
        items = self.get_items(selector, _cap = match + 1, skip_bad = return_none)
        if len(items) <= match:
            if not return_none:
                raise SelectorError(f"Supplied match ({match}) >= len(results) ({len(items)})") from IndexError()
            return None
        return items[match]

    # Because we can't check to see if we've supplied a correct object type, we can only return true or false
    def has_item(self, selector):
        if id(selector) in self._items_by_id: return True
        try:
            self.get_item(selector)
            return True
        except (SelectorError, SelectorTypeError):
            return False

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
        # TODO now we're recording order with the dictionary too

    # Can throw regular IndexError if one value is out of error
    # Should it accept other selectors
    def swap(self, item1, item2):
        if item1 < 0 or item1 >= len(self._items_ordered) or item2 < 0 or item1 >= len(self._items_ordered):
            raise SelectorError() from IndexError("The items to swap must be valid indices")
        self._items_ordered[item1], self._items_ordered[item2] = self._items_ordered[item2], self._items_ordered[item1]
        # TODO now we're recording order with the dictionary too

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

