import plotly.graph_objects as go
import warnings
import itertools

from IPython.display import Javascript # Part of Hack #1

# Actually, this doesn't matter. If the depths are the same, it's fine.
"""
class ConflictingDepths(Exception): # Not sure if subclassing Exception is the best answer here
    def __init__(self):
        self.message = "More than one data source has a \"DEPTH\" column- TrackExplorer doesn't know which to use as a Y Axis. You can use \"yaxiname=COLUMN_NAME\" or \"maindata=DATA_SOURCE\" to disambiguate."
    def __str__(self): return self.message
"""

# Get visuals better (legend on hover, labels, colors)

# Combine Tracks

# Flatten

# Save transformation on a LAS files

# go through to-do list
# doc strings w/ tags
# get rid of legend
# make sure to reverse (autorange=reversed)
# get names up on traces
# play around with axis positioning
# combining tracks. combing traces.
# initializizers
# what if you just want a bare track, a bare axis, a bare data, what does it create
# What if you want to access tracks? We can have two functions, one plural, one singular, like HTML.
# Helper Functions
# Plotly Functions
# Dealing with widget (pausing rendering)
LAS_TYPE = "<class 'lasio.las.LASFile'>"
def randomColor(toNumber = 0):
    import random
    if toNumber != 0:
        random.seed(hash(toNumber))
    ops = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    return ops[random.randint(0, len(ops)-1)]

def scrollON():
    #return Javascript("alert('hello')")
    return Javascript('''document.querySelectorAll('.jp-RenderedPlotly').forEach(el => el.style.overflow = 'scroll');''') # Part of Hack #1

# Data must have a y axis, a value axis, and a mnemonic
class Data():
    def __init__(self, index, values, mnemonic): # so it should default to the default index if there is only one 
        self.index = index
        self.values = values
        self.mnemonic = mnemonic
    def info(self):
        return  { "data" : {'mnemonic': self.mnemonic, 'shape': self.values.shape } }

class Graph():
        
    # so, take these styles, self them (or deep copy)
    # some thing are going to be generated automatically
    # if they already exist in the temple you are supplied, ignore them
    axes_template = dict(showgrid=False, zeroline=False)
    other_styles = dict(
        showlegend = False,
        margin = dict(l=5, r=5, t=5, b=5),
        yaxis = dict(
            autorange='reversed',
            showgrid=False,
            zeroline=False
        )
    )

    # fix track name to axis name # TODO (1)
    # fix numTracks to numx axis # TODO (2)
    # make width internal calculator so it's not passed TODO (3)
    # calculate number of ticks based on width TODO (4)
    # don't use tree like that

    def _gen_style(self): # fundamentally broken because it is numAxis not numTracks
        numTracks = len(self.tracks) # TODO (2) gonna have to get axis
        axes = {}
        i = 0
        for track in self.tracks_ordered:
            for axis in track.get_all_axes():
                i+=1
                if "axis"+str(i) not in self.other_styles: # if user overrides other_styles w/ axis (which I don't recommend, don't generate it
                    axes["xaxis"+str(i)] = self.axes_template
        return_dict = dict(
            **self.other_styles,
            **axes
        )
        return return_dict
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
            
            # Process LASio LAS Object
            if str(type(ar)) == LAS_TYPE:

                ## Create Y-Axis
                # Probably need this idea of flattening y axes
                if self.yaxisname in ar.curves.keys():
                    self.yaxis.append(ar.curves[self.yaxisname].data)
                else:
                    self.yaxis.append(ar.index)
                    if not indexOK:
                        warnings.warn("No " + self.yaxisname + " column was found in the LAS data, so we're using `las.index`. set ")

                ## Create Data and Tracks
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
                    
    def draw(self):
        layout = self.get_layout()
        traces = self.get_traces()
        return go.Figure(data=traces, layout=layout)
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
        margin = .002 # default by changeable
        start = .01   # default but must change for numberline
        waste_space = start + (num_tracks-1) * margin
        width = (1 - waste_space) / num_tracks

        args = {}
        # There will be no number line here! Let's deal with that later!
        i_axes = 1
        for track in self.tracks_ordered:    
            axis_key = "xaxis"
            for i in range(1, track.count_axes()+1): # may have to seperate above and belo where to name properly
                axis_key += str(i_axes)
                final = start + width if start+width <= 1 else 1 # rounding errors
                args[axis_key] = dict(domain = [start, final], title = dict(text=track.name, font=dict(color=randomColor(track.name)))) # TODO correct name, probably not, need our own? 
                i_axes += 1
            start += width + margin
        if len(self.tracks_ordered) > 6:
            warnings.warn("If you need scroll bars, call `display(scrollON())` after rendering the graph. This is a plotly issue and we will fix it eventually.")
                
        width = len(self.tracks_ordered) * 200
        args["width"] = width
        args["height"] = 600
        layout = go.Layout(**args).update(**self._gen_style())
        return layout # this layout is not fully updated!

    def get_traces(self):
        traces = []
        tree = self.get_unnamed_tree() # really don't know if this is the best way to iterate given we need styling information for trace (its not all in layout) and this object only contains the actual data. 
        num_axes = 1
        for track in tree:
            for axis in track[0]: # these are... below
                for data in axis:
                    suffix = str(num_axes)
                    traces.append(
                        go.Scattergl(
                            x=data.values,
                            y=data.index,
                            mode='lines',
                            line=dict(color=randomColor(data.mnemonic)),
                            xaxis='x' + suffix,
                            yaxis='y',
                            name = data.mnemonic,
                        
                    ))
                num_axes += 1
            for axis in track[1]: # these are above
                for data in axis:
                    suffix = str(num_axes)
                    traces.append(
                        go.Scattergl(
                            x=data.values,
                            y=data.index,
                            mode='lines',
                            line=dict(color=randomColor(data.mnemonic)),
                            xaxis='x' + suffix,
                            yaxis='y',
                            name = data.mnemonic,
                    ))
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
        self.axes_below = [] # Probably return these as combined iterator
        self.axes_by_id = {}
        
        newAxis = Axis(data)

        if newAxis.name in self.axes:
            self.axes[newAxis.name].append(newAxis)
        else:
            self.axes[newAxis.name] = [newAxis]

        # There will have to be a switch for this TODO
        self.axes_below.append(newAxis)
        self.axes_by_id[id(newAxis)] = newAxis

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
    def get_all_axes(self):
       return list(itertools.chain(self.axes_below, self.axes_above)) 
        

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



# Dropping in your  
# -lasio LAS file
# - panda dataframe
# - welly well
# - well project
# - curve
# - whatever

# Constructing custom tracks! (several axes on one track, several curves on one axes)
# Modifying tracks and axis (combining two tracks into one track w/ two axes)
# Changing (and specifying) color schemes, Graph Schemes
# Deviation
# Getting at plotly

# they all need destructors, to indicate if they don't exist anymore

# this tree thign is bad, should probably be like "get tracks" "get axis" etc