import plotly.graph_objects as go
import itertools, copy, warnings

####
####
#### Utilities
####
####
def make_iter(thing):
    if isinstance(thing, str):
        return [thing]
    try:
        test = iter(thing)
        return thing
    except Exception as e:
        thing = [thing]
        return thing

def flatten_array(things):
    things2 = []
    for thing in things:
        thing = make_iter(thing)
        things2.extend(thing)
    return things2
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

    ####
    ####
    #### Basic Add-Get(s)-Remove Axis
    ####
    ####

    def get_all_axes(self):
        return list(itertools.chain(self.axes_below, self.axes_above)) 
    def get_lower_axes(self):
        return self.axes_below
    def get_upper_axes(self):
        return self.axes_above



    ## TODO change_anem and register/deregister_trakcs
    def count_axes(self):
        return len(self.axes)
    def count_lower_axes(self):
        return len(self.axes_below)
    def count_upper_axes(self):
        return len(self.axes_above)

    def has_axis(self, selector):
        return self.get_axis(selector) is not None


    def get_named_tree(self):
        return { "track": { self.name:i self.get_axes() } }


