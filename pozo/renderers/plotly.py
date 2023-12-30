import copy
import math
import warnings

from IPython.display import Javascript # Part of Hack #1
import plotly.graph_objects as go
import pint

import pozo
import pozo.renderers as pzr
import pozo.themes as pzt
import pozo.units as pzu

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
    track_margin = 20,    # margin between each track
    track_start = 75,      # left-side margin on tracks # (set axis to engineering notation)
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
            gridcolor="#f0f0f0", # this needs to be generated
            showline=True,
            linewidth=2,
            tickmode= 'auto',
            nticks= 0,
            ticks="outside",
            tickwidth=1,
            ticklen=6,
            tickangle=55,
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

TRACK_WIDTH_MIN = 65
GRAPH_HEIGHT_MIN = 125
AXIS_PROPORTION_MAX = .6

class Plotly(pzr.Renderer):
    def __init__(self, template=defaults):
        self.template = copy.deepcopy(template)
        self.xaxis_template = copy.deepcopy(self.template["plotly"]["xaxis_template"])
        del self.template["plotly"]["xaxis_template"]

    def _calc_axes_proportion(self, num_axes, height):
        num_axes_adjusted = 0 if num_axes <= 1 else num_axes  # first axis is free!
        proportion_per_axis = self.template["axis_label_height"] / height
        raw_value =  num_axes_adjusted * proportion_per_axis
        if raw_value > AXIS_PROPORTION_MAX:
            raise ValueError(f"To display the {num_axes} stack axes, please use a height greater than {self.template['axis_label_height'] * num_axes_adjusted/.6}")
        return raw_value

    def _calc_track_domain(self, track_pos, num_tracks, width_per_track):
        whole_width = (self.template["track_start"] +
                       ((num_tracks-1) * self.template["track_margin"]) +
                       (num_tracks * width_per_track)
                      )
        track_start_proportion = self.template["track_start"] / whole_width
        track_margin_proportion = self.template["track_margin"] / whole_width
        non_track_proportion = track_start_proportion + ((num_tracks-1)*track_margin_proportion)

        track_width_proportion = (1-non_track_proportion) / num_tracks
        whole_track_proportion = track_width_proportion + track_margin_proportion
        start = track_start_proportion + track_pos*(whole_track_proportion)
        end = start+track_width_proportion
        return [max(start, 0), min(end, 1)]

    def get_layout(self, graph, **kwargs):
        override_theme = kwargs.pop("override_theme", None)
        track_width = kwargs.get("track_width", self.template["width_per_track"])
        if track_width < TRACK_WIDTH_MIN:
            raise ValueError("65px is minimum track width")
        height = kwargs.get("height", None)
        if not isinstance(graph, pozo.Graph):
            raise TypeError("Layout must be supplied a graph object.")
        num_tracks = len(graph)
        if not num_tracks:
            raise ValueError("There are no tracks, there is nothing to lay out.")

        layout = copy.deepcopy(self.template["plotly"])
        if height is not None:
            layout["height"] = height

        if layout["height"] < GRAPH_HEIGHT_MIN:
            raise ValueError("125px is the minimum total height")

        # first pass
        max_axes = 0
        total_axes = 0
        parent_axis_per_track = []
        for track in graph.get_tracks():
            num_axes = len(track)
            max_axes = max(max_axes, num_axes)
            parent_axis_per_track.append(total_axes+1)
            total_axes += num_axes

        layout["width"] = len(graph) * track_width
        layout["yaxis"]["domain"] = [
            0, # Old(bottom axes): self.calculate_axes_height(max_axes_bottom)
            min(1 - self._calc_axes_proportion(max_axes, layout["height"]), 1)
        ]

        ## second pass
        axes_styles = []
        ymin = float('inf')
        ymax = float('-inf')
        themes = pzt.ThemeStack(pzt.default_theme, theme = override_theme)
        themes.append(graph.get_theme())
        for track_pos, track in enumerate(graph.get_tracks()):
            themes.append(track.get_theme())
            anchor_axis = parent_axis_per_track[track_pos]
            for axis_pos, axis in enumerate(track.get_axes()):
                themes.append(axis.get_theme())
                if themes["range_unit"] is not None:
                    range_unit = pzu.registry.parse_units(themes["range_unit"])
                else:
                    range_unit = None
                data_unit = None
                print("\n")
                for datum in axis:
                    if data_unit is not None and data_unit != datum.get_unit():
                        raise pint.UnitException(data_unit, datum.get_unit(), extra_msg="Data being displayied on  one axis must be exactly the same unit.")
                    else:
                        data_unit = datum.get_unit()
                        if not (data_unit is None or range_unit is None or range_unit.is_compatible_with(data_unit)):
                            raise pint.UnitException(range_unit, data_unit, extra_msg="range_unit set by theme is not compatible with data units")
                    print(f"range: {range_unit}")
                    print(f"data: {data_unit}")
                    ymin = min(datum.get_index()[0], ymin)
                    ymax = max(datum.get_index()[-1],ymax)

                if data_unit is None: data_unit = range_unit
                if range_unit is None: range_unit = data_unit # both None, or both whatever wasn't None
                if data_unit != range_unit:
                    print("Transforming units")
                    xrange = pzu.Q(themes["range"], range_unit).m_as(data_unit)
                else:
                    print("Units not transforming")
                    xrange = themes["range"]
                color = themes["color"]

                scale_type = themes["scale"]
                axis_style = dict(
                    **self.xaxis_template
                )
                axis_style['title'] = dict(text=axis.get_name(),font=dict(color=color), standoff=0,)
                axis_style['linecolor'] = color
                axis_style['tickcolor'] = color
                axis_style['tickfont']  = dict(color=color,)

                if axis_style is not None:
                    axis_style['type'] = scale_type
                    if scale_type == "log":
                        xrange = [math.log(xrange[0], 10), math.log(xrange[1], 10)]
                if xrange is not None:
                    axis_style['range'] = xrange

                axis_style['side'] = "top" # Old(bottom axes): if position>0 else "bottom"
                if axis_pos:
                    axis_style['anchor'] = "free"
                    bottom = layout["yaxis"]["domain"][1]
                    position_above_bottom = (1-bottom) * ((axis_pos) / (max_axes - 1))
                    axis_style['position'] = min(bottom + position_above_bottom, 1)
                    axis_style['overlaying'] = "x" + str(anchor_axis)

                axis_style['domain'] = self._calc_track_domain(track_pos, num_tracks, track_width)

                axes_styles.append(axis_style)


                themes.pop()
            themes.pop()
        for i, axis in enumerate(axes_styles):
            layout["xaxis" + str(i+1)] = axis
        layout['yaxis']['maxallowed'] = ymax
        layout['yaxis']['minallowed'] = ymin
        layout['yaxis']['range'] = [ymax, ymin]
        return layout

    def get_traces(self, graph, **kwargs):
        override_theme = kwargs.pop("override_theme", None)
        traces = []
        num_axes = 1
        themes = pzt.ThemeStack(pzt.default_theme, theme = override_theme)
        themes.append(graph.get_theme())
        for track in graph:
            themes.append(track.get_theme())
            for axis in track:
                themes.append(axis.get_theme())
                all_traces = []
                for datum in axis:
                    themes.append(datum.get_theme())
                    color = themes["color"]
                    with warnings.catch_warnings():
                        warnings.filterwarnings(action='ignore', category=pint.UnitStrippedWarning, append=True)
                        all_traces.append(go.Scattergl(
                            x=datum.get_values(),
                            y=datum.get_index(),
                            mode='lines', # nope, based on data w/ default
                            line=dict(color=color, width=1), # needs to be better, based on data
                            xaxis='x' + str(num_axes),
                            yaxis='y',
                            name = datum.get_name(),
                        ))
                    themes.pop()
                num_axes += 1
                traces.extend(all_traces)
                themes.pop()
            themes.pop()
        return traces

    def render(self, graph, **kwargs):
        javascript = kwargs.pop("javascript", True)
        layout = self.get_layout(graph, **kwargs)
        traces = self.get_traces(graph, **kwargs)
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



