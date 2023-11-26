import copy
from IPython.display import Javascript # Part of Hack #1

# You can create your own dictionary like 'defaults' and 
# construct a Style() with it (pass it in as `template`)
# Specifying values that are marked as "generated" will 
# lead to undefined behavior, probably be overwritten.
# It may be better to inherit the Style() class and
# define your own class that overrides the generators.
# Furthermore, certain keywords are marked as required,
# since the generators depend on them and expect them.

defaults = dict(
    # Non-Plotly style values, used to generate Plotly layout values. These are all "required".
    width_per_track = 200,  # width of each track, used to calculate total width
    track_margin = .004,    # margin between each track # TODO should be pixels
    track_start = .01,      # left-side margin on tracks # TODO should be pixels
    axis_label_height = 60, # size of each xaxis when stacked
    
    # Plotly style values, structured like a plotly layout dictionary.
    # Important to know that `xaxes_template` will be used to create several `xaxis1`,`xaxis2`, `xaxisN` keys.
    # `xaxis_template` will not make it into the final layout dictionary passed to Plotly.
    plotly = dict(
        height = 900,          # required
        showlegend = False,
        margin = dict(l=15, r=15, t=5, b=5),
        plot_bgcolor = "#FFFFFF",
#       width=?                # generated

        yaxis = dict(
                showgrid=True,
                zeroline=False,
                gridcolor="#f0f0f0",
#               domain=[?,?],  # generated
#               maxallowed=,   # generated
#               minallowed=,   # generated
#               range=[?,?],   # generated
        ),

        xaxis_template = dict(
            showgrid=True,
            zeroline=False,
            gridcolor="#f0f0f0",
            showline=True,
            linewidth=2,
            ticks="outside",
            tickwidth=1,
            ticklen=6,
            tickangle=0,
#           side=['']              # generated
#           tickcolor=='#???',     # generated
#           linecolor='#???',      # generated
#           title=dict(
#               text="???",        # generated
#               font=dict(
#                   color="#???"   # generated
#           ),
#           tickfont=dict(
#               color="#???"       # generated
#           )
#           domain = [?,?]         # generated
#           anchor=""              # generated
#           autoshift=             # Doesn't work for x-axes!
#           position=              # generated
#           overlaying=            # generated
        ),
    ),
)
class Style:
    def __init__(self, template=defaults):
        self.template = copy.deepcopy(template)
        self.xaxis_template = copy.deepcopy(self.template["plotly"]["xaxis_template"])
        del self.template["plotly"]["xaxis_template"]

    # We don't want to modify the template, so lets copy the plotly portion
    def init_layout(self):
        self.ymin = None
        self.ymax = None
        self.max_axes_bottom = None
        self.max_axes_top = None

        self.layout_actual = copy.deepcopy(self.template["plotly"])

    # Graph will pass information and we will do some basic calculations
    def set_figure_dimensions(self, num_tracks, max_axes_bottom, max_axes_top):
        self.num_tracks = num_tracks
        self.layout_actual["width"] = num_tracks * self.template["width_per_track"]
        self.layout_actual["yaxis"]["domain"] = [
            self.calculate_axes_height(max_axes_bottom),
            1 - self.calculate_axes_height(max_axes_top)
        ]
        self.max_axes_bottom = max_axes_bottom
        self.max_axes_top = max_axes_top

    # Calculate proportional height of each axis
    def calculate_axes_height(self, num_axes):
        # num_axes as 0 and 1 are the same because both are autoaligned, so minus 1 and floor @ 0
        num_axes = max(num_axes -1, 0)
        proportion_per_axis = self.template["axis_label_height"] / self.template["plotly"]["height"]
        return num_axes * proportion_per_axis

    def calculate_track_domain(self, track_position):
        non_track_space = self.template["track_start"] + ( 
            (self.num_tracks-1) * self.template["track_margin"]
        )
        track_width = (1 - non_track_space) / self.num_tracks
        whole_track_width = track_width + self.template["track_margin"]
        start = self.template["track_start"] + track_position*(whole_track_width)
        end = start + track_width
        return [start, end]
    
    def get_layout(self):
        return self.layout_actual
    
    def set_y_limits(self):
        self.layout_actual['yaxis']['maxallowed'] = self.ymax
        self.layout_actual['yaxis']['minallowed'] = self.ymin
        self.layout_actual['yaxis']['range'] = [self.ymax, self.ymin]
        
    def set_axes(self, axes):
        for i, axis in enumerate(axes):
            self.layout_actual["xaxis" + str(i+1)] = axis
            
    def set_axis_horizontal_position(self, axis, position):
        axis['domain'] = self.calculate_track_domain(position)

    def set_axis_vertical_position(self, axis, position, parent):
        axis['side'] = "top" if position>0 else "bottom"
        if not abs(position) == 1:
            axis['anchor'] = "free"
            print(f"position: {position}")
            axis['position'] = self.get_axis_position(position)
            axis['overlaying'] = "x" + str(parent) 

    def get_axis(self, display_name, mnemonic=None):
        color='#AAAAAA' # default axis color if not set? # if no mnemonic
        if mnemonic is not None:
            color=self.randomColor(mnemonic)
        axis = dict(
            **self.xaxis_template
        )
        axis['title'] = dict( # TODO: Does this work?
            text=display_name,
            font=dict(
                color=color
            ),
            standoff=0,
        )
        axis['linecolor'] = color
        axis['tickcolor'] = color
        axis['tickfont']=dict(color=color,)
        return axis

    def get_axis_position(self, i):
        domain = self.layout_actual["yaxis"]["domain"]
        if i > 0:
            print("Above")
            bottom = domain[1]
            total_axis_space = 1-domain[1]
            proportion = abs(i-1) / (self.max_axes_top - 1 )
        elif i < 0:
            print("Below")
            bottom = domain[0]
            total_axis_space = -domain[0]
            proportion = abs(i-1) / (self.max_axes_bottom -1 )
        print(f"bottom: {bottom} and total axis space: {total_axis_space} and proportion: {proportion}")
        print(f"because: i = {i}")
        return min(bottom + total_axis_space * proportion, 1)

    def set_min_max(self, ymin, ymax):
        self.ymin = ymin if self.ymin is None else min(self.ymin, ymin)
        self.ymax = ymax if self.ymax is None else max(self.ymax, ymax)
    
    def randomColor(self, toNumber = 0):
        import random
        if toNumber != 0:
            random.seed(hash(toNumber))
        ops = ["#1f77b4",
               "#ff7f0e",
               "#2ca02c",
               "#d62728",
               "#9467bd",
               "#8c564b",
               "#e377c2",
               "#7f7f7f",
               "#bcbd22",
               "#17becf"]
        return ops[random.randint(0, len(ops)-1)]
    
    
    def javascript(self): # TODO can we really not just display this directly form here?
        add_scroll = '''document.querySelectorAll('.jp-RenderedPlotly').forEach(el => el.style.overflowX = 'auto');'''
        
        return Javascript(add_scroll) # Part of Hack #1