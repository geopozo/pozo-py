[para español]()

# Pozo

Pozo is an open source, intuitive api for visualizing well logs. It accepts las objects from [lasio](https://github.com/kinverarity1/lasio), and uses [plotly](https://github.com/plotly/plotly-py) to render interactive graphs.

```bash
$ pip install pozo
```

Don't forget `pip install lasio` if you're using lasio!

## Basic Usage

```python
import pozo
import lasio
las = lasio.read("/your/las/file/here")
myGraph = pozo.Graph(las)
myGraph.set_theme("cangrejo") # recommended
myGraph.render()
```

See [this example](https://github.com/geopozo/pozo-py/tree/main/docs/en/users/saladin) for more involved usage, but note that github will not render the graphs because they are too big. You must open it in binder or your own environment for that.

## Quick Reference

*Note: the docstring reference is not written yet*

### Basic Classes

There are several `pozo` classes: One `Graph` contains many `Track` which contains many `Axis` which contains many `Data`.

```
# Graph objects can do almost anything
myGraph = pozo.Graph(las)
# OR, same thing
myGraph = pozo.Graph()
myGraph.process_data(las)
```
`process_data()` can accept `las` objects and (TODO). Similiar functions include:
```
# These can only accept `Data`, `Axis`, and `Track` 
# and only if the container is lower on the hierarchy:
# e.g.
# `Graph` accepts anything in `.add_tracks()`.
# `Axis` only accepts `Data` in `.add_data()`.
graph.add_tracks(...)
track.add_axes(...)
axes.add_data(...)
```
#### Basic Styling

New `Graph()` objects and the `graph.render()` (which overrides what was set on `Graph()`) take arguments:

```
# or in myGraph.render()
myGraph = pozo.Graph(las,
	depth=[min, max],
	depth_position=0, # default, leftmost, or 1 after first track, etc
	show_depth=True, # default
	javascript=True, # default, will use javascript to fix up scrollbars
	height=900, # sets height of graph
)

# OR

myGraph.show_depth(False)
myGraph.set_depth_position(10)
myGraph.set_height(900)
myGraph.set_depth([0, 10000])
```

### Creating Data Manually

Strongly recommended to create a new axis for each data (is default behavior) instead of adding multiple data to the same axis, even if mathematically they share an axis. In `pozo`, an axis is also a label, a coloring, etc.
```
data = [10, 20, 30]
depths = [0, 1, 2]
myNewData = pozo.Data(data, data_unit="some_unit", depth=depths, depth_unit="some_unit", mnemonic="DT")
```
`pozo.Data()` requires a `data` argument first, a `depth=` argument, and a `mnemonic=` (or `name=`). Units are good practice (we use `pint`).
```
myGraph.add_tracks(myNewData)

# This will automatically wrap `myNewData` in a new `Axis`, and a new `Track`.
# All will set their `name` to be equal to the mnemonic.
```

### Searching for Objects
```
myGraph = pozo.Graph(las)
tracks = myGraph.getTracks(selector1...) # returns tracks []
oneTrack = myGraph.getTrack(selector)    # returns first match or None
axes = myGraph.getAxes(selector1...)     # returns axes []
data = myGraph.getData(selector1...)     # returns data []

axes2 = tracks[0].getAxes(selector1...)  # returns axes []
oneAxis = tracks[0].getAxis(selector)    # returns first match or None
data2 = tracks[0].getData(selector1...)  # returns data []

data3 = axes[0].getData(selector1...)    # returns data []
oneDatum = axes[0].getDatum(selector)    # returns first match or None
```
#### Selectors

Selectors can be:
* numbers (position)
* names (sometimes things have same name!)
* nothing at all (`getTracks()` returns all tracks)
* `pozo.HasLog("MNEMONIC")`: eg. `graph.getData(pozo.HasLog("CGR"))` will return all data of "CGR"

### Other Functions
```
# All axes from tracks in the [] will be moved onto the selector_sink track
# In order of how you write them!
graph.combine_tracks(selector_sink, [selector1, selector2])

graph.pop_tracks(selectors) # removes and returns matches
track.pop_axes(selectors) # removes and returns matches
axis.pop_data(selectors) # removes and returns matches

graph.has_track(selector) # True or False
track.has_axis(selector) # True or False
axis.has_data(selector) # True or False

graph.reorder_all_tracks([selectors...]) # must indicate every track unambiguously
track.reorder_all_axes([selectors...]) # must indicate every axis unambiguously
axis.reorder_all_data([selectors...]) # must indicate every data unambiguously

graph.move_tracks(*selectors, ?) # the ? must be one of
# position= (+ or -)
# distance= (+ or -)
# before=selector
# after=selector
```
### Themes

`graph.set_theme("cangrejo")` is a good option, it will determine colors, ranges, and units based on mnemonic.


Themes can be set manually on any object, with specificity taking preference. The dictionary of a theme is:
```
{
	"color": "blue", # we use the Colours library
	"track_width": 100,
	"scale": "log" | "linear",
	"range": [0, 1000],
	"range_unit": "ohm * meter", # string from pint
	# range_units help pozo map your Data to the graph.
	# eg. If range_unit is meters and the data is in feet, it converts during render.
}
```
Also, if using "cangrejo" (or any other **Dynamic Mnemonic Theme** that you write):

```
graph.set_theme("cangrejo") # graph.set_theme(pozo.themes.MnemonicDictionary(myDictionaryObject))
graph.get_theme().set_fallback({ "track_width": 100 }) # will set a fallback if there is no other match
```
