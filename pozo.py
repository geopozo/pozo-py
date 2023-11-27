import plotly.graph_objects as go
import itertools, copy, warnings

####
####
#### Utilities
####
####
def make_iter(thing):
    try:
        test = iter(thing)
        return thing
    except Exception as e:
        thing = [thing]
        return thing
####
####
#### Constants
####
####

LAS_TYPE = "<class 'lasio.las.LASFile'>"

####
####
#### Graph Class
####
####

class Graph():

    ## Constructor
    def __init__(self, *args, **kwargs):
        self.style = kwargs.get('style', Style())


        # Objects
        self.tracks_ordered = [] 
        self.tracks_by_id = {}

        self.process_data(self, *args, **kwargs)

    def process_data(self, *args, **kwargs):
        for ar in args:
            # Process LASio LAS Object
            if str(type(ar)) == LAS_TYPE:
                self.add_las_object(ar, **kwargs)
            # Process Data, Track, Axis, Numpy, Welly, Panda, XArray

    def add_las_object(self, ar, **kwargs):
        include = kwargs.get('include', [])
        exclude = kwargs.get('exclude', [])
        yaxis = kwargs.get('yaxis', None) # what if not none
        yaxis_name = kwargs.get('yaxis_name',"DEPTH")

        if yaxis is not None:
            if len(yaxis) != len(ar.index):
                raise ValueError(f"Length of supplied yaxis ({len(yaxis)}) does not match length of LAS File index ({len(ar.index)})")
            yaxis_name = None
        elif yaxis_name in ar.curves.keys():
            yaxis = ar.curves[yaxis_name].data
        else:
            yaxis = ar.index
            yaxis_name = None


        for curve in ar.curves:
            ## Deciding to ignore?
            if yaxis_name is not None and curve.mnemonic == yaxis_name:
                continue
            mnemonic = curve.mnemonic.split(":", 1)[0] if ":" in curve.mnemonic else curve.mnemonic
            if len(include) != 0 and curve.mnemonic not in include and mnemonic not in include: 
                continue
            elif len(exclude) != 0 and curve.mnemonic in exclude or mnemonic in exclude:
                continue 


            data = Data(yaxis, curve.data, mnemonic)
            newTrack = Track(data)

            self.add_track(newTrack)

    #### 
    #### 
    #### Basic Add-Get(s)-Remove Track
    #### 
    #### 

    def add_track(self, track): #TODO allow it take axes and data
        if id(track) in self.tracks_by_id: return
        self.tracks_ordered.append(track)
        self.tracks_by_id[id(track)] = track

    def get_tracks(self, selectors, ignore_orphans=True, cap=0): # add cap
        tracks = []
        try: # TODO: factor out
            test = iter(selectors)
        except Exception as e:
            selectors = [selectors]
        for selector in selectors:
            if cap and len(tracks) >= cap: break
            if isinstance(selector, int): # get by track index
                selector -=1
                if selector >= len(self.tracks_ordered) or selector < 0:
                    raise IndexError("Track index out of range")
                tracks.append(self.tracks_ordered[selector])
            elif isinstance(selector, str) or isinstance(selector, Axis): # get by axis/axis-name
                for track in self.tracks_ordered:
                    if track.has_axis(selector):
                        tracks.append(track)
            elif isinstance(selector, Track): # get by track object
                if id(selector) in self.tracks_by_id or not ignore_orphans:
                    tracks.append(selector)
        if len(tracks) == 0: return None
        if cap and len(tracks) >= cap: tracks = tracks[0:cap]
        return tracks

    def get_track(self, selector, match=0): # get first match
        tracks = self.get_tracks(selector, cap=1)
        if match >= len(tracks):
            return None
        return tracks[match]

    def remove_tracks(self, tracks):
        tracks = self.get_tracks(tracks)
        if tracks is None: return None
        for track in tracks:
            if id(track) not in self.tracks_by_id: continue
            del self.tracks_by_id[id(track)]
            self.tracks_ordered.remove(track)
        return tracks

    ####
    ####
    #### Modify Tracks
    ####
    ####

    def add_to_track(self, destination, tracks):
        destination = self.get_track(destination)
        if destination is None: raise Exception("Destination track does not exist")
        tracks = self.get_tracks(tracks, ignore_orphans=False)
        if tracks is None: return    
        for track in tracks:
            if id(track) in self.tracks_by_id:
                self.remove_tracks(track)
            for lower in track.get_lower_axes():
                destination.add_axis(lower, position=-1000)
            for upper in track.get_upper_axes():
                destination.add_axis(upper, position=1000)

    ####
    ####
    #### Rendering Functions
    ####
    ####

    def get_layout(self): # TODO will not be done this way
        
        self.style.init_layout()

        num_tracks = len(self.tracks_ordered)
        if not num_tracks:
            raise Exception("There are no tracks, there is nothing to lay out")
            
        max_axes_top = 0
        max_axes_bottom = 0
        for track in self.tracks_ordered:
            max_axes_bottom = max(track.count_lower_axes(), max_axes_bottom)
            max_axes_top = max(track.count_upper_axes(), max_axes_top)

        self.style.set_figure_dimensions(num_tracks, max_axes_bottom, max_axes_top)

        # Style object must have figure dimensions before it can render axis styles
        # Although it could be written to do that retroactively, I suppose
        axes = []
        for track_position, track in enumerate(self.tracks_ordered):
            parent_axis = len(axes)+1 # axes need to anchor to first axis of track
            new_axes = track.render_style(self.style, parent_axis)
            for axis in new_axes: # axis dictionaries
                self.style.set_axis_horizontal_position(axis, track_position) # axis modified in place
                axes.append(axis)

        self.style.set_axes(axes)
        self.style.set_y_limits()
        return self.style.get_layout()

    def get_traces(self):
        traces = [] 
        num_axes = 1
        for track in self.tracks_ordered:
            for axis in track.get_all_axes():
                # if there is an update_trace, it's better to update the axis than pass a num axes
                traces.extend(axis.render_traces(num_axes)) # Big UGH
                num_axes += 1
        return traces

    def draw(self):
        layout = self.get_layout()
        traces = self.get_traces()
        fig = go.Figure(data=traces, layout=layout)
        # Could seperate this into render and config
        fig.show() # TODO renderer will create figure so... Graph.Renderer.Render() probably
        display(self.style.javascript()) # This is going to be in layout, Display

 
    ####
    ####
    #### Utility Functions
    ####
    ####

    ## For your info
    def get_named_tree(self):
        result = []
        for track in self.tracks_ordered:
            result.append(track.get_named_tree())
        return { 'graph': result }

class Track():
    def __init__(self, *args, **kwargs): # {name: data}

        self.axes = {}
        self.axes_below = [] # Considered "before" axes_above list
        self.axes_above = []
        self.axes_by_id = {}

        self.add_axes(*args, **kwargs)

    def add_axes(self, *args, **kwargs): # accept "upper" and "lower"
        for ar in args:
            if isinstance(ar, Data):
                self.add_axis(Axis(ar))
            ## process Axes, [Data], Axis
            ## how do we indicate where to add the axis (top or bottom)

    #### 
    #### 
    #### Basic Add-Get(s)-Remove Axis
    #### 
    #### 

    def add_axis(self, axis, position=1): # add_axes?
        # should it also accept data, and [data] (and then process_data doesn't have to
        if position == 0:
            raise Exception("Position must be > or < 0")
        if id(axis) in self.axes_by_id:
            warnings.Warn("An axis was not added as it is already on the track")
            return

        if axis.name in self.axes: # Because more than one axis can have the same now
            self.axes[axis.name].append(axis)
        else:
            self.axes[axis.name] = [axis]
        
        if position > 0:
            if position >= len(self.axes_above):
                self.axes_above.append(axis)
            else:
                self.axes_above.insert(position-1, axis)
        else:
            position = -position
            if position >= len(self.axes_below):
                self.axes_below.append(axis)
            else:
                self.axes_below.insert(position-1, axis)
        
        self.axes_by_id[id(axis)] = axis

    def get_all_axes(self):
        return list(itertools.chain(self.axes_below, self.axes_above)) 
    def get_lower_axes(self):
        return self.axes_below
    def get_upper_axes(self):
        return self.axes_above

    def get_axes(self, selectors, ignore_orphans=True, cap=0):
        axes = []
        try:
            test = iter(selectors)
        except Exception as e:
            selectors = [selectors]
        for selector in selectors:
            if cap and len(axes) >= cap: break
            if isinstance(selector, str): # axes by name
                if selector in self.axes:
                    axes.extend(self.axes[selector])
            elif isinstance(selector, int): # axes by index # (amything but 0)
                source = self.axes_below if selector < 0 else self.axes_above
                index = abs(selector) - 1
                if index >= len(source):
                    raise KeyError("Invalid index in get_axes")
                axes.append(source[index])
            elif isinstance(select, axis): # just get by actual axis
                if id(axis) in self.axes_by_id or not ignore_orphans:
                    axes.append(axis)
        if len(axes) == 0: return None
        if cap and len(axes) > cap: axes = axes[0:cap]
        return axes

    def get_axis(self, selector, match=0):
        axes = self.get_axes(selector, cap=1)
        if axes is None or match >= len(axes):
            return None
        return axes[match]

    def remove_axes(self, axes):
        axes = self.get_axes(axes)
        if axes is None: return None
        for axis in axes:
            if id(axis) not in self.axes_by_id: continue
            del self.axes_by_id[id(axis)]
            self.axes[axis.name].remove(axis)
            if len(self.axes[axis.name]) == 0:
                del self.axes[axis.name]
            try:
                self.axes_below.remove(axis)
            except ValueError:
                self.axes_above.remove(axis)
        return axes
    
    def count_axes(self):
        return len(self.axes)
    def count_lower_axes(self):
        return len(self.axes_below)
    def count_upper_axes(self):
        return len(self.axes_above)

    def has_axis(self, selector):
        return self.get_axis(selector) is not None

    def render_style(self, style, lower_parent):
        axes = [] # array of style dictionaries, not Axis()
        for axis_position, axis in enumerate(self.get_lower_axes()):
            axis_dict=axis.render_style(style)
            style.set_axis_veritcal_position(
                axis_dict,
                -(axis_position+1),
                lower_parent,
            ) # modifies the dict
            axes.append(axis_dict)
        for axis_position, axis in enumerate(self.get_upper_axes()):
            axis_dict=axis.render_style(style)
            style.set_axis_vertical_position(
                axis_dict,
                axis_position+1,
                lower_parent+self.count_lower_axes(),
            ) # modifies the dict
            axes.append(axis_dict)
        return axes

    def get_named_tree(self):
        above = []
        below = []
        for axis in reversed(self.axes_above):
            above.append(axis.get_named_tree())
        for axis in reversed(self.axes_below):
            below.append(axis.get_named_tree())
        return { "track": { self.name: { "above": above, "below": below } } }

class Axis():

    def __init__(self, *args, **kwargs):
        self._name = kwargs.get('name', self.data[0].mnemonic)
        self._display_name = kwargs.get('display_name', self.name)
        # Add Color TODO
        self._data = {}
        self._data_ordered = []
        self._data_by_id = {} # Could we just

        for ar in args:
            self.add_data(ar)

    def add_data(self, data):
        data = make_iter(data)
        for datum in data:
            if id(datum) in self.data_by_id:
                #warnings ## WARNING TODO
                continue
            if isinstance(datum, Data):
                self._data_ordered.append(datum)
                if datum.get_name() in self._data:
                    self._data[datum.get_name()].append(datum)
                else:
                    self._data[datum.get_name()] = [datum]
                self._data_by_id[id(datum)] = datum
                datum._register_axes(self)
            elif isinstance(datum, Axis):
                self.add_data(datum.get_data())
            else:
                warnings.Warn("Axis.add_data() takes Data, Axis, or an iterable of those types. Type " + type(datum) + " was ignored")
            
    def get_data(self, selectors = None, cap = 0, ignore_orphans=True): # TODO get by name or by actual
        if selectors is None:
            if cap: return self._data[0:cap]
            return self._data
        selectors = make_iter(selectors)
        data = []
        for selector in selectors:
            if cap and len(data) >= cap: break
            elif isinstance(selector, str):
                data.extend(self._data[selector])
            elif isinstance(selector, Data):
                if id(selector) in self._data_by_id or not ignore_orphans:
                    data.append(selector)
        if not len(data): return None
        if cap and len(data) > cap: data = data[0:cap]
        return data
    
    def get_datum(self, selector, match=0):
        data = self.get_data(selector, cap=match+1)
        if not data or match >= len(data): return None
        return data[match]

    def remove_data(self, selectors = None, cap=0):
        selectors = make_iter(selectors)
        data = self.get_data(selectors, cap)
        for datum in data:
            pass ### TODO
        return data
            
    def _change_data_name(self, datum, old_name, new_name):
        if old_name == new_name:
            return
        ### TODO (remove from one index, put it in the other index)

    def get_named_tree(self):
        result = []
        for el in self.data:
            result.append(el.get_named_tree())
        return { "axis" : { self.name: result } }

class Data():
    def __init__(self, index, values, **kwargs): # Default Index?
        if 'name' not in kwargs and 'mnemonic' not in kwargs:
            raise ValueError("You must specifiy either 'name=' or 'mnemonic' equals. If not told to be different, they will be the same.")
        axes = kwargs.get('axes', [])
        self._axes = {}
        self._name = kwargs.get('name', mnemonic)
        self._index = index
        self._values = values
        self._mnemonic = mnemonic
        self._color = kwargs.get('color', Color())

        if not isinstance(axes, list) or len(axes) > 0:
            axes = make_iter(axes)
            self._register_axes(axes)

    def _register_axes(self, axes):
        axes = make_iter(axes)
        for axis in axes:
            if id(axis) in self._axes_by_id:
                warnings.Warn("Tried to add data to axes which already contains data. Ignored")
                continue
            self._axes_by_id[id(axis)] = axis
            
    def _deregister_axes(self, axes):
        axes = make_iter(axes)
        for axis in axes:
            if id(axis) not in self._axes_by_id:
                warnings.Warn("Tried to remove data from axes where it doesn't exist. Ignored.")
                continue
            del self._axes_by_id[id(axis)]

    def set_name(self, name):
        if self._name == name:
            return
        old_name = self._name
        self._name = name
        for axis_id in self._axes_by_id:
            self._axes_by_id[axis_id]._change_data_name(self, old_name, self._name)

    def get_name(self):
        return self._name
    
    def set_values(self, values):
        self._values = values
    def get_values(self):
        return self._values

    def set_index(self, index):
        self._index = index
    def get_index(self):
        return self._index
    
    ## TODO: if user changes set values/index, should we automatically update graph?

    def set_values(self, values):
        self._values = values
    def get_values(self):
        return self._values
        
    def set_mnemonic(self, mnemonic):
        self._mnemonic = mnemonic
    def get_mnemonic(self):
        return self._mnemonic
        
    def set_color(self, color):
        self._color = color

    def get_named_tree(self):
        return  { "data" : {
            'name': self._name,
            'mnemonic': self._mnemonic,
            'shape': self._values.shape,
            'color': self._color,
        } }

class Color(): ## TODO better default colors, in pozo.style
    def __init__(self, color=None):
        self.set_color(color)
        self._i = 0
    
    def set_color(self, color):
        if color:
            color = make_iter(color)
        ## TODO, verify colors
        self._color = color

    def get_color(self, i=0):
        if not self._color or not len(self._color): return "#000000"
        return self._color[i % len(self._color)]