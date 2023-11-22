import plotly.graph_objects as go
import itertools, copy, warnings
from IPython.display import Javascript # Part of Hack #1

track_margin_default = .004
track_start_default = .01 
xaxes_template_default = dict(
    showgrid=True,
    zeroline=False,
    gridcolor="#f0f0f0",
    showline=True,
    linewidth=2,
    ticks="outside",
    tickwidth=1,
    automargin=True, # i dunno was trying to create margin, didn't work
    #tickcolor='crimson', # automatic
    ticklen=6,
    tickangle=0,
    # All generated automatically
    #linecolor='#1f77b4',
    #titlefont=dict(
    #    color="#1f77b4"
    #),
    #tickfont=dict(
    #    color="#1f77b4"
    #)
)
default_styles_default = dict(
    showlegend = False,
    margin = dict(l=15, r=15, t=25, b=5),
    yaxis = dict(
        showgrid=True,
        zeroline=False,
        gridcolor="#f0f0f0",
    ),
    height = 600,
    plot_bgcolor = "#FFFFFF",
)
default_width_per_track = 200

LAS_TYPE = "<class 'lasio.las.LASFile'>"

def randomColor(toNumber = 0):
    import random
    if toNumber != 0:
        random.seed(hash(toNumber))
    ops = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]
    return ops[random.randint(0, len(ops)-1)]

def scrollON(): # TODO can we really not just display this directly form here?
    return Javascript('''document.querySelectorAll('.jp-RenderedPlotly').forEach(el => el.style.overflow = 'scroll');''') # Part of Hack #1

class Graph():
    def __init__(self, *args, **kwargs):
        self.yaxis_max = 0
        self.yaxis_min = 30000 # it's a hack, but it'll do
        # Essential Configuration
        self.yaxisname = kwargs.get('yaxisname',"DEPTH")
        self.width_per_track = kwargs.get('width_per_track', default_width_per_track)
        self.default_styles = kwargs.get('default_styles', copy.deepcopy(default_styles_default))
        self.track_margin = kwargs.get('track_margin', track_margin_default)
        self.track_start = kwargs.get('track_start', track_start_default)
        # Random Configuration
        self.indexOK = kwargs.get('indexOK', False) # Supresses warning about using index, not column.

        # Objects
        # A list and its index see NOTE:ORDEREDDICT
        self.tracks_ordered = [] 
        self.tracks = {}
        self.track_by_id = {}
        self.yaxis = [] # Why are we storing information about the x and y axis?

        for ar in args:
            
            # Process LASio LAS Object
            if str(type(ar)) == LAS_TYPE:

                ## Create Y-Axis
                # Probably need this idea of flattening y axes
                # Oof, even max and min here is tough, what if this doesn't exist
                if self.yaxisname in ar.curves.keys():
                    self.yaxis.append(ar.curves[self.yaxisname].data)
                    self.yaxis_max = max(self.yaxis_max, ar.curves[self.yaxisname].data.max())
                    self.yaxis_min = min(self.yaxis_min, ar.curves[self.yaxisname].data.min())
                else:
                    self.yaxis.append(ar.index)
                    self.yaxis_max = max(self.yaxis_max, ar.index.max())
                    self.yaxis_min = min(self.yaxis_min, ar.index.min())
                    if not indexOK:
                        warnings.warn("No " + self.yaxisname + " column was found in the LAS data, so we're using `las.index`. set ")

                ## Create Data and Tracks ## Should be separate function
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
                    
    ## For your info
    def get_named_tree(self):
        result = []
        for track in self.tracks_ordered:
            result.append(track.get_named_tree())
        return { 'graph': result }
    
    ## Rendering Functions
    def get_layout(self):
        # default but changeable
 
        num_tracks = len(self.tracks_ordered)
        waste_space = self.track_start + (num_tracks-1) * self.track_margin
        width = (1 - waste_space) / num_tracks

        axes = {}
        i = 0
        start = self.track_start
        
        # Graph is what organize it into a layout structure
        for track in self.tracks_ordered:
            for style in track.get_axis_styles():
                i += 1
                # Style shouldn't have a domain members
                axes["xaxis" + str(i)] = dict(
                    domain = [start, min(start + width, 1)],
                    **style
                )
            start += width + self.track_margin
        if len(self.tracks_ordered) > 6: # TODO tune this number
            warnings.warn("If you need scroll bars, call `display(scrollON())` after rendering the graph. This is a plotly issue and we will fix it eventually.")   
        generated_styles = dict(
            **axes,
            width=len(self.tracks_ordered) * self.width_per_track, # probably fixed width option?
        )

        #### place some checks in here TOOO (user can edit defaults)
        self.default_styles['yaxis']['maxallowed']= self.yaxis_max
        self.default_styles['yaxis']['minallowed']= self.yaxis_min
        self.default_styles['yaxis']['range'] = [self.yaxis_max, self.yaxis_min]
        layout = go.Layout(**generated_styles).update(**self.default_styles)
        return layout

    def get_traces(self):
        traces = [] 
        num_axes = 1
        for track in self.tracks_ordered:
            for axis in track.get_all_axes():
                # if there is an update_trace, it's better to update the axis than pass a num axes
                traces.extend(axis.render_traces(num_axes))
                num_axes += 1
        return traces

    def draw(self):
        layout = self.get_layout()
        traces = self.get_traces()
        fig = go.Figure(data=traces, layout=layout)
        fig.show()
        display(scrollON()) # This is going to have some CSS mods

class Track():
    # TODO Track also as to take axes
    # TODO What do do with multiple data
    def __init__(self, data, **kwargs): # {name: data}
        self.name = kwargs.get('name', data.mnemonic) # Gets trackname from the one data
        self.display_name = kwargs.get('display_name', self.name)
        

        # This is really one object (but we can't private in python)
        self.axes = {}
        self.axes_below = [] # Considered "before" axes_above list
        self.axes_above = []
        self.axes_by_id = {}
        
        newAxis = Axis(data)

        ## add_axis function
        if newAxis.name in self.axes:
            self.axes[newAxis.name].append(newAxis)
        else:
            self.axes[newAxis.name] = [newAxis]
        self.axes_above.append(newAxis)
        self.axes_by_id[id(newAxis)] = newAxis
        # end
        
    def count_axes(self):
        return len(self.axes)

    def get_all_axes(self):
        return list(itertools.chain(self.axes_below, self.axes_above)) 
    def get_lower_axes(self):
        return self.axes_below
    def get_upper_axes(self):
        return self.axes_above

    def get_axis_styles(self):
        styles = []
        for axis in self.get_lower_axes():
            style = axis.get_style()
            style['side'] = "bottom"
            styles.append(style)
        for axis in self.get_upper_axes():
            style = axis.get_style()
            style['side'] = "top"
            styles.append(style)
        return styles

    
    ## FYI
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
        self.data = data if type(data) == list else [data]
        self.axis_template = kwargs.get('template', copy.deepcopy(xaxes_template_default))
        self.name = kwargs.get('name', self.data[0].mnemonic)
        self.display_name = kwargs.get('display_name', self.name)
        
    def get_color(self):
        return randomColor(self.data[0].mnemonic) # for now, more options later

    def get_style(self):
        color = self.get_color()
        return dict(
            title = dict(
                standoff=20, # dunno, trying to create margin, didn't work
                text=self.display_name,
                font=dict(
                    color=color
                )
            ), 
            linecolor=color,
            tickfont=dict(
                color=color,
            ),
            tickcolor=color,
            **self.axis_template,
        )

    def render_traces(self, axis_number): ## is there an update trace?
    # TODO should create several traces
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

    ##### Not sure I like these, if nothing uses them, re-evaluated them
    def get_named_tree(self): # I feel this might be useful? Tracks really can be numbers.
        result = []
        for el in self.data:
            result.append(el.get_named_tree())
        return { "axis" : { self.name: result } }

# Data must have a y axis, a value axis, and a mnemonic
class Data():
    def __init__(self, index, values, mnemonic): # so it should default to the default index if there is only one 
        self.index = index
        self.values = values
        self.mnemonic = mnemonic

    ##### Not sure I like these!
    def get_named_tree(self): # This should be just for display, so maybe a _repr_*_ function
        return  { "data" : {'mnemonic': self.mnemonic, 'shape': self.values.shape } }