import pytest
import pozo.ood.ordereddictionary as od
import pozo.ood.extra_selectors as s
from pozo.ood.exceptions import SelectorTypeError, SelectorError

class OODChild(od.ObservingOrderedDictionary, od.ChildObserved):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

def assert_ood_sane(ood = od.ObservingOrderedDictionary(), num = None):
    i = 0
    for item in ood:
        i += 1
    assert len(ood._items_by_id) == i
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
    ood = od.ObservingOrderedDictionary()
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
    ## Test basic initialization
    ood_child = OODChild()
    assert_ood_sane(ood_child, 0)
    assert_child_name(ood_child, "")

    ood_child = OODChild(name="test")
    assert_ood_sane(ood_child, 0)
    assert_child_name(ood_child, "test")


    # add_items
    od.strict_index = True
    children = [OODChild(name="A"), OODChild(name="B"), OODChild(name="C")]
    parents = [OODChild(name="Alphabet Parent"), OODChild(name="Alphabet Parent2"), OODChild(name="Alphabet Parent2")]
    for child in children:
        assert_ood_sane(child, 0)
    for parent in parents:
        assert_ood_sane(parent, 0)

    parents[0].add_items(children[0])
    assert id(children[0]) in parents[0]._items_by_id
    assert_ood_sane(parents[0], 1)
    assert_child_has_parents(children[0], 1, [parents[0]])
    assert parents[0].has_item("A")
    assert parents[0].has_item(children[0].get_name())
    assert parents[0].has_item(children[0])

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
        assert len(parents[0]) == 3
        assert parents[0].has_item(children[0])
        parents[0].add_items(*children)
    with pytest.raises(ValueError):
        parents[1].add_items(children[0])
    with pytest.raises(ValueError):
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

    # test _check index
    assert not parents[1]._check_index(-1)
    assert not parents[1]._check_index(10)
    assert not parents[1]._check_index(len(parents[1]))
    assert not parents[1]._check_index(slice(1,10))
    assert parents[1]._check_index(0)
    assert parents[1]._check_index(1)
    assert parents[1]._check_index(2)
    assert parents[1]._check_index(slice(0, 3))
    assert parents[1]._check_index(None)

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
    assert_ood_sane(parents[0], 4)
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
    with pytest.raises(SelectorError):
        parents[0].get_items("E")
        parents[0].get_items(200)
        parents[0].get_items(slice(1000, 1010))
        parents[0].get_items(s.Name_I("E", 10))
        parents[0].get_items(s.Name_I("A", 10))
    parents[0].unset_strict()
    assert parents[0].get_items("E") == []
    assert parents[0].get_items(200) == []
    assert parents[0].get_items(slice(1000, 1010)) == []
    assert parents[0].get_items(s.Name_I("E", 10)) == []
    assert parents[0].get_items(s.Name_I("A", 10)) == []
    with pytest.raises(SelectorError):
        parents[0].get_items("E", strict_index=True)
        parents[0].get_items(200, strict_index=True)
        parents[0].get_items(slice(1000, 1010), strict_index=True)
        parents[0].get_items(s.Name_I("E", 10), strict_index=True)
        parents[0].get_items(s.Name_I("A", 10), strict_index=True)
    parents[0].set_strict()
    with pytest.raises(SelectorError):
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
    with pytest.raises(SelectorTypeError):
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
    assert parents[0].get_item(s.Name_I("A", 1)) == clone_child

    with pytest.raises(SelectorTypeError):
        parents[0].get_item(200.0)
        parents[0].get_item(parents)
        parents[0].get_item({})
        parents[0].get_item((1,2,3))
        parents[0].get_item(s.Name_I(1, 2))
        parents[0].get_item(s.Name_I(1, "a"))
        parents[0].get_item(s.Name_I("a", "a"))

    with pytest.raises(SelectorError):
        parents[0].get_item("E")
        parents[0].get_item(200)
        parents[0].get_item(slice(1000, 1010))
        parents[0].get_item(s.Name_I("E", 10))
        parents[0].get_item(s.Name_I("A", 10))

    parents[0].unset_strict()
    assert parents[0].get_item("E") == None
    assert parents[0].get_item(200) == None
    assert parents[0].get_item(slice(1000, 1010)) == None
    assert parents[0].get_item(s.Name_I("E", 10)) == None
    assert parents[0].get_item(s.Name_I("A", 10)) == None
    parents[0].set_strict()


    assert parents[0].has_item("E") == False
    assert parents[0].has_item(200) == False
    assert parents[0].has_item(slice(1000, 1010)) == False
    assert parents[0].has_item(s.Name_I("E", 10)) == False
    assert parents[0].has_item(s.Name_I("A", 10)) == False
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
    assert_ood_sane(layer1[0], len(alphabet))
    for child in layer1[0]:
        assert isinstance(child, OODChild)
        assert_ood_sane(child, 0)

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
    with pytest.raises(SelectorError):
        layer1[0].reorder_all_items([1, 2, 3, 4])
    assert layer1[0].get_items() == layer2
    with pytest.raises(SelectorError):
        layer1[0].reorder_all_items(list(alphabet + alphabet))
    assert layer1[0].get_items() == layer2
    with pytest.raises(SelectorError):
        layer1[0].reorder_all_items(["othhh"] + list(alphabet)[1:])
    assert layer1[0].get_items() == layer2
    with pytest.raises(SelectorTypeError):
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
    assert_ood_sane(parents[0], 3)

    parents[1].add_items(clone_child, position=0)
    assert_ood_sane(parents[1], 4)
    assert len(parents[1]._get_items_by_name("A")) == 2
    assert len(parents[1]._get_items_by_name("B")) == 1
    assert len(parents[1]._get_items_by_name("C")) == 1
    assert children[0] == parents[1]._get_items_by_name("A")[0]
    assert clone_child == parents[1]._get_items_by_name("A")[1]
    assert parents[1].get_items("A", 1) == [clone_child, children[0]]
    assert parents[1].get_items("A", 2) == [clone_child, children[0], children[1]]
    parents[1].pop_items(*children)
    assert parents[1].get_items() == [clone_child]

    layer1[2].unset_strict()
    layer1[2].add_items(*layer2)
    for i, child in enumerate(layer1[2]):
        child.add_items(layer3[0], layer3[i%2+1])
        assert_ood_sane(child, 2)
    assert layer1[2].get_items(s.Has_Children(layer2[0])) == []
    assert layer1[2].get_items(s.Has_Children(layer2[2])) == []
    assert layer1[2].get_items(s.Has_Children(layer3[0])) == layer2
    # has children layer3[1] should return half
    # has chidlren layer3[2] should return half
    # has chidlren layer3[1] shoudl equal layer3[3]
    # has children layer3[2] should equal layer3[4]
