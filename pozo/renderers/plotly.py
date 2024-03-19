import copy
import math
import warnings
import re
import weakref #unused? TODO

import numpy as np
from IPython.display import Javascript # Part of Hack #1
import plotly as plotly
import plotly.graph_objects as go
import pint

import pozo
import pozo.renderers as pzr
import pozo.themes as pzt
import pozo.units as pzu

re_space = re.compile(' ')
re_power = re.compile('\*\*')

# TODO FOR CROSSPLOT MUST X Y AND ALL COLOR HAVE THE SAME SHAPE OR ELSE BREAK INTERACTIVITY

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
    depth_axis_left_shift = 5, # what the fuck is this TODO
    axis_label_height = 60, # size of each xaxis when stacked

    # Plotly style values, structured like a plotly layout dictionary.
    # Important to know that `xaxes_template` will be used to create several `xaxis1`,`xaxis2`, `xaxisN` keys.
    # `xaxis_template` will not make it into the final layout dictionary passed to Plotly.
    plotly = dict(
        height = 900,          # required
        showlegend = True,
        legend = dict(
            yanchor = "top",
            y = 1,
            xanchor = "left",
#           x = 0,             # generated
        ),
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
        self.last_fig = None

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

    def get_layout(self, graph, xp=None, **kwargs):
        main_y_axis = "yaxis"
        if xp is not None:
            main_y_axis = "yaxis2"
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
        if xp is not None:
            layout[main_y_axis] = copy.deepcopy(layout['yaxis'])
            del layout['yaxis']
            xp.size = layout['height']
            xp.depth_range=depth_range

        if layout["height"] < GRAPH_HEIGHT_MIN:
            raise ValueError("125px is the minimum total height")

        # first pass
        # calculate: biggest main stack
        # calculate: parent axis for all
        # print("***First pass:")
        max_axis_stack = 0
        total_axes = 0 if xp is None else 1
        parent_axis_per_track = []
        for track in graph.get_tracks():
            if pzt.ThemeStack(track.get_theme())['hidden']: continue
            num_axes = 0
            for axis in track.get_axes(): # track.get_axes(matchesTheme({hidden:true}))
                if not pzt.ThemeStack(track.get_theme())['hidden']: num_axes += 1

            max_axis_stack = max(max_axis_stack, num_axes)
            parent_axis_per_track.append(total_axes+1)
            total_axes += num_axes
        layout[main_y_axis]["domain"] = [
            0, # Old(bottom axes): self.calculate_axes_height(max_axes_bottom)
            min(1 - self._calc_axes_proportion(max_axis_stack, layout["height"]), 1)
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
                    unit = format(data_unit, '~')
                    unit = re_space.sub('', unit)
                    unit = re_power.sub('^', unit)
                    append_unit = " (" + unit + ")"
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
                    bottom = layout[main_y_axis]["domain"][1]
                    position_above_bottom = (1-bottom) * ((axis_pos) / (max_axis_stack - 1))
                    axis_style['position'] = min(bottom + position_above_bottom, 1)
                    axis_style['overlaying'] = "x" + str(anchor_axis)
                else:
                    # All pozo-keys should not be delivered to plotly
                    axis_style['pozo-width'] = themes["track_width"]
                    axis_style['position'] = layout[main_y_axis]["domain"][1] # BUG PLOTLY: not needed if no xp, because position calcs automatically
                    total_track_width += themes["track_width"]
                    if depth_axis_pos == (track_pos+1):
                        axis_style['pozo-yaxis-end'] = True


                axes_styles.append(axis_style)


                themes.pop()
            themes.pop()
        num_tracks = track_pos + 1
        # all stuff dependent on position could go here
        layout["width"] = self._calc_total_width(num_tracks, total_track_width, depth_axis_pos)
        shift_for_xp = 0
        colorbar_size = 0
        depth_axis_left_shift = self.template["depth_axis_left_shift"] if depth_axis_pos == 0 else 0 # this doesn't seem well calculated
        layout["width"] += depth_axis_left_shift
        if xp is not None:
            layout["width"] += xp.size + colorbar_size
            shift_for_xp = (colorbar_size+xp.size) / (layout["width"])
            colorbar_pos = (xp.size)/layout["width"]
            xp_layout = xp.create_layout(container_width = layout["width"])
            layout["yaxis"] = xp_layout["yaxis"]
            layout["xaxis"] = xp_layout["xaxis"]
            layout["xaxis"]["domain"] = (0, colorbar_pos - 80/layout["width"]) # add some extra marign for text
            layout["legend"]["x"] = colorbar_pos * .8
        last_end = shift_for_xp + depth_axis_left_shift/layout["width"]
        track = 0
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
            axis_num = i + 1
            if xp is not None:
                axis_num += 1
            layout["xaxis" + str(axis_num)] = axis
        if show_depth == False:
            layout[main_y_axis]['showticklabels'] = False
            layout[main_y_axis]['ticklen'] = 0
        elif depth_axis_pos >= num_tracks:
            layout[main_y_axis]['position'] = 1
        elif depth_axis_pos:
            layout[main_y_axis]['position'] = depth_axis_pos_prop + self.template['track_margin']/layout['width']
        elif xp is not None:
            layout[main_y_axis]['position'] = shift_for_xp
        layout[main_y_axis]['maxallowed'] = ymax
        layout[main_y_axis]['minallowed'] = ymin # not changing with depth_range
        if depth_range is not None:
            layout[main_y_axis]['range'] = [depth_range[1], depth_range[0]]
        else:
            layout[main_y_axis]['range'] = [ymax, ymin]
        return layout

    def get_traces(self, graph, xp=None, **kwargs):
        container_width = kwargs.get("container_width", None)
        override_theme = kwargs.pop("override_theme", None)
        override_theme = kwargs.pop("theme_override", override_theme)
        traces = []
        num_axes = 1 if xp is None else 2
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
                            yaxis='y' if xp is None else 'y2',
                            name = datum.get_name(),
                            hovertemplate = default_hovertemplate,
                            showlegend = False,
                        ))
                    themes.pop()
                num_axes += 1
                traces.extend(all_traces)
                themes.pop()
            themes.pop()
        if xp is not None:
            traces.extend(xp.create_traces(container_width=container_width))
        return traces

    def render(self, graph, **kwargs): # really, what gets passed in with kwargs TODO
        xp = kwargs.pop("xp", None)
        layout = self.get_layout(graph, xp=xp, **kwargs)
        container_width = layout["width"] if xp is not None else 0
        traces = self.get_traces(graph, xp=xp, container_width=container_width, **kwargs)
        if xp is None:
            self.last_fig = go.FigureWidget(data=traces, layout=layout)
            self.last_fig._depth_axis = "yaxis1"
        else:
            self.last_fig = xpFigureWidget(data=traces, layout=layout, depth_range=xp.depth_range, renderer=xp)
            self.last_fig._depth_axis = "yaxis2"
            self.last_fig.layout.on_change(self.last_fig._depth_change_cb, 'yaxis2.range')
            xp.add_figure(self.last_fig)
        return self.last_fig

    def javascript(self):
        add_scroll = '''document.querySelectorAll('.jp-RenderedPlotly').forEach(el => el.style.overflowX = 'auto');'''

        return Javascript(add_scroll) # Part of Hack #1

def is_array(value):
    if isinstance(value, str): return False
    if hasattr(value, "magnitude"):
        return is_array(value.magnitude)
    return hasattr(value, "__len__")

class xpFigureWidget(go.FigureWidget):
    def link_depth_to(self, fig):
        fig.layout.on_change(self._depth_change_cb, fig._depth_axis+'.range', append=True)

    def __init__(self, data=None, layout=None, frames=None, skip_invalid=False, **kwargs):
        self._depth_range = kwargs.pop("depth_range", [None])
        self._xp_renderer = kwargs.pop("renderer", None)
        if self._xp_renderer is None: raise ValueError("Don't call xpFigureWidget directly, let a renderer call it so it has all it's info")
        self._depth_lock = False

        super().__init__(data=data, layout=layout, frames=frames, skip_invalid=skip_invalid, **kwargs)

    def _depth_change_cb(self, layout, new_range):
        if not self._depth_lock:
            self.set_depth_range(new_range)
        self._tracks_depth_range = new_range

    def lock_depth_range(self):
        self._depth_lock = True

    def unlock_depth_range(self):
        self._depth_lock = False
        self.match_depth_range()

    def match_depth_range(self):
        self.set_depth_range(depth_range=self._tracks_depth_range)

    def set_depth_range(self, depth_range=None): # TODO for both graphs? xp and main?
        self._depth_range = sorted(depth_range) if depth_range else None
        color_range_queue=[]
        with self.batch_update():
            for trace in self['data']:
                if not trace.meta or trace.meta.get("filter", None) != 'depth': continue
                trace.x = self._xp_renderer.x.get_data(slice_by_depth=self._depth_range)
                trace.y = self._xp_renderer.y.get_data(slice_by_depth=self._depth_range)
                color_data = trace.meta.get('color_data', None)
                if color_data == 'depth': # if xp were to change x or y, this would be wrong in renderer
                    trace.marker.color = self._xp_renderer.x.get_depth(slice_by_depth=(self._depth_range))
                elif color_data in self._xp_renderer._colors_by_id:
                    trace.marker.color = self._xp_renderer._colors_by_id[color_data].get_data(slice_by_depth=self._depth_range)
                if 'color_range' in trace.meta and trace.meta['color_range'] != (None):
                    color_range_queue.append((trace.name, trace.meta['color_range']))
        with self.batch_update(): # instead of two batches, color_range could take the new info as arguments
            for item in color_range_queue:
                self.set_color_range(item[0], color_range=item[1])

    # we have to set self._color_range so that can recalculate it when depth changes
    def set_color_range(self, name, color_range=(None), auto=False, lock=False):
        for trace in self['data']:
            if trace.meta and 'color_data' in trace.meta:
                if trace.name != name: continue
                if color_range: color_range = list(sorted(color_range))
                calc_key = 'colorscale_calculated'
                select_key = 'colorscale_selected'

                # if we never calculated or what we have is different than what we calculaed
                if (calc_key not in trace.meta
                    or trace.meta[calc_key] != trace.marker.colorscale
                    ):
                    trace.meta[select_key] = trace.marker.colorscale # its a tuple maybe it is hashable

                colorscale_selected = trace.meta[select_key]
                if auto==True or color_range==[None]:
                    trace.meta['color_range'] = (None)
                    if calc_key in trace.meta: del trace.meta[calc_key]
                    if select_key in trace.meta: del trace.meta[select_key]
                    trace.marker.colorscale = colorscale_selected
                    return

                data_min = np.nanmin(trace.marker.color)
                data_max = np.nanmax(trace.marker.color)
                if lock == True:
                    color_range = [data_min, data_max]
                trace.meta['color_range'] = color_range
                if color_range[0] is None: color_range[0] = data_min
                if color_range[1] is None: color_range[1] = data_max

                distance = data_max - data_min
                normalized_color_range = np.round((color_range - data_min) / distance, 2)
                norm_distance = normalized_color_range[1] - normalized_color_range[0]

                normalized_pairs = [] # lets create normalized pairs
                for pair in colorscale_selected:
                    normalized_pairs.append(((pair[0]*norm_distance)+normalized_color_range[0], pair[1]))
                if normalized_pairs[0][0] > 1: normalized_pairs = [(0, normalized_pairs[0][1]), (1,normalized_pairs[0][1]) ]
                elif normalized_pairs[-1][0] < 0: normalized_pairs = [(0, normalized_pairs[-1][1]), (1,normalized_pairs[-1][1]) ]
                else:
                    # can bottom be extended
                    if normalized_pairs[0][0] > 0: normalized_pairs.insert(0, (0, normalized_pairs[0][1]))
                    elif normalized_pairs[0][0] < 0:
                        lb = normalized_pairs[0]
                        ub = None
                        old_pairs = normalized_pairs.copy()
                        for pair in old_pairs:
                            if pair[0] > 0:
                                if ub == None:
                                    ub = pair
                                    #print(lb)
                                    new_color = plotly.colors.label_rgb(
                                        plotly.colors.find_intermediate_color(
                                            plotly.colors.hex_to_rgb(lb[1]),
                                            plotly.colors.hex_to_rgb(ub[1]),
                                            (-lb[0])/(ub[0]-lb[0]) # distance from 0
                                            ))
                                    #print(ub)
                                    normalized_pairs = [(0, new_color)]
                                normalized_pairs.append(pair)
                            else:
                                lb = pair
                    if normalized_pairs[-1][0] < 1: normalized_pairs.append((1, normalized_pairs[-1][1]))
                    elif normalized_pairs[-1][0] > 1:
                        ub = normalized_pairs[-1]
                        lb = None
                        old_pairs = list(reversed(normalized_pairs.copy()))
                        for pair in old_pairs:
                            if pair[0] < 1: # we're here
                                if lb == None:
                                    lb = pair
                                    # print(lb)
                                    new_color = plotly.colors.label_rgb(
                                        plotly.colors.find_intermediate_color(
                                            plotly.colors.hex_to_rgb(lb[1]),
                                            plotly.colors.hex_to_rgb(ub[1]),
                                            (1-lb[0])/(ub[0]-lb[0]) # distance from 0
                                            ))
                                    normalized_pairs = [(1, new_color)]
                                normalized_pairs.append(pair)
                            else:
                                ub = pair
                        normalized_pairs = list(reversed(normalized_pairs))
                    # if not, does it need to be truncated
                trace.marker.colorscale = tuple(normalized_pairs)
                trace.meta[calc_key] = tuple(normalized_pairs)
                # should ctime be the min max for the whole thing

class CrossPlot():
    marker_symbols = ["circle", "diamond", "square", "cross", "x", "pentagon", "start", "hexagram", "starsquare"]
    default_marker = {
            "opacity": .8,
            "size": 5
            }
    def _get_marker_no_color(self):
        marker = self.default_marker.copy()
        marker["symbol"] = self.marker_symbols[len(self.marker_symbols) % self._marker_symbol_index]
        self._marker_symbol_index += 1
        return marker

    def _get_marker_with_color(self, array, title=None, colorscale="Viridis_r", container_width=None):
        marker = self._get_marker_no_color()
        marker["color"] = array
        marker["showscale"] = True
        marker["colorscale"] = colorscale
        if container_width is not None:
            marker["colorbar"] = dict(
                    title=title,
                    orientation='h',
                    thickness=20,
                    thicknessmode='pixels',
                    x=(self.size/(2.00)-45)/container_width,
                    xref='paper',
                    y=10/self.size, # 10% margin, does this really work for all sizes?
                    yref='paper',
                    len=self.size*.9,
                    lenmode='pixels')
        else:
            marker["colorbar"] = dict(
                    title=title,
                    orientation='h',
                    thickness=20,
                    thicknessmode='pixels')
        return marker

    def _resolve_selector_to_data(self, selector):
        POZO_OBJS = (pozo.Graph, pozo.Track, pozo.Axis)
        if isinstance(selector, POZO_OBJS):
           data = selector.get_data()
           if len(data) == 0:
               raise ValueError(f"{selector} has no pozo.Data object")
           return data[0] # we process it in the following
        elif isinstance(selector, pozo.Data):
            if not is_array(selector.get_data()): raise TypeError(f"{selector}'s data seems weird: {selector.get_data()}")
            if not is_array(selector.get_depth()):raise TypeError(f"{selector}'s depth seems weird: {selector.get_depth()}")

            return selector
        raise TypeError(f"{selector} does not appear to be a pozo object, it's a {type(selector)}")

    def reinit(self, x = None, y = None, **kwargs):
        self.size                = kwargs.pop("size", self.size)
        self.depth_range         = kwargs.pop("depth_range", self.depth_range)
        self.xrange             = kwargs.pop("xrange", self.xrange)
        self.yrange             = kwargs.pop("yrange", self.yrange)
        colors                   = kwargs.pop("colors", None)
        if colors is not None:
            if not is_array(colors): colors = [colors]
            self.colors = colors
        self.y              = y if y is not None else self.y
        self.x              = x if x is not None else self.x

    def __init__(self, x=None, y=None, colors=[None], **kwargs):
        # rendering defaults
        self.size                = kwargs.pop("size", 500)
        self.depth_range         = kwargs.pop("depth_range", [None])
        self.xrange             = kwargs.pop("xrange", None)
        self.yrange             = kwargs.pop("yrange", None)
        if not is_array(colors): colors = [colors]

        self.colors = colors
        self.y = y
        self.x = x
        self._colors_by_id = {}
        self._figures_by_id = weakref.WeakValueDictionary()
        # figures will contain all the colors currently be used, if we ever have a need to audit
        # and eliminate colors_by_id that are nto necessary TODO

    @property
    def colors(self):
        return self.__colors

    @colors.setter
    def colors(self, colors):
        self.__colors = []
        for color in colors:
            if color is None:
                self.__colors.append(None)
            elif isinstance(color, str) and color.lower() == "depth":
                self.__colors.append("depth")
            else:
                self.__colors.append(self._resolve_selector_to_data(color))

    @property
    def x(self):
        return self.__x
    @x.setter
    def x(self, x):
        self.__x = self._resolve_selector_to_data(x) if x is not None else None

    @property
    def y(self):
        return self.__y
    @y.setter
    def y(self, y):
        self.__y = self._resolve_selector_to_data(y) if y is not None else None

    def create_layout(self, container_width=None):
        margin = (120) / self.size if container_width is not None else 0
        return dict(
            width       = self.size,
            height      = self.size,
            xaxis       = dict(
                            title = self.x.get_name(),
                            range = self.xrange,
                            linecolor = "#888",
                            linewidth = 1,
            ),
            yaxis       = dict(
                            title = self.y.get_name(),
                            range = self.yrange,
                            domain = (margin, 1),
                            linecolor = "#888",
                            linewidth = 1,
            ),
            showlegend  = True
        )

    def create_trace(self, color, **kwargs):
        depth_range = kwargs.pop("depth_range", self.depth_range)
        container_width = kwargs.get("container_width", None)
        trace = self._base_trace.copy()
        trace['meta']={'filter':'depth'}
        if color is not None:
            if isinstance(color, str) and color.lower() == "depth":
                trace['meta']['color_data'] = 'depth'
                color_array = self.x.get_depth(slice_by_depth=depth_range)
            else:
                color_data = self._resolve_selector_to_data(color)
                color_array = color_data.get_data(slice_by_depth=depth_range)
                trace['meta']['color_data'] = id(color)
                self._colors_by_id[id(color)] = color

            name = color_data.get_name() if color != "depth" else "depth"
            trace['name'] = name
            trace['marker'] = self._get_marker_with_color(color_array, name, container_width=container_width)
            trace['hovertemplate'] = '%{x}, %{y}, %{marker.color}'
            trace['visible'] = 'legendonly'
        else:
            trace['marker'] = self._get_marker_no_color()
            trace['name'] = "x"
        return trace

    def create_traces(self, container_width=None, **kwargs):
        depth_range = kwargs.pop("depth_range", self.depth_range)
        x_data = self.x.get_data(slice_by_depth=depth_range)
        y_data = self.y.get_data(slice_by_depth=depth_range)
        self._marker_symbol_index = 1

        # Doing some stats
        missing = (np.isnan(x_data) + np.isnan(y_data)).sum() # TODO improve with more statistics, how many values are there, etc
        display(f"Number of unplottable values: {missing} ({(100 * missing/len(x_data)):.1f}%)")

        self._base_trace = dict(
            x = x_data,
            y = y_data,
            mode='markers',
        )

        # Make Traces
        trace_definitions = []
        plotly_traces     = []
        for color in self.colors:
            trace_definitions.append(self.create_trace(color, container_width=container_width, depth_range=depth_range))
        if trace_definitions and 'visible' in trace_definitions[0]: del trace_definitions[0]['visible']

        for trace in trace_definitions:
            plotly_traces.append(go.Scattergl(trace))
        return plotly_traces

    def add_figure(self, fig):
        self._figures_by_id[id(fig)] = fig

    def render(self, **kwargs):
        depth_range = kwargs.get("depth_range", self.depth_range)
        layout = self.create_layout(**kwargs)
        traces = self.create_traces(**kwargs)

        # if none, it it is min and max
        fig = xpFigureWidget(data=traces, layout=layout, depth_range=depth_range, renderer=self) # how do we set depth range here
        self.add_figure(fig)
        self.last_fig = fig

        return fig
