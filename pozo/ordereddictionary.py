from pozo.exceptions import SelectorTypeError, SelectorError
import pozo.extra_selectors as s


## We need to keep track whether or not the output is sorted or not
## It will generally by sorted if a) there is only one selector b) the selector is not a dictionary
## We need to start store _items_by_id w/ position
## Changing and swapping position needs to reflect their change

strict_index = False

class ObservingOrderedDictionary(s.Selector):

    # Needs to accept a custom indexer
    def __init__(self, *args, **kwargs):
        global strict_index
        self._strict_index = kwargs.pop('strict_index', strict_index)
        self._items_ordered = []
        self._items_by_name = {}
        self._items_by_id = {}

        super().__init__(*args, **kwargs)

    ## Sort of an odd function here- could make a _get_item_by_id but it's overkill.
    def process(self, parent, **kwargs):
        strict_index = kwargs.get('strict_index', self._strict_index)
        if id(self) in parent._items_by_id:
            return [self]
        if strict_index: raise SelectorError("Bad index supplied: item doesn't exist")
        return []

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
        index = kwargs.pop("index", slice(None))
        if not self._enforce_key(name, **kwargs): return []
        if not self._enforce_index(index, **kwargs): return []
        items = self._items_by_name[name][index]
        if not isinstance(items, list):
            return [items]
        return items

    # Throws key/index errors
    def _get_items_by_slice(self, indices, **kwargs):
        if not self._enforce_index(indices, **kwargs): return []
        return self._items_ordered[indices]

    # Throws key/index errors
    def _get_item_by_index(self, index, **kwargs):
        if not self._enforce_index(index, **kwargs): return
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
            elif isinstance(selector, s.Selector):
                items.extend(selector.process(self, **kwargs))
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

    def get_item(self, selector, match = 0, **kwargs):
        match = kwargs.get('match', 0)
        strict_index = kwargs.get('strict_index', self._strict_index)
        if "_cap" in kwargs: kwargs.pop("_cap")
        items = self.get_items(selector, _cap = match + 1, **kwargs)
        if len(items) <= match:
            if strict_index:
                raise SelectorError(f"Supplied match ({match}) >= len(results) ({len(items)})") from IndexError()
            return None
        return items[match]

    # Because we can't check to see if we've supplied a correct object type, we can only return true or false
    def has_item(self, selector):
        try:
            self.get_item(selector, strict_index=True)
            return True
        except (SelectorError, SelectorTypeError):
            return False

    # Can throw regular IndexError if one value of the keys is out of order
    def reorder_items(self, order): # take other selectors
        if ( not isinstance(order, list) or
            len(order) != len(set(order)) != len(self._items_ordered) or
            max(order) >= len(self._items_ordered) or
            min(order) < 0 or
            not all( (
                 isinstance(i, (int, str, s.Name_I))
                 or id(i) in self._items_by_id
                ) for i in order)):
            raise SelectorError("You must list ALL objects present by index, name, Name_I or actual object") from IndexError()
        for i, selector in enumerate(order):
            item = None
            if id(selector) in self._items_by_id: # Should be selector
                item = selector
            elif isinstance(item, (str, s.Name_I)):
                item = self._get_items_by_name(selector, strict_index=True)
            if item is None:
                raise IndexError("One of your selectors didn't match an existing item")
            elif len(item) != 1:
                raise ValueError("One of your selectors returned more than one item. You can use selectors.Name_I to avoid this")
            order[i] = self._items_ordered.index(item[0])

        self._items_ordered = [self._items_ordered[i] for i in order]

    def put_items(self, selector, position):
        items = self.get_items(selector, strict_index=True)
        if not isinstance(value, int):
            raise TypeError("The position to move to must be an integer, follow array access syntax")
        if position != len(self._get_items_by_slice):
            self._enforce_index(position, strict_index=True)
        for item in reversed(items):
            original_index = self._items_ordered.index(item)
            self._items_ordered[original_index] = None
            self._items_ordered.insert(position, item) # TODO, can it take negatives?
            self._items_ordered.remove(None)


    def move_item(self, selector, value): # TODO, can it take negatives
        items = self.get_items(selector, strict_index=True)
        if not isinstance(value, int):
            raise TypeError("The value to move to must be an integer, positive or negative")
        for item in items:
           new_position = min(max(self._items_ordered.index(item) + value, 0), len(self._items_ordered.index(item)))
           self._put_items(item, new_position)


    def pop_items(self, *selectors, **kwargs):
        items = self.get_items(*selectors, **kwargs)
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

