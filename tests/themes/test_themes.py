import pytest
import pozo.themes as pzt

def test_Theme():
    assert type(pzt.Theme()) == pzt.Theme
    new_theme = pzt.Theme()
    assert new_theme.get_context() == {}
    new_theme.set_context({"key":"value"})
    assert new_theme.get_context()["key"] == "value"
    new_theme.set_context(None)
    assert new_theme.get_context() == {}
    with pytest.raises(NotImplementedError):
        new_theme.resolve(None, None)
    with pytest.raises(TypeError):
        new_theme.set_context([])
    with pytest.raises(TypeError):
        new_theme.set_context(3)
    with pytest.raises(TypeError):
        new_theme.set_context("yes")
    with pytest.raises(TypeError):
        new_theme.set_context(False)
    with pytest.raises(TypeError):
        new_theme.set_context()

def test_ThemeDict():
    tdict1 = pzt.ThemeDict({"key": "value"})
    tdict2 = pzt.ThemeDict(dict(key="value"))
    assert tdict1["key"] == tdict2["key"]
    assert tdict1.resolve("key") == tdict2.resolve("key")

def test_DynamicTheme():
    assert type(pzt.DynamicTheme()) == pzt.DynamicTheme

def test_Themeable():
    assert type(pzt.Themeable()) == pzt.Themeable
    themeable1 = pzt.Themeable()
    themeable2 = pzt.Themeable(theme = {})
    themeable3 = pzt.Themeable(theme = {'key':'value'})
    themeable4 = pzt.Themeable(theme = pzt.DynamicTheme())
    themeable5 = pzt.Themeable(theme = pzt.ThemeDict({'key':'value'}))

    theme1 = themeable1.get_theme()
    assert theme1 == {}
    assert theme1.get_context() == {}
    assert theme1.resolve('key') == None
    theme2 = themeable2.get_theme()
    assert theme2 == {}
    assert theme2.get_context() == {}
    assert theme2.resolve('key') == None
    theme3 = themeable3.get_theme()
    assert theme3['key'] == 'value'
    assert theme3.get_context() == {}
    assert theme3.resolve('key') == 'value'
    theme4 = themeable4.get_theme()
    assert type(theme4) == pzt.DynamicTheme
    assert theme4.get_context() == {}
    with pytest.raises(NotImplementedError):
        assert theme4.resolve('key', theme4.get_context()) == None
    theme5 = themeable5.get_theme()
    assert theme5['key'] == 'value'
    assert theme5.get_context() == {}
    assert theme5.resolve('key') == 'value'

def test_ThemeStack():
    theme1 = pzt.ThemeDict({
        "a": "theme1",
        })
    theme2 = pzt.ThemeDict({
        "a": "theme2",
        "b": "theme2",
        })
    theme3a = pzt.ThemeDict({
        "c": "theme3a",
        })
    theme3 = pzt.ThemeDict({
        "a": "theme3",
        "b": "theme3",
        "c": theme3a,
        "d": theme3a, # So this should still resolve to theme4
        })
    theme4 = pzt.ThemeDict({
        "a":"theme4",
        "b":"theme4",
        "c":"theme4",
        "d":"theme4",
        })
    theme5 = pzt.ThemeDict({
        "a":"theme5",
        "b":"theme5",
        "c":"theme5",
        "d":"theme5",
        "e":"theme5",
        })
    override = pzt.ThemeDict({ # put this on top of just theme 5
        "a": theme1,
        "b": theme2,
        "c": theme3,
        "d": theme4,
        "e": theme4,
        })
    list_no_override = pzt.ThemeStack(default=None)
    assert len(list_no_override._list) == 0
    with pytest.raises(KeyError): list_no_override["a"]
    with pytest.raises(KeyError): list_no_override["b"]
    with pytest.raises(KeyError): list_no_override["c"]
    with pytest.raises(KeyError): list_no_override["d"]
    with pytest.raises(KeyError): list_no_override["e"]
    with pytest.raises(KeyError): list_no_override["f"]
    list_no_override.append(theme5)
    assert len(list_no_override._list) == 1
    assert list_no_override["a"] == "theme5"
    assert list_no_override["b"] == "theme5"
    assert list_no_override["c"] == "theme5"
    assert list_no_override["d"] == "theme5"
    assert list_no_override["e"] == "theme5"
    with pytest.raises(KeyError): list_no_override["f"]
    list_no_override.append(theme4)
    assert len(list_no_override._list) == 2
    assert list_no_override["a"] == "theme4"
    assert list_no_override["b"] == "theme4"
    assert list_no_override["c"] == "theme4"
    assert list_no_override["d"] == "theme4"
    assert list_no_override["e"] == "theme5"
    with pytest.raises(KeyError): list_no_override["f"]
    list_no_override.append(theme3)
    assert len(list_no_override._list) == 3
    assert list_no_override["a"] == "theme3"
    assert list_no_override["b"] == "theme3"
    assert list_no_override["c"] == "theme3a"
    assert list_no_override["d"] == "theme4"
    assert list_no_override["e"] == "theme5"
    with pytest.raises(KeyError): list_no_override["f"]
    list_no_override.append(theme2)
    assert len(list_no_override._list) == 4
    assert list_no_override["a"] == "theme2"
    assert list_no_override["b"] == "theme2"
    assert list_no_override["c"] == "theme3a"
    assert list_no_override["d"] == "theme4"
    assert list_no_override["e"] == "theme5"
    with pytest.raises(KeyError): list_no_override["f"]
    list_no_override.append(theme1)
    assert len(list_no_override._list) == 5
    assert list_no_override["a"] == "theme1"
    assert list_no_override["b"] == "theme2"
    assert list_no_override["c"] == "theme3a"
    assert list_no_override["d"] == "theme4"
    assert list_no_override["e"] == "theme5"
    with pytest.raises(KeyError): list_no_override["f"]
    list_no_override.pop()
    assert len(list_no_override._list) == 4
    assert list_no_override["a"] == "theme2"
    assert list_no_override["b"] == "theme2"
    assert list_no_override["c"] == "theme3a"
    assert list_no_override["d"] == "theme4"
    assert list_no_override["e"] == "theme5"
    with pytest.raises(KeyError): list_no_override["f"]
    list_no_override.pop()
    assert len(list_no_override._list) == 3
    assert list_no_override["a"] == "theme3"
    assert list_no_override["b"] == "theme3"
    assert list_no_override["c"] == "theme3a"
    assert list_no_override["d"] == "theme4"
    assert list_no_override["e"] == "theme5"
    with pytest.raises(KeyError): list_no_override["f"]
    list_no_override.pop()
    assert len(list_no_override._list) == 2
    assert list_no_override["a"] == "theme4"
    assert list_no_override["b"] == "theme4"
    assert list_no_override["c"] == "theme4"
    assert list_no_override["d"] == "theme4"
    assert list_no_override["e"] == "theme5"
    with pytest.raises(KeyError): list_no_override["f"]
    list_no_override.pop()
    assert len(list_no_override._list) == 1
    assert list_no_override["a"] == "theme5"
    assert list_no_override["b"] == "theme5"
    assert list_no_override["c"] == "theme5"
    assert list_no_override["d"] == "theme5"
    assert list_no_override["e"] == "theme5"
    with pytest.raises(KeyError): list_no_override["f"]
    list_no_override.pop()
    assert len(list_no_override._list) == 0
    with pytest.raises(KeyError): list_no_override["a"]
    with pytest.raises(KeyError): list_no_override["b"]
    with pytest.raises(KeyError): list_no_override["c"]
    with pytest.raises(KeyError): list_no_override["d"]
    with pytest.raises(KeyError): list_no_override["e"]
    with pytest.raises(KeyError): list_no_override["f"]
    list_override = pzt.ThemeStack(theme=override)
    assert len(list_no_override._list) == 0
    assert list_override["a"] == "theme1"
    assert list_override["b"] == "theme2"
    assert list_override["c"] == "theme3a"
    assert list_override["d"] == "theme4"
    with pytest.raises(KeyError): list_override["e"]
    with pytest.raises(KeyError): list_override["f"]
    list_override.append(theme5)
    assert list_override["a"] == "theme1"
    assert list_override["b"] == "theme2"
    assert list_override["c"] == "theme3a"
    assert list_override["d"] == "theme4"
    assert list_override["e"] == "theme5"
    with pytest.raises(KeyError): list_override["f"]
    list_override.pop()
    assert list_override["a"] == "theme1"
    assert list_override["b"] == "theme2"
    assert list_override["c"] == "theme3a"
    assert list_override["d"] == "theme4"
    with pytest.raises(KeyError): list_override["e"]
    with pytest.raises(KeyError): list_override["f"]
    with pytest.raises(IndexError):
        list_override.pop()


def test_ColorWheel():
    wheel = pzt.ColorWheel()
    assert wheel._per == "axis"
    themeL = pzt.ThemeStack()
    theme = pzt.ThemeDict({"color":["red", "green", "blue"]})
    theme.set_context({"type":"not_axis"})
    themeL.append(theme)

    assert themeL["color"] == "#ff0000"
    assert themeL["color"] == "#ff0000"
    assert themeL["color"] == "#ff0000"
    assert themeL["color"] == "#ff0000"
    assert themeL["color"] == "#ff0000"
    assert themeL["color"] == "#ff0000"

    themeL = pzt.ThemeStack()
    theme = pzt.ThemeDict({"color":["red", "green", "blue"]})
    theme.set_context({"type":"track"})
    themeL.append(theme)
    theme2 = pzt.ThemeDict()
    theme2.set_context({"type":"axis"})
    themeL.append(theme2)
    assert themeL["color"] == "#ff0000"
    themeL.pop()
    theme2.set_context({"type":"axis"})
    themeL.append(theme2)
    assert themeL["color"] == "#008000"
    themeL.pop()
    theme2.set_context({"type":"axis"})
    themeL.append(theme2)
    assert themeL["color"] == "#0000ff"
    themeL.pop()
    theme2.set_context({"type":"axis"})
    themeL.append(theme2)
    assert themeL["color"] == "#ff0000"
    themeL.pop()
    theme2.set_context({"type":"axis"})
    themeL.append(theme2)
    assert themeL["color"] == "#008000"
    themeL.pop()
    theme2.set_context({"type":"axis"})
    themeL.append(theme2)
    assert themeL["color"] == "#0000ff"

    themeL = pzt.ThemeStack()
    theme = pzt.ThemeDict({"color":["red", "green", "blue"]})
    theme.set_context({"type":"track"})
    themeL.append(theme)
    theme2 = pzt.ThemeDict({"color":"black"})
    theme2.set_context({"type":"axis"})
    themeL.append(theme2)
    assert themeL["color"] == "#000000"
    assert themeL["color"] == "#000000"
    assert themeL["color"] == "#000000"
    assert themeL["color"] == "#000000"

    themeL = pzt.ThemeStack()
    theme = pzt.ThemeDict({"color":["red", "green", "blue"]})
    themeL.append(theme)
    assert themeL["color"] == "#ff0000"

    themeL = pzt.ThemeStack()
    theme = pzt.ThemeDict({"color":pzt.ColorWheel(["red", "green", "blue"], each=True)})
    themeL.append(theme)
    assert themeL["color"] == "#ff0000"
    assert themeL["color"] == "#008000"
    assert themeL["color"] == "#0000ff"
    assert themeL["color"] == "#ff0000"
    assert themeL["color"] == "#008000"
    assert themeL["color"] == "#0000ff"

