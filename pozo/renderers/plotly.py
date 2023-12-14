import copy
from IPython.display import Javascript # Part of Hack #1

import plotly.graph_objects as go

import pozo
import pozo.renderers as pzr

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


class Plotly(pzr.Renderer):
    def __init__(self, template=defaults):
        self.template = copy.deepcopy(template)
        self.xaxis_template = copy.deepcopy(self.template["plotly"]["xaxis_template"])
        del self.template["plotly"]["xaxis_template"]

    def randomColor(self, toNumber = 0): # gots to go
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

    def _calc_axes_proportion(self, num_axes):
        num_axes = 0 if num_axes <= 1 else num_axes  # first axis is free!
        proportion_per_axis = self.template["axis_label_height"] / self.template["plotly"]["height"]
        return num_axes * proportion_per_axis

    def _calc_track_domain(self, track_pos, num_tracks):
        non_track_space = self.template["track_start"] + ((num_tracks-1)*self.template["track_margin"])
        track_width = (1-non_track_space) / num_tracks
        whole_track_width = track_width + self.template["track_margin"]
        start = self.template["track_start"] + track_pos*(whole_track_width)
        end = start+track_width
        return [start, end]

    def get_layout(self, graph):
        if not isinstance(graph, pozo.Graph):
            raise TypeError("Layout must be supplied a graph object.")
        num_tracks = len(graph)
        if not num_tracks:
            raise ValueError("There are no tracks, there is nothing to lay out.")

        layout = copy.deepcopy(self.template["plotly"])


        # first pass
        max_axes = 0
        total_axes = 0
        parent_axis_per_track = []
        for track in graph.get_tracks():
            num_axes = len(track)
            max_axes = max(max_axes, num_axes)
            parent_axis_per_track.append(total_axes)
            total_axes += num_axes

        layout["width"] = len(graph) * self.template["width_per_track"]
        layout["yaxis"]["domain"] = [
            0, # Old(bottom axes): self.calculate_axes_height(max_axes_bottom)
            1 - self._calc_axes_proportion(max_axes)
        ]

        ## second pass
        axes_styles = []
        ymin = float('inf')
        ymax = float('-inf')
        for track_pos, track in enumerate(graph.get_tracks()):
            anchor_axis = parent_axis_per_track[track_pos]
            for axis_pos, axis in enumerate(track.get_axes()):
                for datum in axis:
                    ymin = min(datum.get_index()[0], ymin)
                    ymax = max(datum.get_index()[-1],ymax)

                color='#AAAAAA' # TODO: fix everything about color
                if datum.get_mnemonic() is not None:
                    color=self.randomColor(datum.get_mnemonic())

                axis_style = dict(
                    **self.xaxis_template
                )
                axis_style['title'] = dict(text=axis.get_name(),font=dict(color=color), standoff=0,)
                axis_style['linecolor'] = color
                axis_style['tickcolor'] = color
                axis_style['tickfont']  = dict(color=color,)

                axis_style['side'] = "top" # Old(bottom axes): if position>0 else "bottom"
                if axis_pos:
                    axis_style['anchor'] = "free"
                    bottom = layout["yaxis"]["domain"][1]
                    position_above_bottom = (1-bottom) * ((axis_pos-1) / (max_axes - 1))
                    axis_style['position'] = min(bottom + position_above_bottom, 1)
                    axis_style['overlaying'] = "x" + str(anchor_axis)

                axis_style['domain'] = self._calc_track_domain(track_pos, num_tracks)

                axes_styles.append(axis_style)

        for i, axis in enumerate(axes_styles):
            layout["xaxis" + str(i+1)] = axis
        layout['yaxis']['maxallowed'] = ymax
        layout['yaxis']['minallowed'] = ymin
        layout['yaxis']['range'] = [ymax, ymin]

        return layout

    def get_traces(self, graph):
        traces = []
        num_axes = 1
        for track in graph:
            for axis in track:
                all_traces = []
                for datum in axis:
                   all_traces.append(go.Scattergl(
                        x=datum.get_values(),
                        y=datum.get_index(),
                        mode='lines', # nope, based on data w/ default
                        line=dict(color='#000000'), # needs to be better, based on data
                        xaxis='x' + str(num_axes),
                        yaxis='y',
                        name = datum.get_name(),
                    ))
                traces.extend(all_traces) # Big UGH
                num_axes += 1
        return traces

    def render(self, graph, javascript=True):
        layout = self.get_layout(graph)
        traces = self.get_traces(graph)
        fig = go.Figure(data=traces, layout=layout)
        fig.show()
        if not javascript: return
        display(self.javascript()) # This is going to be in layout, Display

    def javascript(self):
        add_scroll = '''document.querySelectorAll('.jp-RenderedPlotly').forEach(el => el.style.overflowX = 'auto');'''

        return Javascript(add_scroll) # Part of Hack #1

# Old(bottom axes):
#        elif i < 0:
#            print("Below")
#            bottom = domain[0]
#            total_axis_space = -domain[0]
#            proportion = abs(i-1) / (self.max_axes_bottom -1 )
#
#

# We need to "implant it" (use it)
# It should fufill a couple abstracts to be valid (what is the basic API?) Something for a matlab version.
# It should _obey overrides_ (can it be forced?)
# It needs to override colors/calculations



