import pytest
import ordereddictionary as od
from ordereddictionary import ObservingOrderedDictionary as OOD

def assert_ood_sane(ood = OOD()):
    assert len(ood._items_by_id) == len(ood._items_by_name) == ood._count_dictionary()
    return ood._count_dictionary()

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
    assert assert_ood_sane(ood_child) == 0
    assert_child_name(ood_child, "")

    ood_child = OODChild(name="test")
    assert assert_ood_sane(ood_child) == 0
    assert_child_name(ood_child, "test")

    ## Unit tests

    # test key_I with correct values and instances of bad values
    # with pytest.raises(SelectorTypeError)


    ## Fuzzy Use Tests (randomly add, remove, and rename, check has, get, get_items w/ several different configurations, completely, and with random )
    child_names = ["child1", "child2", "child3", "child4"]
    oods = []
    for name in child_names:
        oods.append(OODChild(name=name))
    for i, ood in enumerate(oods):
        assert assert_ood_sane(ood) == 0
        assert_child_name(ood, child_names[i])

    clones = []
    for i in range(0, 5):
        clones.append(OODChild(name="clone"))

    parents = [ OOD(), OODChild() ]

    for parent in parents:
        parent.add_items(oods[0])
        assert assert_ood_sane(parent) == 1
        # should be testing get_items first
        assert parent.has_item(oods[0])
        assert parent.has_item(0)
        assert parent.has_item("child1")
        assert parent.has_item(slice(None))
        assert_get_item_equal(parent, 0, "child1", slice(None), od.Key_I("child1", 0))

        #with pytest.raises(TypeError): # test errors as well w/ has item
        # Remove one child
        # Add 3 children
        # Remove two children
        # Add a new child
        # Change its name
        # Try to remove its old name
        # Try to remove its new name

        # Add the clones
