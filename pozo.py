import plotly.graph_objects as go
import itertools, copy, warnings

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
        include = kwargs.get('include', [])
        exclude = kwargs.get('exclude', [])
        yaxis = kwargs.get('yaxis', None)
        yaxis_name = kwargs.get('yaxis_name',"DEPTH")
        self.style = kwargs.get('style', Style())


        # Objects
        # A list and its index see NOTE:ORDEREDDICT
        self.tracks_ordered = [] 
        self.tracks_by_id = {}

        self.process_data(self, *args, **kwargs)

    def process_data(self, *args, **kwargs):
        include = kwargs.get('include', [])
        exclude = kwargs.get('exclude', [])
        yaxis = kwargs.get('yaxis', None) # what if not none
        yaxis_name = kwargs.get('yaxis_name',"DEPTH")

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
            pass
        elif yaxis_name in ar.curves.keys():
            yaxis = ar.curves[yaxis_name].data
        else:
            yaxis = ar.index

        for curve in ar.curves:
            ## Deciding to ignore?
            if curve.mnemonic == yaxis_name:
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

    def add_track(self, track):
        if id(track) in self.tracks_by_id: return
        self.tracks_ordered.append(track)
        self.tracks_by_id[id(track)] = track

    def get_tracks(self, selectors, ignore_orphans=True): # add cap
        tracks = []
        try:
            test = iter(selectors)
        except Exception as e:
            selectors = [selectors]
        for selector in selectors:
            if isinstance(selector, int):
                selector -=1
                if selector >= len(self.tracks_ordered) or selector < 0:
                    raise IndexError("Track index out of range")
                tracks.append(self.tracks_ordered[index])
            elif isinstance(selector, str) or isinstance(selector, Axis):
                for track in self.tracks_ordered:
                    if track.has_axis(selector):
                        tracks.append(track)
            elif isinstance(selector, Track):
                if id(selector) in self.tracks_by_id or not ignore_orphans:
                    tracks.append(selector)
        if len(tracks) == 0:
            return None
        return tracks

    def get_track(self, selector, match=0):
        tracks = self.get_tracks(selector)
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

    def combine_tracks(self, destination, tracks):
        destination = self.get_track(destination)
        if destination is None: raise Exception("Destination track does not exist")
        tracks = self.get_tracks(tracks, ignore_orphans=False)
        if tracks is None: return    
        for track in tracks:
            if id(track) in self.tracks_by_id:
                self.remove_track(track)
            for lower in track.get_lower_axes():
                destination.add_axis(lower, position=-1000)
            for upper in track.get_upper_axes():
                destination.add_axis(upper, position=1000)

    ####
    ####
    #### Rendering Functions
    ####
    ####

    def get_layout(self):
        # default but changeable
        self.style.init_layout()

        num_tracks = len(self.tracks_ordered) # TODO should be done by style
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
            new_axes = track.render_style(self.style, len(axes))
            for axis in new_axes:
                axes.append(self.style.set_axis_horizontal_position(axis, track_position))
        self.style.add_axes(axes)
        self.style.set_y_limits()
        # Don't love this generation
        
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
        fig.show()
        display(scrollON()) # This is going to be in layout, Display

 
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

        # This is really one object (but we can't private in python)
        self.axes = {}
        self.axes_below = [] # Considered "before" axes_above list
        self.axes_above = []
        self.axes_by_id = {}

        self.process_data(*args, **kwargs)

    def process_data(self, *args, **kwargs): # accept "upper" and "lower"
        for ar in args:
            if isinstance(ar, Data):
                self.add_axis(Axis(ar))
            ## process axis
            ## how do we indicate where to add the axis (top or bottom)
            ## Process other types?

    #### 
    #### 
    #### Basic Add-Get(s)-Remove Axis
    #### 
    #### 

    def add_axis(self, axis, position=1): # add_axes?
        if position == 0:
            raise Exception("Position must be > or < 0")
        if id(axis) in self.axes_by_id:
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
            if isinstance(selector, str):
                if selector in self.axes:
                    axes.extend(self.axes[selector])
            elif isinstance(selector, int):
                if selector < 0:
                    index = (-selector) - 1
                    if index >= len(self.axes_below):
                        raise KeyError("Invalid index in get_axes")
                    axes.append(self.axes_below[index])
                else:
                    index = selector - 1
                    if index >= len(self.axes_above):
                        raise KeyError("Invalid index in get_axes")
                    axes.append(self.axes_below[index])
            elif isinstance(select, axis):
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
        axes = []
        for axis_position, axis in enumerate(self.get_lower_axes()):
            axes.append(
                style.set_axis_veritcal_position(
                    axis.render_style(style),
                    -axis_position+1,
                    lower_parent,
                )
            )
        for axis_position, axis in enumerate(self.get_upper_axes()):
            axes.append(
                style.set_axis_vertical_position(
                    axis.render_style(style),
                    axis_position+1,
                    lower_parent+self.count_lower_axes(),
                )
            )
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

    def __init__(self, data, **kwargs):
        try:
            test = iter(data)
        except Exception as e:
            data = [data]
        self.data = data
        self.name = kwargs.get('name', self.data[0].mnemonic)
        self.display_name = kwargs.get('display_name', self.name)

    def render_style(self, style):
        min = None
        max = None
        for datum in self.data:
            min = datum.index[0] if min is None else min(datum.index[0], min)
            max = datum.index[-1] if max is None else max(datum.index[-1], max)
        style.set_min_max(min, max)

        mnemonic = None
        if len(self.data) == 1:
            mnemonic = self.data[0].mnemonic
        return style.get_axis(self.display_name, mnemonic=mnemonic)
    
    def render_traces(self, axis_number): 
        all_traces = []
        for datum in self.data: 
           all_traces.append(go.Scattergl(
                x=datum.values,
                y=datum.index,
                mode='lines', # nope, based on data w/ default
                line=dict(color=self.get_color()), # needs to be better, based on data
                xaxis='x' + str(axis_number),
                yaxis='y',
                name = datum.mnemonic, # probably needs to be better
            ))
        return all_traces

    def get_named_tree(self):
        result = []
        for el in self.data:
            result.append(el.get_named_tree())
        return { "axis" : { self.name: result } }

class Data():
    def __init__(self, index, values, mnemonic): # Default Index?
        self.index = index
        self.values = values
        self.mnemonic = mnemonic

    def get_named_tree(self):
        return  { "data" : {'mnemonic': self.mnemonic, 'shape': self.values.shape } }