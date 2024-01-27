[para español](https://github.com/geopozo/pozo-py/blob/main/docs/es/L%C3%89ANME.md)

# 🐰 Pozo Well Visualizer

Pozo is an open source, intuitive api for visualizing well logs. It uses [plotly](https://github.com/plotly/plotly.py) to render interactive graphs.

```bash
$ pip install pozo
```

Don't forget `pip install lasio` if you're using lasio! If you're using jupyter, `pip install ipywidgets plotly nbformat` as well.

## Simplest Usage

```python
import pozo
import lasio
las = lasio.read("SALADIN.LAS")

# You can specify the data you are interested in
myGraph = pozo.Graph(las, include=["CALI", "CGR", "LLS", "ILD", "LLD", "NPH", "RHOB"])

# This is a good theme
myGraph.set_theme("cangrejo") # recommended theme!

myGraph.render(height=800, depth=[1080, 1180])

```
<p align="center"><img src="docs/images/log_example2.png" /> </p>

<br />

Notice the tracks are in the same order as your list `include=[...]`.


#### Combining Tracks
```
# Before you render

graph1.combine_tracks("CGR", "CALI") # Also maintains order!

graph1.combine_tracks("LLD","ILD","LLS") 

graph1.combine_tracks("RHOB", "NPHI")

# Notice we change position of depth axis with `depth_position=1`
graph1.render(height=800, depth_position=1, depth=[1080, 1180])
```
<p align="center"><img src="docs/images/log_example.png" /> </p>

#### Theming
The `"cangrejo"` theme above is built-in. It uses the `mnemonic` of the data to determine what the color, range, and unit might be. However, it doesn't cover all cases, so you have two options:
```
# Option One: Set a fallback for everything (only works if theme is set to "cangrejo")
graph.get_theme().set_fallback{"track_width":200}

# Option Two: Set a specific theme on a specific track:
graph.get_tracks("CGR")[0].set_theme({"track_width":200})

# Some possible settings:
#  "color": "blue"
#  "scale": "log"
#  "range": [0, 10]
#  "range_unit": "meter"
```

*TODO: to learn more about theming*

#### Selecting Tracks

```
# Returns list of Track objects
tracks         = graph1.get_tracks("CGR", "MDP") # by name
other_tracks   = graph1.get_tracks(0, 2)         # by position

# Removes AND returns list of Track of objects
popped_tracks  = graph1.pop_tracks("CGR", 3)     # by name or position

# Note: The name is often the mnemonic. But not always, like in combined tracks.
# To search explicitly by mnemonic:
popped_tracks2 = graph1.pop_tracks(pozo.HasLog("CGR"))
```

*TODO: to learn more about selecting*

## Adding Data Manually

#### Sometimes you want to do your own math and construct your own data:

```
data = [1, 2, 3]
depth = [1010, 1020, 1030]

new_data=Data(data, depth=depth, mnemonic="LOL!")
graph.add_tracks(new_data)
# all data must have either a mnemonic or a name

```
You can now call `graph.add_tracks(new_data)`

But maybe you want to theme it first. Don't theme the "Data" directly, it won't impact much:

```
new_tracks = graph.add_tracks(new_data)
new_tracks[0].set_theme({"color":"red", range=[0, 1], range_unit="fraction"})
```

*TODO: learn more about the pozo internal data structure*

## Sanitizing Data

### Units

*TODO: common geology-only units*

## Common Operations

### Common Derived Data

### Common Track Views

### Utility Functions

#### Exporting to LAS file
