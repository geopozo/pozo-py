import plotly.graph_objects as go
import warnings

# Actually, this doesn't matter. If the depths are the same, it's fine.
"""
class ConflictingDepths(Exception): # Not sure if subclassing Exception is the best answer here
    def __init__(self):
        self.message = "More than one data source has a \"DEPTH\" column- TrackExplorer doesn't know which to use as a Y Axis. You can use \"yaxiname=COLUMN_NAME\" or \"maindata=DATA_SOURCE\" to disambiguate."
    def __str__(self): return self.message
"""

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

class Data();
    def __init__(self, index, values, mnemonic): # so it should default to the default index if there is only one 
        self.index = index
        self.values = values
        self.mnemonic = mnemonic

class Explorer():
    def __init__(self, *args, **kwargs):

        # Essential Configuration
        self.yaxisname = kwargs.get('yaxisname',"DEPTH")

        # Random Configuration
        self.indexOK = kwargs.get('indexOK', False)

        # Objects
        # A list and its index see NOTE:ORDEREDDICT
        self.track_ordered = [] 
        self.tracks = {}
        
        self.yaxis = []

        for ar in args:
            # This is for processing a whole LASio LAS file
            if str(type(ar)) == LAS_TYPE:
                # What we're going to need to do is point this data to its Y-Axis
                if self.yaxisname in ar.curves.keys():
                    self.yaxis.append(ar.curves[self.yaxisname])
                else:
                    self.yaxis.append(ar.index)
                    if !indexOK:
                        warnings.warn("No " + self.yaxisname + " column was found in the LAS data, so we're using `las.index`. set ")
                for curve in ar.curves if curve not in {self.yaxisname}:
                    data = Data(self.yaxis[-1], curve.data, curve.mnemonic)
                    newTrack = Track(data)

                    # NOTE:ORDEREDDICT the dictionary contains multi value per key, but insert order is still maintained
                    self.track_ordered.append(newTrack)
                    if data.mnemonic is in self.tracks:
                        self.tracks[data.mnemonic].append(newTrack)
                    eslse:
                        self.tracks[data.mnemonic] = [newTrack]
                    
    
    def list_tracks(self):
        # This isn't gong to work: print(self.yaxisname + ": " + self.yaxis.shape())
        for track in self.track_ordered:
            track.list()
                    
    # def render(self):
    # def remove_track(self, *args):
    # def add_track(self, *args):
    # def list_tracks(self, *args):
    # def get_track(self, track):
    # def combine_tracks(self, track):
    # def split_tracks(self, )

# TODO: how would we accept multiple data
class Track():
    def __init__(self, data, **kwargs): # {name: data}
        self.name = kwargs.get('name', data.mnemonic) # Gets trackname from the one data
        self.display_name = kwargs.get('display_name', self.name)
        

        # This is really one object (but we can't private in python)
        self.axes = {}
        self.axes_above = []
        self.axes_below = []
        
        newAxis = Axis(data)

        if self.name is in self.axes:
            self.axes[self.name].append(newAxis)
        eslse:
            self.axes[self.name] = [newAxis]
        
        self.axes_below.append(newAxis)
        # Flag For Above and Below
        # Setting Positions 

class Axis():
    def __init__(self, data, **kwargs):
        if type(data) != list:
            self.data = [data]
        else:
            self.data = data
        self.name = kwargs.get('name', data[0].mnemonic)
        self.display_name = kwargs.get('display_name', self.name)
        
# TODO RIGHT NOW
        
# Okay, now we have to print the list
# Then I guess we have to render (which isn't that different then list, really)
# Then we have to explore different ways to add axis, add tracks, combine tracks