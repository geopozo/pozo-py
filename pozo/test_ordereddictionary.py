import pytest
import pozo.extra_selectors as s
import pozo.ordereddictionary as od
from pozo.exceptions import SelectorTypeError, SelectorError
from pozo.ordereddictionary import ObservingOrderedDictionary as OOD

def assert_ood_sane(ood = OOD(), num = None):
    i = 0
    for item in ood:
        i += 1
    assert len(ood._items_by_id) == len(ood._items_ordered)
    assert len(ood._items_by_id) == ood._count_dictionary()
    assert len(ood._items_by_id) ==  len(ood)
    if num is not None:
        assert len(ood._items_by_id) == num

def assert_child_has_parents(child, num, parents = None):
    assert len(child._parents_by_id) == num
    if parents is not None:
        assert num == len(parents)
        for parent in parents:
            assert id(parent) in child._parents_by_id

def test_init_ood():
    ood = OOD()
    assert_ood_sane(ood)


def assert_child_name(child, name):
    assert child._name == child.get_name() == name

def test_init_child():
    child = od.ChildObserved()
    assert_child_name(child, "")

    child = od.ChildObserved(name="test")
    assert_child_name(child, "test")

    child.set_name("test2")
    assert_child_name(child, "test2")

def assert_get_item_equal(parent, *args):
    assert len(args) > 1
    for i, arg in enumerate(args): # no zip here!
        if not i: continue
        assert parent.get_item(args[i-1]) == parent.get_item(args[i])

def test_init_ood_w_child():
    class OODChild(OOD, od.ChildObserved):
        def __init__(self, *args, **kwargs):
            super().__init__(**kwargs)

    ## Test basic initialization
    ood_child = OODChild()
    assert_ood_sane(ood_child, 0)
    assert_child_name(ood_child, "")

    ood_child = OODChild(name="test")
    assert_ood_sane(ood_child, 0)
    assert_child_name(ood_child, "test")

    ## Unit tests

    # test these elsewhere (these are selectors)
    # test key_I with correct values and instances of bad values
    # with pytest.raises(SelectorTypeError)

    # add_items
    children = [OODChild(name="A"), OODChild(name="B"), OODChild(name="C")]
    parents = [OODChild(name="Alphabet Parent"), OODChild(name="Alphabet Parent2"), OODChild(name="Alphabet Parent2")]
    for child in children:
        assert_ood_sane(child, 0)
    for parent in parents:
        assert_ood_sane(parent, 0)

    parents[0].add_items(children[0])
    assert_ood_sane(parents[0], 1)
    assert_child_has_parents(children[0], 1, [parents[0]])

    parents[0].add_items(children[1], children[2])
    assert_ood_sane(parents[0], 3)
    for child in children:
        assert_child_has_parents(child, 1, [parents[0]])

    parents[1].add_items(*children)
    assert_ood_sane(parents[1], 3)
    for child in children:
        assert_child_has_parents(child, 2, [parents[0], parents[1]])

    parents[2].add_items(children[0])
    assert_ood_sane(parents[2], 1)
    for i, child in enumerate(children):
        if not i:
            assert_child_has_parents(child, 3, [parents[0], parents[1], parents[2]])
        else:
            assert_child_has_parents(child, 2, [parents[0], parents[1]])

    with pytest.raises(ValueError):
        parents[0].add_items(*children)
        parents[1].add_items(children[0])
        parents[2].add_items(children[0])

    assert_ood_sane(parents[0], 3)
    assert_ood_sane(parents[1], 3)
    assert_ood_sane(parents[2], 1)
    for i, child in enumerate(children):
        if not i:
            assert_child_has_parents(child, 3, [parents[0], parents[1], parents[2]])
        else:
            assert_child_has_parents(child, 2, [parents[0], parents[1]])

    with pytest.raises(ValueError):
        parents[2].add_items(children[2], children[0])

    assert_ood_sane(parents[2], 1)
    for i, child in enumerate(children):
        if not i:
            assert_child_has_parents(child, 3, [parents[0], parents[1], parents[2]])
        else:
            assert_child_has_parents(child, 2, [parents[0], parents[1]])

    # test _enforce index
    with pytest.raises(SelectorError):
        parents[1]._enforce_index(-1)
        parents[1]._enforce_index(10)
        parents[1]._enforce_index(len(parents[1]))
        parents[1]._enforce_index(slice(1,10))
    parents[1]._enforce_index(0)
    parents[1]._enforce_index(1)
    parents[1]._enforce_index(2)
    parents[1]._enforce_index(slice(0, 3))
    parents[1]._enforce_index(None)

    # _enforce_key

    with pytest.raises(SelectorError):
        parents[0]._enforce_key("")
        parents[2]._enforce_key("B")
    parents[0]._enforce_key("A")
    parents[0]._enforce_key("B")
    parents[0]._enforce_key("C")
    parents[2]._enforce_key("A")

    # do _items_by_name
    assert children[0] == parents[0]._get_items_by_name("A")[0]
    assert children[1] == parents[0]._get_items_by_name("B")[0]
    assert children[2] == parents[0]._get_items_by_name("C")[0]
    assert len(parents[0]._get_items_by_name("A")) == 1
    assert len(parents[0]._get_items_by_name("B")) == 1
    assert len(parents[0]._get_items_by_name("C")) == 1

    clone_child = OODChild(name="A")
    parents[0].add_items(clone_child)
    assert_ood_sane(parents[0], 4)
    assert len(parents[0]._get_items_by_name("A")) == 2
    assert len(parents[0]._get_items_by_name("B")) == 1
    assert len(parents[0]._get_items_by_name("C")) == 1
    assert children[0] == parents[0]._get_items_by_name("A")[0]
    assert clone_child == parents[0]._get_items_by_name("A")[1]
    assert clone_child == parents[0]._get_items_by_name(s.Key_I("A", 1))[0]
    assert children[0] == parents[0]._get_items_by_name(s.Key_I("A", 0))[0]
    assert len(parents[0]._get_items_by_name(s.Key_I("A", slice(None)))) == 2
    # assert clone_child == parents[0]._get_items_by_name(s.Key_I("A", slice(None,-1)))
    # So it turns out negatives aren't an implicit feature of slicing like I thought
    # We'd have to support them (or allow them through the checker?)

    # get items by slice
    assert len(parents[0]._get_items_by_slice(slice(None))) == len(parents[0]) == 4
    assert parents[0]._get_items_by_slice(slice(1, 2)) == children[1:2]

    # get item by index
    assert parents[0]._get_item_by_index(0) == children[0]

    # get items
    assert len(parents[0].get_items()) == 4
    assert parents[0].get_items("A", 1) == [children[0], children[1], clone_child] 
    # okay, so _by_id can store the object number, not just the object, no need, we already have it.
    # then we can grab their position
    # Yeah, we have to do that and deep copy (copy your children and then reattach them, if you're being copied)
    # We need to test sorting + strict

    # swap (gotta test gts first)

    # reorder (gotta test gets first)
    # test list too small
    # test list too big
    # test list just right

    # test has_item gotta do gets first


    ## Fuzzy Use Tests (randomly add, remove, and rename, check has, get, get_items w/ several different configurations, completely, and with random )
    child_names = ["child1", "child2", "child3", "child4"]
    oods = []
    for name in child_names:
        oods.append(OODChild(name=name))
    for i, ood in enumerate(oods):
        assert_ood_sane(ood, 0)
        assert_child_name(ood, child_names[i])

    clones = []
    for i in range(0, 5):
        clones.append(OODChild(name="clone"))

    parents = [ OOD(), OODChild() ]

    for parent in parents:
        parent.add_items(oods[0])
        assert_ood_sane(parent, 1)
        # should be testing get_items first
        assert parent.has_item(oods[0])
        assert parent.has_item(0)
        assert parent.has_item("child1")
        assert parent.has_item(slice(None))
        assert_get_item_equal(parent, 0, "child1", slice(None), s.Key_I("child1", 0))

        #with pytest.raises(TypeError): # test errors as well w/ has item
        # Remove one child
        # Add 3 children
        # Remove two children
        # Add a new child
        # Change its name
        # Try to remove its old name
        # Try to remove its new name

        # Add the clones
