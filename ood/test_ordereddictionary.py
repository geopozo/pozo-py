import pytest, random
import pozo.ood.ordereddictionary as od
import pozo.ood.extra_selectors as s
import pozo.ood.exceptions as e

SAMPLE = 1

first_names = [ "thriving", "loving", "eager", "silly", "manufactured", "dumb", "precise", "poingant", "personable", "friendly", "bashful", "timit", "tiny", "relectuant", "fierce", "weird", "ready", "indefatiguable", "dreadful", "trending", "assiduous", "rambunctious", "amicable", "adventurous", "affable", "affectionate", "agreeable", "ambitious",]
middle_names = [ "enormous", "gigantic", "huge", "big", "large", "medium", "average", "typical", "small", "tiny", "microscopic"]
last_names = ["squirrel", "cat", "dog", "mouse", "bug", "mite", "otter", "giraffe", "octopus", "fish", "lion", "tiger", "monkey", "ape", "ant-eater", "dragon", "lizard", "turtle", "parrot", "bird", "parakeet", "owl", "penguin", "pigeon", "dove", "crow", "vulture", "eagle", "hawk"]

def helper_make_names(n = 1):
    ret = {}
    for i in range(n):
        first = first_names[random.randint(0, len(first_names) - 1)]
        middle = middle_names[random.randint(0, len(middle_names) - 1)]
        last = last_names[random.randint(0, len(last_names) - 1)]
        name = first + " " + middle + " " + last
        while name in ret:
            first = first_names[random.randint(0, len(first_names) - 1)]
            middle = middle_names[random.randint(0, len(middle_names) - 1)]
            last = last_names[random.randint(0, len(last_names) - 1)]
            name = first + " " + middle + " " + last
        ret[name] = True
    return list(ret.keys())

class OODChild(od.ObservingOrderedDictionary, od.ChildObserved):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

def assert_od_sane(ood = od.ObservingOrderedDictionary(), num = None):
    i = 0
    for item in ood:
        i += 1
    assert len(ood._items_by_id) == i
    assert len(ood._items_by_id) == len(ood._items_ordered)
    assert len(ood._items_by_id) == ood._count_dictionary()
    assert len(ood._items_by_id) ==  len(ood)
    if num is not None:
        assert len(ood._items_by_id) == num
    for i, item in enumerate(ood):
        assert item == ood._items_ordered[i]

    all_items = {}
    for name in ood._items_by_name:
        for item in name:
            if id(item) in all_items:
                pytest.fail("Dictionary is inconsistent- same item has > 1 name")
                all_items[id(item)] = True

def assert_get_item_equal(parent, *args):
    assert len(args) > 1
    for i, arg in enumerate(args):
        if not i: continue
        try:
            first = parent.get_item(args[i-1], strict_index=True)
        except e.StrictIndexException as err:
            raise IndexError(f" {i-1}th argument didn't work") from err
        try:
            second = parent.get_item(args[i], strict_index=True)
        except e.StrictIndexException as err:
            raise IndexError(f" {i}th argument didn't work") from err
        assert first == second

def assert_child_name(child, name):
    assert child._name == child.get_name() == name

def assert_child_has_parents(child, num, parents = None):
    assert len(child._parents_by_id) == num
    if parents is not None:
        assert num == len(parents)
        for parent in parents:
            assert id(parent) in child._parents_by_id

def test_init_ood():
    ood = od.ObservingOrderedDictionary()
    assert_od_sane(ood, 0)
    assert ood._strict_index is None
    assert ood._name_conflict is None
    assert ood._redundant_add is None

def test_init_child():
    child = od.ChildObserved()
    assert_child_name(child, "unnamed")

    child = od.ChildObserved(name="test")
    assert_child_name(child, "test")

    child.set_name("test2")
    assert_child_name(child, "test2")

def test_init_ood_w_child():
    ood_child = OODChild()
    assert_od_sane(ood_child, 0)
    assert_child_name(ood_child, "unnamed")

    ood_child = OODChild(name="test")
    assert_od_sane(ood_child, 0)
    assert_child_name(ood_child, "test")

def helper_make_items(names):
    ret = []
    if isinstance(names, str):
        names = [names]
    for name in names:
        ret.append(OODChild(name=name))
    return ret

possible_errors = [e.ErrorLevel.IGNORE, e.ErrorLevel.WARN, e.ErrorLevel.ERROR, True, False]

@pytest.mark.parametrize("strict_index", possible_errors)
@pytest.mark.parametrize("name_conflict", possible_errors)
@pytest.mark.parametrize("redundant_add", possible_errors)
def test_add_items_any_config(strict_index, name_conflict, redundant_add):
    parent = helper_make_items("parent")[0]
    parent.set_strict_index(strict_index)   # Testing this here # Not testing global set # Not testing __init__ set
    parent.set_name_conflict(name_conflict) # Testing this here # Not testing global set # Not testing __init__ set
    parent.set_redundant_add(redundant_add) # Testing this here # Not testing global set # Not testing __init__ set
    assert_od_sane(parent, 0)

    names = helper_make_names(68)
    children = helper_make_items(names[:30])
    position_children = helper_make_items(names[30:-8])
    specific_position_children = helper_make_items(names[60:])

    ## Basic Add-Item Several Children
    parent.add_items(*children)
    assert_od_sane(parent, 30)

    for i, child in enumerate(parent._items_ordered):
        assert_child_name(child, children[i].get_name())
        assert_get_item_equal(parent,
                              child,
                              children[i],
                              parent._items_ordered[i],
                              parent._items_by_id[id(children[i])],
                              parent._items_by_name[names[i]][0],
                              parent._items_by_id[id(child)],
                              parent._items_by_name[child.get_name()][0],
                              )
        assert len(child._parents_by_id) == 1
        assert_child_has_parents(child, 1, [parent])
    assert parent._items_ordered == children
    assert sorted(parent._items_by_name.keys()) == sorted(names[0:30])

    ## Add Item At Specific Key Points
    parent.add_items(*specific_position_children[0:2], position=0)
    assert_od_sane(parent, 32)
    assert_get_item_equal(parent, specific_position_children[0], parent._items_ordered[0])
    assert_get_item_equal(parent, specific_position_children[1], parent._items_ordered[1])
    parent.add_items(*specific_position_children[2:4], position=len(parent))
    assert_od_sane(parent, 34)
    assert_get_item_equal(parent, specific_position_children[2], parent._items_ordered[-2])
    assert_get_item_equal(parent, specific_position_children[3], parent._items_ordered[-1])
    parent.add_items(*specific_position_children[4:6], position=-len(parent))
    assert_od_sane(parent, 36)
    assert_get_item_equal(parent, specific_position_children[4], parent._items_ordered[0])
    assert_get_item_equal(parent, specific_position_children[5], parent._items_ordered[1])
    parent.add_items(*specific_position_children[6:], position=-1) #TODO: -1 not appending should be documented
    assert_od_sane(parent, 38)
    assert_get_item_equal(parent, specific_position_children[6], parent._items_ordered[-3])
    assert_get_item_equal(parent, specific_position_children[7], parent._items_ordered[-2])

    ## Add Items At Random Points
    positions_original = []
    positions = []
    for child in position_children:
        new_pos = random.randint(-len(parent), len(parent))
        transformed = new_pos if new_pos >= 0 else len(parent)+new_pos
        positions_original.append(new_pos)
        positions.append(transformed)
        parent.add_items(child, position=new_pos)
        assert_get_item_equal(parent, child, parent._items_ordered[transformed])
    assert_od_sane(parent, 68)
    actual_positions = []
    for i, pos in enumerate(positions):
        for j, pos2 in enumerate(actual_positions):
            if pos2 >= pos:
                actual_positions[j] += 1
        actual_positions.append(pos)

    for pos, child in zip(actual_positions, position_children):
        assert_get_item_equal(parent, child, parent._items_ordered[pos])

    proper_state = parent._items_ordered.copy()
    assert proper_state == parent._items_ordered

    # The following will always fail no matter the configuration

    bad_children = helper_make_items(["no_name", "no_register_parent", "bad position"])
    bad_children[0].get_name = None
    bad_children[1]._register_parent = None
    # bad_children[2] will be added to improper positions

    with pytest.raises(TypeError):
        parent.add_items("ppthhh")
    assert proper_state == parent._items_ordered
    with pytest.raises(TypeError):
        parent.add_items(bad_children[0])
    assert proper_state == parent._items_ordered
    with pytest.raises(TypeError):
        parent.add_items(bad_children[1])
    assert proper_state == parent._items_ordered
    with pytest.raises(IndexError):
        parent.add_items(bad_children[2], position=len(parent) + 1)
    assert proper_state == parent._items_ordered
    with pytest.raises(IndexError):
        parent.add_items(bad_children[2], position="alsdklaskd")
    assert proper_state == parent._items_ordered
    with pytest.raises(IndexError):
        parent.add_items(bad_children[2], position=-len(parent)-1)
    assert proper_state == parent._items_ordered
    with pytest.raises(IndexError):
        parent.add_items(bad_children[2], position=[])
    assert proper_state == parent._items_ordered
    with pytest.raises(IndexError):
        parent.add_items(bad_children[2], position=None)
    assert proper_state == parent._items_ordered

@pytest.mark.parametrize("strict_index", possible_errors)
@pytest.mark.parametrize("name_conflict", possible_errors)
def test_add_item_redundant_add(strict_index, name_conflict):
    child = helper_make_items("One Child")[0]
    second_child = helper_make_items("Child Two")[0]
    third_child = helper_make_items("Child Three")[0]
    parent = helper_make_items("Parent")[0]
    parent.add_items(child)
    assert_od_sane(parent, 1)
    parent.set_redundant_add(e.ErrorLevel.ERROR)
    with pytest.raises(e.RedundantAddException):
        parent.add_items(child)
    assert_od_sane(parent, 1)
    parent.set_redundant_add(e.ErrorLevel.WARN)
    with pytest.warns():
        parent.add_items(child)
    assert_od_sane(parent, 1)
    parent.set_redundant_add(e.ErrorLevel.IGNORE)
    parent.add_items(child)
    assert_od_sane(parent, 1)

    parent.set_redundant_add(e.ErrorLevel.ERROR)
    with pytest.raises(e.RedundantAddException):
        parent.add_items(second_child, second_child)
    assert_od_sane(parent, 1)
    parent.set_redundant_add(e.ErrorLevel.WARN)
    with pytest.warns():
        parent.add_items(second_child, second_child)
    assert_od_sane(parent, 2)
    parent.set_redundant_add(e.ErrorLevel.IGNORE)
    parent.add_items(second_child, second_child)
    assert_od_sane(parent, 2)
    parent.add_items(second_child, second_child, third_child, third_child)
    assert_od_sane(parent, 3)

@pytest.mark.parametrize("strict_index", possible_errors)
@pytest.mark.parametrize("redundant_add", possible_errors)
def test_add_item_name_conflict(strict_index, redundant_add):
    children = helper_make_items(["A", "A", "B"])
    parent = helper_make_items("Parent")[0]
    parent.add_items(children[0])
    assert_od_sane(parent, 1)
    parent.add_items(children[2])
    assert_od_sane(parent, 2)

    ## Trying to add child again
    parent.set_name_conflict(e.ErrorLevel.ERROR)
    with pytest.raises(e.NameConflictException):
        parent.add_items(children[1])
    assert_od_sane(parent, 2)
    parent.set_name_conflict(e.ErrorLevel.WARN)
    with pytest.warns(), pytest.raises(e.NameConflictException):
        parent.add_items(children[1])
    assert_od_sane(parent, 2)
    parent.set_name_conflict(e.ErrorLevel.IGNORE)
    parent.add_items(children[1])
    assert_od_sane(parent, 3)

    ## Trying to add same child twice in one call
    parent = helper_make_items("Parent")[0]
    children = helper_make_items(["A", "A", "B"])
    assert_od_sane(parent, 0)
    parent.set_name_conflict(e.ErrorLevel.ERROR)
    with pytest.raises(e.NameConflictException):
        parent.add_items(*children)
    assert_od_sane(parent, 0)
    parent.set_name_conflict(e.ErrorLevel.WARN)
    with pytest.warns(), pytest.raises(e.NameConflictException):
        parent.add_items(*children)
    assert_od_sane(parent, 0)
    parent.set_name_conflict(e.ErrorLevel.IGNORE)
    parent.add_items(*children)
    assert_od_sane(parent, 3)

def helper_make_selector(parent, child, random=False):
    selectors = []
    if id(child) not in parent._items_by_id:
        selectors=[child, s.Name_I(child.get_name(), 0), len(parent)+2, -len(parent)-2]
    else:
        # Self
        selectors.append(child)

        # Dictionary
        index = parent._items_by_name[child.get_name()].index(child)
        selectors.append(s.Name_I(child.get_name(), index))

        # Position
        selectors.append(parent._items_ordered.index(child))

        # Position Negative
        selectors.append(-(len(parent) - selectors[2]))

    if random:
        return [selectors[random.randint(0, len(selectors)-1)]]
    return selectors

# Need to test slices, need to test names
@pytest.mark.parametrize("name_conflict", possible_errors)
@pytest.mark.parametrize("redundant_add", possible_errors)
def test_get_items(name_conflict, redundant_add):
    parent = helper_make_items("parent")[0]
    parent.set_name_conflict(name_conflict)
    parent.set_redundant_add(redundant_add)
    assert_od_sane(parent, 0)
    names = helper_make_names(600)
    children = helper_make_items(names[:300])
    not_children = helper_make_items(names[300:])
    parent.add_items(*children)
    assert_od_sane(parent, 300)
    assert parent.get_items() == children

    parent.set_strict_index(e.ErrorLevel.ERROR)

    # Ordering and combinging properly
    for n in range(300):
        continue
        for o in range(SAMPLE):
            children_of_interest = []
            for p in range(n):
                if bool(random.getrandbits(1)):
                    children_of_interest.append(children[p])
            if len(children_of_interest) == 0: continue
            selectors = []
            for child in children_of_interest:
                selectors.extend(helper_make_selector(parent, child))
            random.shuffle(selectors)
            items = parent.get_items(*selectors)
            last_pos = -1
            for item in items:
                assert id(item) in parent._items_by_id
                pos= parent._items_ordered.index(item)
                assert pos > last_pos
                last_pos = pos

    # Invalid Types
    invalid_types = [[], object(), 3.120, (), {}]
    for kind in invalid_types:
        with pytest.raises(e.SelectorTypeError):
            parent.get_items(kind)

    # Bad Index
    with pytest.raises(e.StrictIndexException):
        for n in range(300):
            for o in range(SAMPLE):
                children_of_interest = []
                for p in range(n):
                    if bool(random.getrandbits(1)):
                        children_of_interest.append(not_children[p])
                if len(children_of_interest) == 0: continue
                selectors = []
                for child in children_of_interest:
                    selectors.extend(helper_make_selector(parent, child))
                random.shuffle(selectors)
                items = parent.get_items(*selectors)
                last_pos = -1
                for item in items:
                    assert id(item) in parent._items_by_id
                    pos= parent._items_ordered.index(item)
                    assert pos > last_pos
                    last_pos = pos

    # strict index overriden
    for n in range(300):
        for o in range(SAMPLE):
            children_of_interest = []
            for p in range(n):
                if bool(random.getrandbits(1)):
                    children_of_interest.append(not_children[p])
            if len(children_of_interest) == 0: continue
            selectors = []
            for child in children_of_interest:
                selectors.extend(helper_make_selector(parent, child))
            random.shuffle(selectors)
            items = parent.get_items(*selectors, strict_index=False)
            assert items == []

    # Ordering and combinging properly, strict overriden, mixed
    all_possible_children = random.shuffle(children.copy() + not_children.copy())
    for n in range(600):
        continue
        for o in range(SAMPLE):
            children_of_interest = []
            for p in range(n):
                if bool(random.getrandbits(1)):
                    children_of_interest.append(all_possible_children[p])
            if len(children_of_interest) == 0: continue
            selectors = []
            for child in children_of_interest:
                selectors.extend(helper_make_selector(parent, child))
            random.shuffle(selectors)
            with pytest.warns():
                items = parent.get_items(*selectors, strict_index=e.ErrorLevel.WARN)
            last_pos = -1
            for item in items:
                assert id(item) in parent._items_by_id
                assert item not in children
                pos= parent._items_ordered.index(item)
                assert pos > last_pos
                last_pos = pos


# Not my favorite, same as above, just opposite config scheme
@pytest.mark.parametrize("name_conflict", possible_errors)
@pytest.mark.parametrize("redundant_add", possible_errors)
def test_get_items_config_inverted(name_conflict, redundant_add):
    parent = helper_make_items("parent")[0]
    parent.set_name_conflict(name_conflict)
    parent.set_redundant_add(redundant_add)
    assert_od_sane(parent, 0)
    names = helper_make_names(600)
    children = helper_make_items(names[:300])
    not_children = helper_make_items(names[300:])
    parent.add_items(*children)
    assert_od_sane(parent, 300)
    assert parent.get_items() == children

    parent.set_strict_index(e.ErrorLevel.IGNORE)

    # Ordering and combinging properly
    for n in range(300):
        continue
        for o in range(SAMPLE):
            children_of_interest = []
            for p in range(n):
                if bool(random.getrandbits(1)):
                    children_of_interest.append(children[p])
            if len(children_of_interest) == 0: continue
            selectors = []
            for child in children_of_interest:
                selectors.extend(helper_make_selector(parent, child))
            random.shuffle(selectors)
            items = parent.get_items(*selectors)
            last_pos = -1
            for item in items:
                assert id(item) in parent._items_by_id
                pos= parent._items_ordered.index(item)
                assert pos > last_pos
                last_pos = pos

    # Invalid Types
    invalid_types = [[], object(), 3.120, (), {}]
    for kind in invalid_types:
        with pytest.raises(e.SelectorTypeError):
            parent.get_items(kind)

    # Bad Index
    with pytest.raises(e.StrictIndexException):
        for n in range(300):
            for o in range(SAMPLE):
                children_of_interest = []
                for p in range(n):
                    if bool(random.getrandbits(1)):
                        children_of_interest.append(not_children[p])
                if len(children_of_interest) == 0: continue
                selectors = []
                for child in children_of_interest:
                    selectors.extend(helper_make_selector(parent, child))
                random.shuffle(selectors)
                items = parent.get_items(*selectors, strict_index=True)
                last_pos = -1
                for item in items:
                    assert id(item) in parent._items_by_id
                    pos= parent._items_ordered.index(item)
                    assert pos > last_pos
                    last_pos = pos

    # strict index (not) overriden
    for n in range(300):
        for o in range(SAMPLE):
            children_of_interest = []
            for p in range(n):
                if bool(random.getrandbits(1)):
                    children_of_interest.append(not_children[p])
            if len(children_of_interest) == 0: continue
            selectors = []
            for child in children_of_interest:
                selectors.extend(helper_make_selector(parent, child))
            random.shuffle(selectors)
            items = parent.get_items(*selectors)
            assert items == []

    # Ordering and combinging properly, strict overriden, mixed
    all_possible_children = random.shuffle(children.copy() + not_children.copy())
    for n in range(600):
        continue
        for o in range(SAMPLE):
            children_of_interest = []
            for p in range(n):
                if bool(random.getrandbits(1)):
                    children_of_interest.append(all_possible_children[p])
            if len(children_of_interest) == 0: continue
            selectors = []
            for child in children_of_interest:
                selectors.extend(helper_make_selector(parent, child))
            random.shuffle(selectors)
            with pytest.warns():
                items = parent.get_items(*selectors, strict_index=e.ErrorLevel.WARN)
            last_pos = -1
            for item in items:
                assert id(item) in parent._items_by_id
                assert item not in children
                pos= parent._items_ordered.index(item)
                assert pos > last_pos
                last_pos = pos



# Fix insert in move
# Test Name Changing On 

# TODO:
# get_item
# has_item
# pop
# move

# How to make sure multi_parent does what it's supposed to
# Write Tests for Selectors
# Write a scramble function() which supposedly does nothing to a dictionary but uses a lot of functions


def test_user_simulation():
    # add_items
    e.StrictIndexException.default_level = True
    e.NameConflictException.default_level = False
    e.MultiParentException.default_level = False
    e.RedundantAddException.default_level = e.ErrorLevel.ERROR
    parents = [OODChild(name="Alphabet Parent"), OODChild(name="Alphabet Parent2"), OODChild(name="Alphabet Parent2")]
    children = [OODChild(name="A"), OODChild(name="B"), OODChild(name="C")]

    parents[0].add_items(children[0])
    assert id(children[0]) in parents[0]._items_by_id
    assert_od_sane(parents[0], 1)
    assert_child_has_parents(children[0], 1, [parents[0]])
    assert parents[0].has_item("A")
    assert parents[0].has_item(children[0].get_name())
    assert parents[0].has_item(children[0])

    parents[0].add_items(children[1], children[2])
    assert_od_sane(parents[0], 3)
    for child in children:
        assert_child_has_parents(child, 1, [parents[0]])

    parents[1].add_items(*children)
    assert_od_sane(parents[1], 3)
    for child in children:
        assert_child_has_parents(child, 2, [parents[0], parents[1]])

    parents[2].add_items(children[0])
    assert_od_sane(parents[2], 1)
    for i, child in enumerate(children):
        if not i:
            assert_child_has_parents(child, 3, [parents[0], parents[1], parents[2]])
        else:
            assert_child_has_parents(child, 2, [parents[0], parents[1]])

    with pytest.raises(e.RedundantAddException):
        assert len(parents[0]) == 3
        assert parents[0].has_item(children[0])
        parents[0].add_items(*children)
    with pytest.raises(e.RedundantAddException):
        parents[1].add_items(children[0])
    with pytest.raises(e.RedundantAddException):
        parents[2].add_items(children[0])

    assert_od_sane(parents[0], 3)
    assert_od_sane(parents[1], 3)
    assert_od_sane(parents[2], 1)
    for i, child in enumerate(children):
        if not i:
            assert_child_has_parents(child, 3, [parents[0], parents[1], parents[2]])
        else:
            assert_child_has_parents(child, 2, [parents[0], parents[1]])

    with pytest.raises(e.RedundantAddException):
        parents[2].add_items(children[2], children[0])

    assert_od_sane(parents[2], 1)
    for i, child in enumerate(children):
        if not i:
            assert_child_has_parents(child, 3, [parents[0], parents[1], parents[2]])
        else:
            assert_child_has_parents(child, 2, [parents[0], parents[1]])

    # test _check index
    assert not parents[1]._check_index(-1 * len(parents[1]) -1)
    assert not parents[1]._check_index(10)
    assert not parents[1]._check_index(len(parents[1])+1)
    assert not parents[1]._check_index(slice(1,10))
    assert parents[1]._check_index(0)
    assert parents[1]._check_index(1)
    assert parents[1]._check_index(2)
    assert parents[1]._check_index(slice(0, 3))
    assert not parents[1]._check_index(None)

    # _check_key

    assert not parents[0]._check_key("")
    assert not parents[2]._check_key("B")
    assert parents[0]._check_key("A")
    assert parents[0]._check_key("B")
    assert parents[0]._check_key("C")
    assert parents[2]._check_key("A")

    # do _items_by_name
    assert children[0] == parents[0]._get_items_by_name("A")[0]
    assert children[1] == parents[0]._get_items_by_name("B")[0]
    assert children[2] == parents[0]._get_items_by_name("C")[0]
    assert len(parents[0]._get_items_by_name("A")) == 1
    assert len(parents[0]._get_items_by_name("B")) == 1
    assert len(parents[0]._get_items_by_name("C")) == 1

    clone_child = OODChild(name="A")
    parents[0].add_items(clone_child)
    assert_od_sane(parents[0], 4)
    assert len(parents[0]._get_items_by_name("A")) == 2
    assert len(parents[0]._get_items_by_name("B")) == 1
    assert len(parents[0]._get_items_by_name("C")) == 1
    assert children[0] == parents[0]._get_items_by_name("A")[0]
    assert clone_child == parents[0]._get_items_by_name("A")[1]
    assert parents[0].get_items("A", 1) == [children[0], children[1], clone_child]

    # get items by slice
    assert len(parents[0]._get_items_by_slice(slice(None))) == len(parents[0]) == 4
    assert parents[0]._get_items_by_slice(slice(1, 2)) == children[1:2]

    # get item by index
    assert parents[0]._get_item_by_index(0) == children[0]

    # get items
    assert len(parents[0].get_items()) == 4
    assert parents[0].get_items() == children + [clone_child]
    assert parents[0].get_items("A", 1) == [children[0], children[1], clone_child]
    sel = s.Name_I("A", 1)
    assert isinstance(sel, s.Selector)
    result = parents[0].get_items(s.Name_I("A", 1))
    assert clone_child == parents[0].get_items(s.Name_I("A", 1))[0]
    assert children[0] == parents[0].get_items(s.Name_I("A", 0))[0]
    assert len(parents[0].get_items(s.Name_I("A", slice(None)))) == 2
    # assert clone_child == parents[0]._get_items_by_name(s.Name_I("A", slice(None,-1)))
    # So it turns out negatives aren't an implicit feature of slicing like I thought
    # We'd have to support them (or allow them through the checker?)

    # testing strict_index
    with pytest.raises(e.StrictIndexException):
        parents[0].get_items("E")
        parents[0].get_items(200)
        parents[0].get_items(slice(1000, 1010))
        parents[0].get_items(s.Name_I("E", 10))
        parents[0].get_items(s.Name_I("A", 10))
    parents[0].set_strict_index(False)
    assert parents[0].get_items("E") == []
    assert parents[0].get_items(200) == []
    assert parents[0].get_items(slice(1000, 1010)) == []
    assert parents[0].get_items(s.Name_I("E", 10)) == []
    assert parents[0].get_items(s.Name_I("A", 10)) == []
    with pytest.raises(e.StrictIndexException):
        parents[0].get_items("E", strict_index=True)
        parents[0].get_items(200, strict_index=True)
        parents[0].get_items(slice(1000, 1010), strict_index=True)
        parents[0].get_items(s.Name_I("E", 10), strict_index=True)
        parents[0].get_items(s.Name_I("A", 10), strict_index=True)
    parents[0].set_strict_index(True)
    with pytest.raises(e.StrictIndexException):
        parents[0].get_items("E")
        parents[0].get_items(200)
        parents[0].get_items(slice(1000, 1010))
        parents[0].get_items(s.Name_I("E", 10))
        parents[0].get_items(s.Name_I("A", 10))
    assert parents[0].get_items("E", strict_index=False) == []
    assert parents[0].get_items(200, strict_index=False) == []
    assert parents[0].get_items(slice(1000, 1010), strict_index=False) == []
    assert parents[0].get_items(s.Name_I("E", 10), strict_index=False) == []
    assert parents[0].get_items(s.Name_I("A", 10), strict_index=False) == []
    assert parents[2].get_items(children[2], strict_index=False) == []

    assert parents[0].get_items("A", s.Name_I("A", 0), s.Name_I("AA", 100), 1, strict_index=False) == [children[0], children[1], clone_child]

    # testing type errors
    with pytest.raises(e.SelectorTypeError):
        parents[0].get_items(200.0)
        parents[0].get_items(parents)
        parents[0].get_items[{}]
        parents[0].get_items((1,2,3))
        parents[0].get_items(s.Name_I(1, 2))
        parents[0].get_items(s.Name_I(1, "a"))
        parents[0].get_items(s.Name_I("a", "a"))

    # testing get_item()

    assert parents[0].get_item("A") == children[0]
    assert parents[0].get_item(1) == children[1]
    assert not parents[0].get_item("alsdklaksd", strict_index=False)
    assert not parents[0].get_item("A", match=2, strict_index=False)
    assert parents[0].get_item("A", match=1) == clone_child
    assert parents[0].get_item(s.Name_I("A", 1)) == clone_child

    with pytest.raises(e.SelectorTypeError):
        parents[0].get_item(200.0)
        parents[0].get_item(parents)
        parents[0].get_item({})
        parents[0].get_item((1,2,3))
        parents[0].get_item(s.Name_I(1, 2))
        parents[0].get_item(s.Name_I(1, "a"))
        parents[0].get_item(s.Name_I("a", "a"))

    with pytest.raises(e.StrictIndexException):
        parents[0].get_item("E")
        parents[0].get_item(200)
        parents[0].get_item(slice(1000, 1010))
        parents[0].get_item(s.Name_I("E", 10))
        parents[0].get_item(s.Name_I("A", 10))

    parents[0].set_strict_index(False)
    assert parents[0].get_item("E") == None
    assert parents[0].get_item(200) == None
    assert parents[0].get_item(slice(1000, 1010)) == None
    assert parents[0].get_item(s.Name_I("E", 10)) == None
    assert parents[0].get_item(s.Name_I("A", 10)) == None
    parents[0].set_strict_index(True)


    assert parents[0].has_item("E") == False
    assert parents[0].has_item(200) == False
    assert parents[0].has_item(slice(1000, 1010)) == False
    assert parents[0].has_item(s.Name_I("E", 10)) == False
    assert parents[0].has_item(s.Name_I("A", 10)) == False
    with pytest.raises(e.SelectorTypeError):
        assert parents[0].has_item(200.0) == False
        assert parents[0].has_item(parents) == False
        assert parents[0].has_item({}) == False
        assert parents[0].has_item((1,2,3)) == False
    #assert parents[0].has_item(s.Name_I(1, 2)) == False
    #assert parents[0].has_item(s.Name_I(1, "a")) == False
    #assert parents[0].has_item(s.Name_I("a", "a")) == False

    assert parents[0].has_item("A")  == True
    assert parents[0].has_item(1) == True
    assert parents[0].has_item(s.Name_I("A", 1)) == True

    alphabet = "abcdefghijklmnopqrstuvwxyz"
    layer1, layer2, layer3 = [], [], []
    for letter in alphabet:
        layer1.append(OODChild(name = letter))
        layer2.append(OODChild(name = letter))
        layer3.append(OODChild(name = letter))

    layer1[0].add_items(*layer2)
    assert_od_sane(layer1[0], len(alphabet))
    for child in layer1[0]:
        assert isinstance(child, OODChild)
        assert_od_sane(child, 0)

    for letter, child in zip(alphabet, layer1[0]):
        assert child.get_name() == letter

    layer1[1].add_items(*reversed(layer2))

    for letter, child in zip(reversed(alphabet), layer1[1]):
        assert child.get_name() == letter

    assert layer1[1].get_items() == list(reversed(layer2))
    assert layer1[0].get_items() == layer2

    layer1[1].reorder_all_items(list(alphabet))
    assert layer1[1].get_items() == layer2

    import random
    layer1[0].reorder_all_items(list(alphabet))
    reorder = random.sample(range(0, len(alphabet)), len(alphabet))
    layer1[0].reorder_all_items(reorder)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == alphabet[reorder[i]]

    for __i in range(0, 200):
        layer1[0].reorder_all_items(list(alphabet))
        reorder = random.sample(range(0, len(alphabet)), len(alphabet))
        layer1[0].reorder_all_items(reorder)
        for i, child in enumerate(layer1[0]):
            assert child.get_name() == alphabet[reorder[i]]

    for __i in range(0, 200):
        reorder = random.sample(alphabet, len(alphabet))
        layer1[0].reorder_all_items(reorder)
        layer1[1].reorder_all_items(reorder)
        for i, child in enumerate(layer1[0]):
            assert child.get_name() == reorder[i]
        assert layer1[0].get_items() == layer1[1].get_items()
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2
    with pytest.raises(TypeError):
        layer1[0].reorder_all_items(1)
    assert layer1[0].get_items() == layer2
    assert len(layer1[0]) == len(alphabet) == len("abcdefghijklmnopqrstuvwxyz")
    with pytest.raises(e.SelectorError):
        layer1[0].reorder_all_items([1, 2, 3, 4])
    assert layer1[0].get_items() == layer2
    with pytest.raises(e.SelectorError):
        layer1[0].reorder_all_items(list(alphabet + alphabet))
    assert layer1[0].get_items() == layer2
    with pytest.raises((e.SelectorError, e.StrictIndexException)):
        layer1[0].reorder_all_items(["othhh"] + list(alphabet)[1:])
    assert layer1[0].get_items() == layer2
    with pytest.raises(e.SelectorTypeError):
        layer1[0].reorder_all_items([[]])
    assert layer1[0].get_items() == layer2

    #move_items
    goal1 = "bcdefghijklamnopqrstuvwxyz"
    layer1[0].move_items("a", after="l")
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal1[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items("a", before="m")
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal1[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items("a", position=12)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal1[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items("a", distance=+11)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal1[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("bcdefghijkl"), position=0)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal1[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("bcdefghijkl"), before="a")
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal1[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("bcdefghijkl"), distance=-1) #TODO what happens if we move multiples a distance
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal1[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("bcdefghijkl"), distance=-10) #TODO what happens if we move multiples a distance
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal1[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    goal2 = "abcdefghijklzmnopqrstuvwxy" # move "ab" to 26, move "ab" after z, move "ab" + 24 or more move "c-z" to position 0, before a

    layer1[0].move_items("z", after="l")
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal2[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items("z", before="m")
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal2[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items("z", position=12)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal2[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items("z", distance=-13)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal2[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("mnopqrstuvwxy"), position=len(alphabet)) # this means append, but we want it in order
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal2[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("mnopqrstuvwxy"), after="z")
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal2[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("mnopqrstuvwxy"), distance=+1)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal2[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("mnopqrstuvwxy"), distance=+10)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal2[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2


    goal3 = "cdefghijklmnopqrstuvwxyzab" # move "ab" to 26, move "ab" after z, move "ab" + 24 or more move "c-z" to position 0, before a
    layer1[0].move_items(*list("ab"), position=26)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal3[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("ab"), after='z')
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal3[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("ab"), distance=25)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal3[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("ab"), distance=10000)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal3[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("cdefghijklmnopqrstuvwxyz"), position=0)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal3[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("cdefghijklmnopqrstuvwxyz"), before='a')
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal3[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("cdefghijklmnopqrstuvwxyz"), distance=-2)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal3[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    layer1[0].move_items(*list("cdefghijklmnopqrstuvwxyz"), distance=-26)
    for i, child in enumerate(layer1[0]):
        assert child.get_name() == goal3[i]
    layer1[0].reorder_all_items(list(alphabet))
    assert layer1[0].get_items() == layer2

    num_children_old = len(parents[0])
    num_parents_old = len(clone_child._parents_by_id)
    popped = parents[0].pop_items(s.Name_I("A", 1))
    assert len(parents[0]) == num_children_old-1
    assert parents[0] not in clone_child._parents_by_id
    assert len(clone_child._parents_by_id) == num_parents_old - 1
    assert popped == [clone_child]
    assert_od_sane(parents[0], 3)

    parents[1].add_items(clone_child, position=0)
    assert_od_sane(parents[1], 4)
    assert len(parents[1]._get_items_by_name("A")) == 2
    assert len(parents[1]._get_items_by_name("B")) == 1
    assert len(parents[1]._get_items_by_name("C")) == 1
    assert children[0] == parents[1]._get_items_by_name("A")[0]
    assert clone_child == parents[1]._get_items_by_name("A")[1]
    assert parents[1].get_items("A", 1) == [clone_child, children[0]]
    assert parents[1].get_items("A", 2) == [clone_child, children[0], children[1]]
    parents[1].pop_items(*children)
    assert parents[1].get_items() == [clone_child]

    layer1[2].set_strict_index(False)
    layer1[2].add_items(*layer2)
    for i, child in enumerate(layer1[2]):
        child.add_items(layer3[0], layer3[i%2+1])
        assert_od_sane(child, 2)
    assert layer1[2].get_items(s.Has_Children(layer2[0])) == []
    assert layer1[2].get_items(s.Has_Children(layer2[2])) == []
    assert layer1[2].get_items(s.Has_Children(layer3[0])) == layer2
    assert layer1[2].get_items(s.Has_Children(layer3[1], layer3[2])) == layer2
    assert layer1[2].get_items(s.Has_Children(layer3[1], layer3[2])) == layer2
    assert len(layer1[2].get_items(s.Has_Children(layer3[1]))) == len(layer2)/2
    assert len(layer1[2].get_items(s.Has_Children(layer3[2]))) == len(layer2)/2

    assert layer1[2].get_item("a") == layer2[0]
    assert layer1[2].has_item("a")
    #assert layer1[2]._allow_name_conflicts
    assert layer2[0].get_name() == "a"
    layer2[0].set_name("ABC")
    assert layer2[0].get_name() == "ABC"
    assert layer1[2].has_item(layer2[0])
    assert layer1[2].has_item("ABC")
    assert not layer1[2].has_item("a")
    layer2[0].set_name("b")
    assert layer2[0].get_name() == "b"
    assert layer1[2].has_item(layer2[0])
    assert len(layer1[2].get_items("b")) == 2
    assert not layer1[2].has_item("ABC")
    strict_parent = OODChild(name="stricty", name_conflict=True)
    assert_od_sane(strict_parent, 0)
    assert layer2[1].get_name() == "b"
    assert layer2[2].get_name() == "c"
    strict_parent.add_items(layer2[1], layer2[2])
    assert layer2[0].get_name() == layer2[1].get_name()
    with pytest.raises(e.NameConflictException):
        strict_parent.add_items(layer2[0])
    with pytest.raises(e.NameConflictException):
        layer2[2].set_name("b")
    assert layer2[2].get_name() == "c"
    for parent in layer2[2]._get_parents():
        assert len(parent.get_items(layer2[2].get_name())) == 1
        assert parent.get_item(layer2[2]) == parent.get_item(layer2[2].get_name())
    for parent in layer1[0:3]:
        assert parent in layer2[2]._get_parents()
    assert strict_parent.get_name() == "stricty"
    assert strict_parent in layer2[2]._get_parents()

    with pytest.raises(e.NameConflictException):
        strict_parent.add_items(layer3[0], layer3[1], layer3[2])
    assert len(strict_parent) == 2
    with pytest.raises(TypeError):
        OODChild(name=3)
    one_parent_child = OODChild(name="one_parent", multi_parent=True)
    layer1[0].add_items(one_parent_child)
    with pytest.raises(Exception):
        layer1[1].add_items(one_parent_child)
    assert one_parent_child._get_parents() == [layer1[0]]
