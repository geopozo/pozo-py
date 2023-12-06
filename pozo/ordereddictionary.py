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
    def _process(self, parent):
        if id(self) in parent._items_by_id:
            return [self]
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

    def add_items(self, *items, **kwargs): # check to see if item is type childwithparent (and I am parent?)
        position = kwargs.pop("position", len(self))
        for item in items:
            if self.has_item(item):
                raise ValueError("Tried to add item that already exists.")
        for i, item in enumerate(items):
            if isinstance(item, ChildObserved):
                item._register_parents(self)
            self._items_ordered.insert(position+i, item)
            self._add_item_to_by_name(item)
            self._items_by_id[id(item)] = item

    # Will throw IndexErrors if any number is out of range
    def _check_index(self, index, target = None): # TODO, this needs to allow negatives
        if target is None:
            target = self._items_ordered
        if isinstance(index, int):
            if index < 0 or index >= len(target):
                return False
        elif isinstance(index, slice):
            if index.start is not None:
                if not self._check_index(index.start): return False
            if index.stop is not None:
                if not self._check_index(index.stop-1): return False
        return True

    def _count_dictionary(self): #TODO, check to make sure no overlapping items
        count = 0
        for v in self._items_by_name.values():
            count += len(v)
        return count

    # This should throw an error if name not in dictionary
    def _check_key(self, name):
        if name not in self._items_by_name:
            return False
        return True

    # Throws key/index errors
    def _get_items_by_name(self, name, index=slice(None)):
        if not self._check_key(name): return []
        if not self._check_index(index): return []
        items = self._items_by_name[name][index]
        if not isinstance(items, list):
            return [items]
        return items

    # Throws key/index errors
    def _get_items_by_slice(self, indices):
        if not self._check_index(indices): return []
        return self._items_ordered[indices]

    # Throws key/index errors
    def _get_item_by_index(self, index):
        if not self._check_index(index): return
        return self._items_ordered[index]

    # Can return an empty list if a) no selectors supplied or b) skip_bad=True.
    # If selector makes no sense (4.5), will still throw error.
    def get_items(self, *selectors, **kwargs):
        cap = kwargs.get('_cap', 0)
        index = kwargs.get('index', None)
        strict_index = kwargs.get('strict_index', self._strict_index)
        items = []
        if not selectors or selectors[0] is None:
            items = self._items_ordered
            selectors = []
        for i, selector in enumerate(selectors):
            if cap and len(items) >= cap: break
            new_items = None
            if isinstance(selector, int):
                new_items = [self._get_item_by_index(selector)]
            elif isinstance(selector, slice):
                new_items = self._get_items_by_slice(selector)
            elif isinstance(selector, str):
                if index:
                    new_items = self._get_items_by_name(selector, index)
                else:
                    new_items = self._get_items_by_name(selector)
            elif isinstance(selector, s.Selector):
                new_items = selector._process(self)
            else:
                raise SelectorTypeError("Selectors must of type: str, int, slice or a class from package selectors.")
            if new_items and len(new_items)>0:
                items.extend(new_items)
            elif strict_index:
                raise SelectorError(f"Selector {i} did not return any values. You can set strict_index=False to receive [] instead")
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
        items = self.get_items(selector, _cap = match + 1)
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
        if not isinstance(order, list): raise TypeError("You must provide a list of selectors to reorder the items")
        positions_new = []
        for i, selector in enumerate(order):
            positions_new.append(self._items_ordered.index(self.get_item(selector, strict_index=True)))
        if ( len(positions_new) != len(set(positions_ordered)) != len(self) ):
            raise SelectorError("You must provide a list of all objects by some selector.") from ValueError()
        self._items_ordered = [self._items_ordered[i] for i in order]

    def put_items(self, *selectors, **kwargs):
        position = kwargs.pop("position", None)
        if not position:
            raise ValueError("You must supply a position=")
        if not isinstance(position, int):
            raise TypeError("The position to move to must be an integer, follow array access syntax")
        items = self.get_items(*selectors)
        if not items or len(items) == 0: return
        if position != len(self) and not self._check_index(position):
            raise IndexError("Position must be a valid index")
        for item in reversed(items):
            original_index = self._items_ordered.index(item)
            self._items_ordered[original_index] = None
            self._items_ordered.insert(position, item) # TODO, can it take negatives?
            self._items_ordered.remove(None)

    def move_item(self, *selectors, **kwargs):
        distance = kwargs.pop("distance", None)
        before = kwargs.pop("before", None)
        after = kwargs.pop("after", None)
        reference = None
        if ( (1 if distance else 0) + (1 if before else 0) + (1 if after else 0) ) != 1:
            raise SelectorError("You must set exactly one of value, before, or after.")
        if distance:
            if not isinstance(distance, int):
                raise SelectorError("distance must be an integer (positive or negative)")
        elif before:
            reference = self._items_ordered.index(self.get_item(before, strict_index=True))
        elif after:
            reference = self._items_ordered.index(self.get_item(after, strict_index=True))
        items = self.get_items(*selectors, **kwargs)
        if distance > 0:
            offset = 0
            for item in reversed(items):
                position = min(self._items_ordered.index(item) + distance, len(self))
                if position == len(self): # maintain order
                    position -= offset
                    offset += 1
                self._put_items(item, position)
        elif distance < 0:
            offset = 0
            for item in items:
                position = max(self._items_ordered.index(item) + distance, 0)
                if position == 0:
                    position += offset
                    offset += 1
                self._put_items(item, position)
        elif before:
            position = reference
            for item in reversed(items):
                self._put_items(item, position)
        elif after:
            position = reference+1
            for item in reversed(items):
                self._put_items(item, position)


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

    def _notify_parents(self, **kwargs): # how do we get the return value for this TODO
        map(lambda parent: parent._child_update(self, **kwargs), self._parents_by_id.values())

