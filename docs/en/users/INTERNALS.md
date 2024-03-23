# What is Pozo, really?

## The Tree
Let's say you have a `Graph`.
```
import pozo
myGraph = pozo.Graph()
```

This is what you have:

<p align=center><img src=../../images/internal/1.png /></p>


And if you call `myGraph.render()`... you'll get nothing because you haven't added any data yet.

Before we add data, let's add some tracks:

```
myGraph.add_tracks(
	pozo.Track(name="track1"),
	pozo.Track(name="track2")
)
```

Those don't have data, but now our internal data structure looks like this:

<p align=center><img src=../../images/internal/2.png /></p>

`myGraph.render()` still would do nothing, so let's add some data.

```
x = [2, 2, 1, 4, 5, 6]
y = [1, 2, 3, 4, 5, 6]

new_trace = pozo.Trace(x, depth=y, mnemonic="test")

# But where do we add the trace?

track1 = myGraph.get_tracks("track1")[0] # remember, get_tracks always returns a list
track1.add_axes(new_trace)
```

Voilà:

<p align=center><img src=../../images/internal/3.png /></p>

WAIT! Where did the "Axis" box come from?

#### Automatic Pozo Creation

A `pozo.Trace` is **ALWAYS contained** by a `pozo.Axis` is **ALWAYS contained** by a `pozo.Track` is **ALWAYS contained** by a `pozo.Graph`.

If you add a lower-level thing to an upper-level thing, the intermediate things will be created automatically: If you add an `Axis` to a `Graph`, it creates a `Track`. If you add a `Trace` to a `Graph`, it creates an `Axis` and a `Track`.

_Or you can do it all manually:_

```
aGraph = pozo.Graph()
aTrack = pozo.Track()
anAxis = pozo.Axis()
aTrace = pozo.Trace()

aGraph.add_tracks(aTrack)
aTrack.add_axes(aAxis) # order here doesn't matter
anAxis.add_traces(aTrace)
```
### Render
Anyway, now if we `myGraph.render()`, we get this:

<p align=center><img src=../../images/internal/simple_pozo.png /></p>

Very good.

### Quick Reference

*This is not exhaustive, it's meant to illustrate that `pozo.Graph/Track/Axis/Trace` are all very similiar and have similiar mechanics for retreiving, editing, etc children. They also all have a `get_traces()` function if you just want to get at the data for an entire graph or section.* 

## `Graph()`


### Create New:

`newGraph = pozo.Graph()` can take pozo objects or a las file as arguments, and will create tracks for each one. It can also take the following arguments used during rendering:
* `show_depth`: True/False
* `depth_position`: 0, 1, 2, 3, 4
* `depth`: [min, max]
* `height`: height in pixels

### Manipulate:


`someGraph.get_tracks()`: Takes `selector`s, like a name or an index, and returns tracks with that name or at that index
	
`someGraph.pop_tracks()`: Takes `selector`s like a above, and returns the tracks too, but also removes them from the graph

`someGraph.add_tracks()`: Takes `pozo.Data`, `pozo.Axis`, or `pozo.Track`, adds them to the `Graph`, and returns the new `Track`s

`someGraph.combine_tracks()`: Takes `selector`s or `pozo.Track`, and adds them all to the first track listed

`someGraph.move_tracks()`: Takes `selectors` and `position=?` to reorder them


### Display:

`someGraph.render()`: Try to print out your graph. It takes the same extra arguments as `pozo.Graph()`

### Specials:

`someGraph.get_axes()` and `someGraph.get_data()` function too.

## `Track()`

### Create New:

`newTrack = pozo.Track()` can take pozo objects and `name=?`

### Manipulate:

`someTrack.set_name()`: takes a new name

`someTrack.get_name()`: returns the current name

`someTrack.add_axes()`: takes pozo objects and returns the new axes

`someTrack.get_axes()`: takes `selector`s and returns the axes if they exist

`someTrack.get_...` bla bla bla, it's very similiar to `Graph()`. `Axis()` is similiar. `Data()` is different:

## `Axis()`

Is very similiar to `Track()` except it's `get_traces()` `add_traces()` `pop_traces()` etc.

## `Trace()`

### Create Traces:

`myData = pozo.Trace(data, depth=something, mnemonic="something")`: These three are required. But you can also supply `unit=` and `depth_unit=`.

### Manipulate:

`someTrace.get_mnemonic()`: returns mnemonic

`someTrace.set_mnemonic()`: takes mnemonic

`someTrace.get_data()`: returns data

`someTrace.set_data()`: sets data, can also take `depth=`

`someTrace.get_depth()`: gets depth trace

`someTrace.set_depth()`: sets depth data

`someTrace.get_unit()`: gets current units for data

`someTrace.set_unit()`: sets current units for data

`someTrace.get_depth_unit()`: gets current depth unit

`someTrace.set_depth_unit()`: sets current depth unit

`someTrace.convert_unit()`: takes a new unit, and if it can figure out the conversion, does it

`someTrace.convert_depth_unit()` takes a new unit, and if it can figure out the conversion, does it

## Special Selectors

Normally, a selector is a number (position) or a name. There are others:

* Every pozo object is a selector for itself:
```
track1 = pozo.Track()
track2 = pozo.Track()
graph1.add_tracks(track1)
len(graph1.get_tracks(track1, track2)) == 1
```
* `pozo.HasLog("MNEMONIC")` will search every data for a particular object and return the pozo Object you're looking for if it finds it.
