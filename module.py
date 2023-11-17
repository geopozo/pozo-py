import plotly.graph_objects as go
import warnings

# Actually, this doesn't matter. If the depths are the same, it's fine.
"""
class ConflictingDepths(Exception): # Not sure if subclassing Exception is the best answer here
    def __init__(self):
        self.message = "More than one data source has a \"DEPTH\" column- TrackExplorer doesn't know which to use as a Y Axis. You can use \"yaxiname=COLUMN_NAME\" or \"maindata=DATA_SOURCE\" to disambiguate."
    def __str__(self): return self.message
"""

# inspect that ugly ass error
# go through to-do list
# doc strings w/ tags


# Okay, so we need a data structure that stores actual mnemonic and a ponter to the data

# We also have axes in tracks. Both of those will have display names + keys by which to identify them.
# I think the way this goes is, you create a track, and then you can add, remove, and move axis.
# Axis can also have multiple data.
# So I think all the key access should always return a list.
# We can have two functions, one plural, one singular, like HTML.
# And we want to initialize with data fypes.
# Helper Functions
# Plotly Functions (dealing w/ key v value)
# Dealing with widget
## No idea what to do with multidimensional data
## No idea what to do with LAS3
## Declarative?

LAS_TYPE = "<class 'lasio.las.LASFile'>"

# Data must have a y axis, a value axis, and a mnemonic
class Data():
    def __init__(self, index, values, mnemonic): # so it should default to the default index if there is only one 
        self.index = index
        self.values = values
        self.mnemonic = mnemonic
    def info(self):
        return  { "data" : {'mnemonic': self.mnemonic, 'shape': self.values.shape } }

class Graph():
    def __init__(self, *args, **kwargs):

        # Essential Configuration
        self.yaxisname = kwargs.get('yaxisname',"DEPTH")

        # Random Configuration
        self.indexOK = kwargs.get('indexOK', False)

        # Objects
        # A list and its index see NOTE:ORDEREDDICT
        self.tracks_ordered = [] 
        self.tracks = {}
        self.track_by_id = {}

        self.yaxis = []

        for ar in args:
            # This is for processing a whole LASio LAS file
            if str(type(ar)) == LAS_TYPE:

                ## Create Y-Axis
                # Probably need this idea of flattening y axes
                if self.yaxisname in ar.curves.keys():
                    self.yaxis.append(ar.curves[self.yaxisname].data)
                else:
                    self.yaxis.append(ar.index)
                    if not indexOK:
                        warnings.warn("No " + self.yaxisname + " column was found in the LAS data, so we're using `las.index`. set ")

                ## Create Data and Track
                for curve in ar.curves:
                    if curve.mnemonic == self.yaxisname: continue

                    data = Data(self.yaxis[-1], curve.data, curve.mnemonic)
                    # TODO: need to check if mnemonic is modified, now!
                    newTrack = Track(data)

                    # NOTE:ORDEREDDICT- >1 value per key, but insert order is still maintained
                    self.tracks_ordered.append(newTrack)
                    if data.mnemonic in self.tracks:
                        self.tracks[data.mnemonic].append(newTrack)
                    else:
                        self.tracks[data.mnemonic] = [newTrack]
                    self.track_by_id[id(newTrack)] = newTrack
                    
    
    def get_named_tree(self):
        result = []
        for track in self.tracks_ordered:
            result.append(track.get_named_tree())
        return { 'graph': result }
    def get_unnamed_tree(self):
        result = []
        for track in self.tracks_ordered:
            result.append(track.get_unnamed_tree())
        return result
    def get_layout(self):
        num_tracks = len(self.tracks_ordered) 
        margin = .01 # this will have to be changeable
        start = .01 # this might change
        waste_space = start + (num_tracks-1) * .01
        width = (1 - waste_space) / num_tracks

        args = {}
        # There will be no number line here! Let's deal with that later!
        # We also don't know if this work
        i_axes = 1
        for track in self.tracks_ordered: # this is what we do for every track    
            axis_key = "xaxis"
            for i in range(1, track.count_axes()+1):
                axis_key += str(i_axes)
                args[axis_key] = dict(domain = [start, start + width])
                #print("args["+axis_key+"]  = dict(domain= ["+str(start)+", "+str(start + width)+"])")
                i_axes += 1
            start += width + margin
        layout = go.Layout(**args)
        return layout

    def get_traces(self):
        traces = []
        tree = self.get_unnamed_tree()
        num_axes = 1
        for track in tree:
            for axis in track[0]:
                for data in axis:
                    suffix = str(num_axes)
                    traces.append(go.Scatter(x=data.values,
                        y=data.index,
                        xaxis='x' + suffix,
                        yaxis='y'
                    ))
                    #print("go.Scatter(xaxis=x"+str(num_axes) + ")")
                num_axes += 1
            for axis in track[1]:
                for data in axis:
                    suffix = str(num_axes)
                    traces.append(go.Scatter(x=data.values,
                        y=data.index,
                        xaxis='x' + suffix,
                        yaxis='y'
                    ))
                    #print("go.Scatter(xaxis=x"+str(num_axes) + ")")
                num_axes += 1
        return traces
            

# TODO: how would we accept multiple data
# What do we do with multiple data?
# How do we organize the axis?
# If we want them on the same axis, they must pass an Axis structure
# If they pass a data, it will be wrapped in an axis
class Track():
    # TODO Track also as to take axes
    # TODO What do do with multiple data
    def __init__(self, data, **kwargs): # {name: data}
        self.name = kwargs.get('name', data.mnemonic) # Gets trackname from the one data
        self.display_name = kwargs.get('display_name', self.name)
        

        # This is really one object (but we can't private in python)
        self.axes = {}
        self.axes_above = []
        self.axes_below = []
        self.axes_by_id = {}
        
        newAxis = Axis(data)

        if newAxis.name in self.axes:
            self.axes[newAxis.name].append(newAxis)
        else:
            self.axes[newAxis.name] = [newAxis]

        # There will have to be a switch for this
        self.axes_below.append(newAxis)
        self.axes_by_id[id(newAxis)] = newAxis # c style lol
    def count_axes(self):
        return len(self.axes)

    def get_named_tree(self):
        above = []
        below = []
        for axis in reversed(self.axes_above):
            above.append(axis.get_named_tree())
        for axis in reversed(self.axes_below):
            below.append(axis.get_named_tree())
        return { "track": { self.name: { "above": above, "below": below } } }
    def get_unnamed_tree(self):
        above = []
        below = []
        for axis in reversed(self.axes_above):
            above.append(axis.get_unnamed_tree())
        for axis in reversed(self.axes_below):
            below.append(axis.get_unnamed_tree())
        return [above, below]

# Axis can take multiple data
# It will place all the data on the same axis
# What happens if the axis has multiple y data?
# If it should be on a different y axis, that's the users problem
# We should accept data, data, data and [data, data], data
# Do we allow formatting in construction?
# Will it be able to create a "pause render" function?
class Axis():
    def __init__(self, data, **kwargs):
        if type(data) != list:
            self.data = [data]
        else:
            self.data = data
        self.name = kwargs.get('name', self.data[0].mnemonic)
        self.display_name = kwargs.get('display_name', self.name)
    def get_named_tree(self):
        result = []
        for el in self.data:
            result.append(el.info())
        return { "axis" : { self.name: result } }
    def get_unnamed_tree(self):
        result = []
        for el in self.data:
            result.append(el)
        return result

# Explore ideas of creating each item individually, just take notes
# Then I guess we have to render (which isn't that different then list, really) )yes, we have to render(
# Then we have to explore different ways to add axis, add tracks, combine tracks


# Dropping in your lasio LAS file, your panda dataframe, your welly well, your well project, your curve, your whatever

# Constructing custom tracks! (several axes on one track, several curves on one axes)

# Modifying tracks and axis (combining two tracks into one track w/ two axes)

# Changing (and specifying) color schemes, Graph Schemes

# Deviation

# Getting at plotly



### Old notes
    # def render(self):
    # def remove_track(self, *args):
    # def add_track(self, *args):
    # def list_tracks(self, *args):
    # def get_track(self, track):
    # def combine_tracks(self, track):
    # def split_tracks(self, )


# they all need destructors

# this tree thign is bad, shoudl probably be like "get tracks" "get axis" etc