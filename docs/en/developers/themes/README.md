# Theming Graphs

`Graphs`, `Tracks`, `Axes`, and `Data` can all accept `Theme` objects.

Or see below for modifying the depth axis, themes don't affect the depth axis.

## Theme Dictionaries
The simplest theme is a dictionary:

```python
graph.set_theme(
	{
		"hidden":        False      # default
		"track_width":   100,       # pixels
		"color":         "black",   # any valid value from package "colour": e.g. "red", "#FF0000" 
		                            # A list, ['red', 'blue', ...], is treated as a `ColorWheel`
		"range":         [0, 100],
		"range_unit":    "meter",   # any valid value from package "pint"
		"scale":         "log",     # linear is default and fall-back
	}
)
	
		
track.set_theme(...) # overrides graph theme
axis.set_theme(...)  # overrides track theme
data.set_theme(...)  # overrides data theme

# This is the built-in fall-back theme:
default = { 'color': ['#636EFA', '#EF553B', '#00CC96', ... ], 'track_width': 200 }
```

You can override all themes when rendering by setting `override_theme` as an argument to any `.render()` function.

## Dynamic Themes

### ColorWheel

`ColorWheel` is an array (or list) of colors that changes on every call:

```
graph1.set_theme( { 
	'color': ['red', 'blue', 'green', '#0F3DA3']
} )
```

A list of colors is converted automatically to a `ColorWheel` object.

> ⚠️ **Rotation Algo**
>
> Since we encourage using a seperate `axis` for every datum (even if mathematically they are the same axis), the `ColorWheel` will return the same color if the `data` are on the same `axis`. To override this, set the theme directly on the `axis` object OR create the `ColorWheel` explicitly: 
``` 
AXIS.set_theme({
	'color': ['red', 'blue', ...] # will rotate over each datum on this axis
	})
```
```
# OR
GRAPH.set_theme({ 
	'color': ColorWheel(['red', 'blue', ...], per='data') # rotates over each datum on the graph
	})
```
```
# DIFFERENT
GRAPH.set_theme({
	'color': ['red', 'blue', ...] # rotates over every axis
	})
TRACK.set_theme({
	... # same
	}}
```

### MnemonicDictionary

A `MnemonicDictionary` returns a theme dependent on the objects's **mnemonic**

(if, unfortunately, an axis has multiple data with different mnemonics, the first is used)

For example, the **cangrejo** built-in theme is constructed:
```
cangrejo = {
    "CALI" : {
        "color" : "black",
        "range": [0, 16],
        "range_unit": "inch",
    },
    "CGR" : {
        "color" : "green",
        "range": [0, 150.00],
        "range_unit": "gAPI",
    },
    "LLS" : {
        "color" : "gray",
        "range": [0.2, 2000],
        "scale": "log",
        "range_unit": "ohm * meter",
    },
	
	..., # more
	
	"-" : {
		"color" : "black"
	},
```

Where `"-"` is the fall-back theme if a mnemonic doesn't match.

You can create a dictionary with this structure:
```
myMnemonicTheme = pozo.themes.MnemonicDictionary({...a dictionary like above...})
myMnemonicTheme.set_fallback('key1':'value1') # optional
myMnemonicTheme.set_fallback('key2':'value2') # optional
graph1.set_theme(myMnemonicTheme)
graph1.get_theme().set_fallback('key3':'value3') # optional
```

[TODO: how to use the default cangrejo theme]



> #### Developer Notes:
>
>There is a `Theme` class, which `MnemonicTheme` and `ThemeDict` inherit. Theme attributes like `track_width` can resolve to a number, or a `Theme`, in which the resolvation process continues until it finds a number. Sometimes, we find a type that is a `shortcut`, and that type is then resolved out of the logic to whatever it is set to be. For example a `color: [list]` resolves by shortcut to a `ColorWheel`.
>
>There's a lot here: themes, contexts, lists, etc. But TODO.

## Depth Axis Attributes

Not all visual attributes are set with *themes*.

Depth axis attributes are generally set by `graph()` or `render()` arguments. The possible attributes include:
```python
# depth=[True|False]      # turn depth on or off
# depth_position=1,2...   # 1: left-most, # 2: before second track, etc ...
# height=900              # height of graph
# javascript=[True|False] # If true, we will post process rendering to add scrollbars to big graphs

graph1  = pozo.graph(depth=True, depth_pos=1)
graph1.render(depth_pos=2, height=900) # render() takes precedence
# TODO: does this all work?
```

# Renderers

When you create a `graphy`, it sets a default `pozo.themes.Plotly` renderer:

```
graph1 = pozo.graph(las_object, renderer=pozo.themes.Plotly())
graph1.render() # graph1.renderer.render(graph1) <-- equivelenet
```

If you need more fine-grained control over the renderer, one way would be to dive into the source code of the `Plotly` renderer and modify it or make your own (not worth it).

**[TODO: source of plotly renderer] Developer: [Do it]**

It may be better to learn how to use `Plotly`, and then do this:

``` [fix]
import plotly # TODO does this work
layout = graph1.renderer.get_layout()
traces = graph2.renderer.get_traces()
... # your modifications here

graph1 = plotly.draw(layout, traces) # plotly API

graph1.update_layout(...) # more plotly API
```

However, since `Plotly` isn't perfect, we do use javascript to modify the plot after it's drawn. The function that does that is [insert function here]. If you use `graph1.render()` it's called automatically. But if you draw the plotly plot yourself, you may need to call it yourself: [insert function called here].
