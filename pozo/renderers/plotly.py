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
    track_margin = 15,      # margin between each track
    track_start = 35,        # left-side margin on tracks # (set axis to engineering notation) (helps with hover)
    depth_axis_width = 30,  # size of depth axis if it's not the first thing
    depth_axis_left_shift = 5,
    axis_label_height = 60, # size of each xaxis when stacked

    # Plotly style values, structured like a plotly layout dictionary.
    # Important to know that `xaxes_template` will be used to create several `xaxis1`,`xaxis2`, `xaxisN` keys.
    # `xaxis_template` will not make it into the final layout dictionary passed to Plotly.
    plotly = dict(
        height = 900,          # required
        showlegend = False,
        margin = dict(l=15, r=15, t=5, b=5),
        plot_bgcolor = '#FFFFFF',
        paper_bgcolor = '#FFFFFF',
#       width=?                # generated

        yaxis = dict(
                visible=True, # Would hdie gridelines too, so hide ticks and labels instead of axis.
                showgrid=True,
                zeroline=False,
                showline=False,
                position=0,
                gridcolor="#f0f0f0",
#               domain=[?,?],  # generated
#               maxallowed=,   # generated
#               minallowed=,   # generated
#               range=[?,?],   # generated
        ),

        xaxis_template = dict(
            showgrid=False, # TODO this is tough, grid where?
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
# different hover breaks sometimes
# different date stuff break sometimes (wasn't showing me august?)

default_hovertemplate = 'Depth: %{y}, Value: %{x}' # how to get this to be the name

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

    def _calc_total_width(self, num_tracks, total_track_width, add_depth_axis):
        whole_width = (self.template["track_start"] +
                       ((num_tracks-1) * self.template["track_margin"]) +
                       total_track_width)
        if add_depth_axis: whole_width += self.template["depth_axis_width"]
        return whole_width

    def _calc_track_domain(self, last_end, track_width, whole_width):
        # Calculating whole width is not possible
        start = (self.template["track_margin"]/whole_width) if last_end > 0 else (self.template["track_start"]/whole_width)
        start += last_end
        end = start + (track_width/whole_width)

        return [max(start, 0), min(end, 1)]

    def _hidden(self, themes):
        hidden = themes["hidden"]
        if hidden: themes.pop()
        return hidden

    def get_layout(self, graph, **kwargs):
        show_depth = kwargs.pop("show_depth", True)
        depth_axis_pos = kwargs.pop("depth_position", 0)
        depth_axis_pos_prop = 0
        if show_depth == False:
            depth_axis_pos = 0
        override_theme = kwargs.pop("override_theme", None)
        override_theme = kwargs.pop("theme_override", override_theme)
        height = kwargs.get("height", None)
        depth_range = kwargs.get("depth", None)
        if depth_range is not None and ( not isinstance(depth_range, (tuple, list)) or len(depth_range) != 2 ):
            raise TypeError(f"Depth range must be a list or tuple of length two, not {depth_range}")
        if not isinstance(graph, pozo.Graph):
            raise TypeError("Layout must be supplied a graph object.")
        if not len(graph):
            raise ValueError("There are no tracks, there is nothing to lay out.")

        layout = copy.deepcopy(self.template["plotly"])
        if height is not None:
            layout["height"] = height

        if layout["height"] < GRAPH_HEIGHT_MIN:
            raise ValueError("125px is the minimum total height")

        # first pass # work with hidden
        # print("***First pass:")
        max_axes = 0
        total_axes = 0
        parent_axis_per_track = []
        for track in graph.get_tracks():
            if pzt.ThemeStack(track.get_theme())['hidden']: continue
            num_axes = 0
            for axis in track.get_axes(): # track.get_axes(matchesTheme({hidden:true}))
                if not pzt.ThemeStack(track.get_theme())['hidden']: num_axes += 1

            max_axes = max(max_axes, num_axes)
            parent_axis_per_track.append(total_axes+1)
            total_axes += num_axes

        layout["yaxis"]["domain"] = [
            0, # Old(bottom axes): self.calculate_axes_height(max_axes_bottom)
            min(1 - self._calc_axes_proportion(max_axes, layout["height"]), 1)
        ]

        # print("***Second pass:")
        ## second pass
        axes_styles = []
        ymin = float('inf')
        ymax = float('-inf')
        y_unit = None
        total_track_width = 0

        themes = pzt.ThemeStack(pzt.default_theme, theme = override_theme)
        themes.append(graph.get_theme())
        if self._hidden(themes): return {}
        track_pos = -1
        for track in graph.get_tracks():
            themes.append(track.get_theme())
            if self._hidden(themes): continue
            track_pos += 1
            anchor_axis = parent_axis_per_track[track_pos]
            axis_pos = -1
            for axis in track.get_axes():
                themes.append(axis.get_theme())
                if self._hidden(themes): continue
                axis_pos += 1
                if themes["range_unit"] is not None:
                    range_unit = pzu.registry.parse_units(themes["range_unit"])
                else:
                    range_unit = None
                data_unit = None
                for datum in axis:
                    themes.append(datum.get_theme())
                    if self._hidden(themes): continue

                    if data_unit is not None and data_unit != datum.get_unit():
                        raise ValueError(f"Data being displayed on one axis must be exactly the same unit. {data_unit} is not {datum.get_unit()}")
                    else:
                        data_unit = datum.get_unit()
                        if not (data_unit is None or range_unit is None or range_unit.is_compatible_with(data_unit)):
                            raise pint.DimensionalityError(range_unit, data_unit, extra_msg="range_unit set by theme is not compatible with data units")
                    themes.pop()
                    if y_unit is not None and datum.get_depth_unit() is not None:
                        if y_unit != datum.get_depth_unit():
                            raise ValueError(f"All depth axis must have the same unit. You must transform the data. {y_unit} is not {datum.get_depth_unit()}")
                    y_unit = datum.get_depth_unit()
                    ymin = min(pzu.Q(datum.get_depth()[0], y_unit), pzu.Q(ymin, y_unit)).magnitude
                    ymax = max(pzu.Q(datum.get_depth()[-1], y_unit), pzu.Q(ymax, y_unit)).magnitude

                if data_unit is None: data_unit = range_unit
                if range_unit is None: range_unit = data_unit # both None, or both whatever wasn't None
                if data_unit != range_unit:
                    xrange = pzu.Q(themes["range"], range_unit).m_as(data_unit)
                else:
                    xrange = themes["range"]
                # So we've just created xrange which is the data_unit
                # But here we'd want to override ticks and such to the range unit
                color = themes["color"]

                scale_type = themes["scale"]
                axis_style = dict(
                    **self.xaxis_template
                )
                append_unit = ""
                if data_unit is not None:
                    append_unit = " (" + format(data_unit, '~') + ")"
                axis_style['title'] = dict(text=axis.get_name() + append_unit, font=dict(color=color), standoff=0,)
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
                else:
                    # All pozo-keys should not be delivered to plotly
                    axis_style['pozo-width'] = themes["track_width"]
                    total_track_width += themes["track_width"]
                    if depth_axis_pos == (track_pos+1):
                        axis_style['pozo-yaxis-end'] = True


                axes_styles.append(axis_style)


                themes.pop()
            themes.pop()
        num_tracks = track_pos + 1
        # all stuff dependent on position could go here
        last_end = 0
        layout["width"] = self._calc_total_width(num_tracks, total_track_width, depth_axis_pos)
        track = 0
        if depth_axis_pos == 0:
            layout["width"] += self.template["depth_axis_left_shift"]
            last_end += self.template["depth_axis_left_shift"]/layout["width"]
        for i, axis in enumerate(axes_styles):
            if 'overlaying' in axis:
                axis['domain'] = axes_styles[i-1]['domain']
            else:
                axis['domain'] = self._calc_track_domain(last_end, axis['pozo-width'], layout["width"])
                last_end = axis['domain'][1]
                del axis['pozo-width']
                if 'pozo-yaxis-end' in axis:
                    depth_axis_pos_prop = axis['domain'][1] + self.template["depth_axis_width"] / layout["width"] - self.template["depth_axis_left_shift"] / layout["width"]
                    last_end += self.template["depth_axis_width"] / layout["width"]
                    del axis['pozo-yaxis-end']
                track+1
            layout["xaxis" + str(i+1)] = axis
        if show_depth == False:
            layout['yaxis']['showticklabels'] = False
            layout['yaxis']['ticklen'] = 0
        elif depth_axis_pos >= num_tracks:
            layout['yaxis']['position'] = 1
        elif depth_axis_pos:
            layout['yaxis']['position'] = depth_axis_pos_prop + self.template['track_margin']/layout['width']
        layout['yaxis']['maxallowed'] = ymax
        layout['yaxis']['minallowed'] = ymin # not changing with depth_range
        if depth_range is not None:
            layout['yaxis']['range'] = [depth_range[1], depth_range[0]]
        else:
            layout['yaxis']['range'] = [ymax, ymin]
        return layout

    def get_traces(self, graph, **kwargs):
        override_theme = kwargs.pop("override_theme", None)
        override_theme = kwargs.pop("theme_override", override_theme)
        traces = []
        num_axes = 1
        themes = pzt.ThemeStack(pzt.default_theme, theme = override_theme)
        themes.append(graph.get_theme())
        if self._hidden(themes): return []
        for track in graph:
            themes.append(track.get_theme())
            if self._hidden(themes): continue
            for axis in track:
                themes.append(axis.get_theme())
                if self._hidden(themes): continue
                all_traces = []
                for datum in axis:
                    themes.append(datum.get_theme())
                    if self._hidden(themes): continue
                    color = themes["color"]
                    with warnings.catch_warnings():
                        warnings.filterwarnings(action='ignore', category=pint.UnitStrippedWarning, append=True)
                        all_traces.append(go.Scattergl(
                            x=datum.get_data(),
                            y=datum.get_depth(),
                            mode='lines', # nope, based on data w/ default
                            line=dict(color=color, width=1), # needs to be better, based on data
                            xaxis='x' + str(num_axes),
                            yaxis='y',
                            name = datum.get_name(),
                            hovertemplate = default_hovertemplate,
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



