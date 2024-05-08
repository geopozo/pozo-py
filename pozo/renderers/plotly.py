# does autoshift work?
# https://plotly.com/python/multiple-axes/#automatically-shifting-axes
import copy
import os
import math
import warnings
import re
import weakref
import multiprocessing
import itertools
from ipywidgets import IntProgress

import numpy as np
from IPython.display import Javascript, display # Part of Hack #1
import plotly as plotly
import plotly.graph_objects as go
import pint

import pozo
import pozo.renderers as pzr
import pozo.themes as pzt
import pozo.units as pzu

re_space = re.compile(' ')
re_power = re.compile(r'\*\*')

warnings.filterwarnings("ignore", category=UserWarning, message="Message serialization failed with")

def toTarget(axis):
    return axis[0] + axis[-1]

def javascript():
    add_scroll = '''var css = '.plot-container { overflow: auto; }',
head = document.getElementsByTagName('head')[0],
style = document.createElement('style');

style.type = 'text/css';
if (style.styleSheet){
  style.styleSheet.cssText = css;
} else {
  style.appendChild(document.createTextNode(css));
}
console.log("Executed javascript()")
head.appendChild(style);'''
    display(Javascript(add_scroll))

javascript()

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
    depth_axis_width = 35,  # size of depth axis if it's not the first thing, will also have margin above
    axis_label_height = 80, # size of each xaxis when stacked
    y_annotation_gutter = 10, # space for writing text

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

        yaxis1 = dict(
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

# move this?
def is_array(value):
    warnings.warn("is_array should be used from pozo", DeprecationWarning)
    if isinstance(value, str): return False
    if hasattr(value, "magnitude"):
        return is_array(value.magnitude)
    return hasattr(value, "__len__")

# So this renderer will have a list of tracks, and their contained axis, but not the data
# Its all position data, not styling data
class Plotly(pzr.Renderer):
    def __init__(self, template=defaults):
        javascript() # double it up
        self.template = copy.deepcopy(template)
        self.xaxis_template = copy.deepcopy(self.template["plotly"]["xaxis_template"])
        del self.template["plotly"]["xaxis_template"]
        self.last_fig = None

    def _hidden(self, themes, override=False):
        hidden = themes["hidden"]
        if hidden or override: themes.pop()
        return hidden or override

    def _process_note(self, note, xref, yref, left_margin=0):
        def _make_shape(note, xref, yref):
            x_lower_bound = 0
            x_upper_bound = 1
            if note.width > 0:
               x_upper_bound = note.width
            elif note.width < 0:
               x_lower_bound = 1 + note.width

            shape = dict(
                    xref    =  xref,
                    x0      =  x_lower_bound+left_margin,
                    x1      =  x_upper_bound,
                    yref    =  yref
                    )
            default_line = dict(
                    color   = 'black',
                    width   = 1,
                    dash    = 'dot',
            )
            if pozo.is_array(note.depth) and len(note.depth) == 2:
                shape['type']       = 'rect'
                shape['y0']         = note.depth[0]
                shape['y1']         = note.depth[1]
                default_line['width'] = 0
                default_line.update(note.line)
                shape['line']       = default_line
                shape['fillcolor']  = note.fillcolor
                shape['layer']      = "above"
                shape['opacity']    = .5
            elif pozo.is_scalar_number(note.depth):
                shape['type']               = 'line'
                shape['y0'] = shape['y1']   = note.depth
                default_line.update(note.line)
                shape['line']               = default_line
            else:
                raise TypeError("Range must be a number or two numbers in a tuple or list")
            return shape
        def _make_note(note, xref, yref, is_line): # if graph,
            annotation = dict(
                text=note.text,
                axref   = xref if xref != 'paper' else None,
                ayref   =  yref if yref != 'paper' else None,
                xref=xref, # could be domain or paper
                x=1,
                yref=yref,
                y=note.depth if is_line else note.depth[0],
                yshift=-5,
                showarrow=False,
            )
            return annotation
        shape = _make_shape(note, xref, yref)
        annotation = None
        if note.show_text:
            annotation = _make_note(note, xref, yref, shape['type'] == 'line')
        return shape, annotation

    def get_layout(self, graph, xp=None, **kwargs):
        if not isinstance(graph, pozo.Graph):
            raise TypeError("Layout must be supplied a graph object.")
        if not len(graph):
            raise ValueError("There are no tracks, there is nothing to lay out.")
        show_depth = kwargs.pop("show_depth", True)
        depth_axis_position = kwargs.pop("depth_position", 0)
        override_theme = kwargs.pop("override_theme", None)
        override_theme = kwargs.pop("theme_override", override_theme)
        height = kwargs.get("height", None)
        depth_range = kwargs.get("depth", None)
        if depth_range is not None and ( not isinstance(depth_range, (tuple, list)) or len(depth_range) != 2 ):
            raise TypeError(f"Depth range must be a list or tuple of length two, not {depth_range}")

        layout = copy.deepcopy(self.template["plotly"])
        if height is not None:
            layout["height"] = height
        if layout["height"] < GRAPH_HEIGHT_MIN:
            raise ValueError("125px is the minimum total height")

        tracks_y_axis = "yaxis1"
        xp_y_axis = None
        xp_x_axis = None
        if xp is not None:
            tracks_y_axis = "yaxis2"
            xp_y_axis = "yaxis1"
            xp_x_axis = "xaxis1"
            layout[tracks_y_axis] = copy.deepcopy(layout['yaxis1'])
            del layout['yaxis1']
            # Honestly all communication between renderers should maybe not happen inside any get_layout
            # nor any get_trace

        # TODO constrain positions and domains

        # posmap is an object eventual assigned to the figure containing axis/graph/position data.
        # it's used to pull out reference numbers easily
        posmap = {
            'xp_x': xp_x_axis,
            'xp_y': xp_y_axis,
            'track_y': tracks_y_axis,
            'pixel_height': layout['height'],
            'pixel_width': 4, # start drawing axes at 4 makes it look a little nicer on the left
            'pixel_cursor': 4,
            'with_xp': xp is not None,
            'xp_end': 0,
            'show_depth': show_depth,
            'depth_track_number': depth_axis_position if show_depth else 0, # putting at 0 easier if turned off
            'depth_auto_left': not depth_axis_position, # weird because if `width_xp` this should be false, but logic works
            'depth_auto_right': False, # calc later
            'tracks_axis_numbers': [],
            'tracks_pixel_widths': [],
            'tracks_x_domains': [],
            'tracks_y_domain': None,
            'axis_line_positions': [],
            'total_axes': int(xp is not None),
            'y_bottom': self.template['y_annotation_gutter']/layout['height'],
            'axis_number_to_Axis': {},
            'trace_id_to_axis_number': {}, # same trace multiple times will break this, TODO, gotta fix plotly first to not need it
            'cross_axis_fills': {}, # this would be a dictionary source: , sink: , shadow_trace: calculated at the end of layout
            # we need a
            }

        effectively_hidden = {}
        # we do a lot of Y calculations in the first run
        max_axis_stack = 0
        track_index = -1
        for track in graph.get_tracks():
            stack = pzt.ThemeStack(track.get_theme())
            if not stack['force'] and ( stack['hidden'] or len(track)==0 ):
                effectively_hidden[id(track)] = True
                continue
            track_index += 1
            if track_index and posmap['depth_track_number'] == track_index:
                posmap['tracks_axis_numbers'].append("depth")
            posmap['tracks_axis_numbers'].append([])
            axes_exist = True if stack['force'] else False
            axis_index = -1
            for axis in track.get_axes():
                if pzt.ThemeStack(axis.get_theme())['hidden']:
                    effectively_hidden[id(axis)] = True
                    continue
                traces_exist = False
                trace_ids = []
                for trace in axis.get_traces():
                    if not pzt.ThemeStack(trace.get_theme())['hidden']:
                        traces_exist = True
                        trace_ids.append(id(trace))
                    else:
                        effectively_hidden[id(trace)] = True
                if not traces_exist:
                    effectively_hidden[id(axis)] = True
                    continue
                axis_index += 1
                axes_exist = True
                posmap['total_axes'] += 1 # plotly axis indicies are base 1 so increment first
                posmap['tracks_axis_numbers'][-1].append(posmap['total_axes'])
                posmap['axis_number_to_Axis'][posmap['total_axes']] = axis
                for trace_id in trace_ids:
                    posmap['trace_id_to_axis_number'][trace_id] = posmap['total_axes']
            if axis_index == -1 and stack['force']:
                posmap['total_axes'] += 1 # plotly axis indicies are base 1 so increment first
                posmap['tracks_axis_numbers'][-1].append(posmap['total_axes'])
                posmap['axis_number_to_Axis'][posmap['total_axes']] = axis
                # there will be a trace here but it will be a dummy trace
            if not axes_exist:
                effectively_hidden[id(track)] = True
                if track_index and posmap['depth_track_number'] == track_index: posmap['tracks_axis_numbers'].pop()
                posmap['tracks_axis_numbers'].pop()
                track_index -= 1
            max_axis_stack = max(len(posmap['tracks_axis_numbers'][-1]), max_axis_stack) if track_index != -1 else 0
        if not max_axis_stack: raise ValueError("Didn't find any axes, not going to render")
        if max_axis_stack == 1: posmap['axis_line_positions'] = [1]
        elif max_axis_stack > 1:
            for i in reversed(range(max_axis_stack+1)):
                posmap['axis_line_positions'].append(
                    1 - i * (self.template["axis_label_height"]/posmap['pixel_height'])
                    )
        layout[tracks_y_axis]["domain"] = posmap['tracks_y_domain'] = ( posmap['y_bottom'], posmap['axis_line_positions'][0] )
        if posmap['depth_track_number'] >= len(posmap['tracks_axis_numbers']):
            posmap['depth_auto_right'] = True
        max_text = 0
        for note in itertools.chain(list(graph.note_dict.values()) + graph.note_list):
            max_text = max(max_text, len(note.text))
        posmap['x_annotation_pixel_width'] = max_text*10
        posmap['pixel_width'] += max_text*10

        ## in the second pass, we apply units and styles, and information from the first run
        axes_styles = [] # why not declare axes_styles earlier and then apply axes styles from the start, instead of here

        ymin = float('inf')
        ymax = float('-inf')
        y_unit = None

        themes = pzt.ThemeStack(pzt.default_theme, theme = override_theme)
        themes.append(graph.get_theme())
        if self._hidden(themes): return {}

        track_index = -1 # we can't use enumerate() becuase sometimes we skip iterations in the loop
        for track in graph.get_tracks():
            themes.append(track.get_theme())
            if not themes['force'] and ( self._hidden(themes, id(track) in effectively_hidden) or len(track) == 0 ): continue
            track_index += 1
            if track_index and posmap['tracks_axis_numbers'][track_index] == 'depth': # don't do it for 0
                track_index +=1
                posmap['tracks_pixel_widths'].append(self.template['depth_axis_width'])

            axis_index = -1 # same story with track_index, need to skip iterations, enumerate() won't work
            for axis in track.get_axes():
                themes.append(axis.get_theme())
                if self._hidden(themes, id(axis) in effectively_hidden): continue
                axis_index += 1

                xrange_raw = themes["range"]
                scale_type_raw = themes["scale"]
                range_unit_raw = themes["range_unit"]
                for trace in axis:
                    if xrange_raw and scale_type_raw and range_unit_raw: break
                    themes.append(trace.get_theme())
                    if self._hidden(themes, id(trace) in effectively_hidden): continue
                    if xrange_raw is None: xrange_raw = themes["range"]
                    if scale_type_raw is None: scale_type_raw = themes["scale"]
                    if range_unit_raw is None: range_unit_raw = themes["range_unit"]
                    themes.pop()

                if range_unit_raw is not None:
                    range_unit = pzu.registry.parse_units(range_unit_raw)
                else:
                    range_unit = None
                data_unit = None
                # this might work for locking them together scaleanchor = False, see other comments
                for trace in axis:
                    themes.append(trace.get_theme())
                    if self._hidden(themes, id(trace) in effectively_hidden): continue

                    if 'cross_axis_fill' in themes:
                        caf = themes['cross_axis_fill']
                        if isinstance(caf, str):
                            if caf not in posmap['cross_axis_fills']:
                                posmap['cross_axis_fills'][caf] = {}
                            # else get the sink
                            # get the axis for that sink
                            # constrain that to myself
                            posmap['cross_axis_fills'][caf]['source'] = trace
                        elif isinstance(caf, (tuple, list)):
                            if caf[0] not in posmap['cross_axis_fills']:
                                posmap['cross_axis_fills'][caf[0]] = {}
                            # else get the source trace
                            # get the axis for that source trace
                            # and use that to constrain myself (in this loop)
                            posmap['cross_axis_fills'][caf[0]]['sink'] = trace

                    if data_unit is not None and data_unit != trace.get_unit():
                        raise ValueError(f"Data being displayed on one axis must be exactly the same unit. {data_unit} is not {trace.get_unit()}")
                    else:
                        data_unit = trace.get_unit()
                        if not (data_unit is None or range_unit is None or range_unit.is_compatible_with(data_unit)):
                            raise pint.DimensionalityError(range_unit, data_unit, extra_msg="range_unit set by theme is not compatible with data units")
                    themes.pop()
                    if y_unit is not None and trace.get_depth_unit() is not None:
                        if y_unit != trace.get_depth_unit():
                            raise ValueError(f"All depth axis must have the same unit. You must transform the data. {y_unit} is not {trace.get_depth_unit()}")
                    y_unit = trace.get_depth_unit()
                    ymin = min(pzu.Q(trace.get_depth()[0], y_unit), pzu.Q(ymin, y_unit)).magnitude
                    ymax = max(pzu.Q(trace.get_depth()[-1], y_unit), pzu.Q(ymax, y_unit)).magnitude

                if data_unit is None: data_unit = range_unit
                if range_unit is None: range_unit = data_unit # both None, or both whatever wasn't None


                if data_unit != range_unit:
                    xrange = pzu.Q(xrange_raw, range_unit).m_as(data_unit)
                else:
                    xrange = xrange_raw
                # So we've just created xrange which is the data_unit
                # But here we'd want to override ticks and such to the range unit
                color = themes["color"]

                scale_type = scale_type_raw
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

                axis_style['type'] = scale_type
                if scale_type == "log":
                    xrange = [math.log(xrange[0], 10), math.log(xrange[1], 10)]
                if xrange is not None:
                    axis_style['range'] = xrange

                axis_style['side'] = "top"
                if axis_index: # is a secondary axis
                    axis_style['anchor'] = "free" # TODO we might be able to just change this, check
                    axis_style['overlaying'] = "x" + str(posmap['tracks_axis_numbers'][track_index][0])
                # TODO why do we need position on automatically anchored axis in the case of XP? (from previous comment)
                axis_style['position'] = min(posmap['axis_line_positions'][axis_index], 1)
                axes_styles.append(axis_style)
                themes.pop()
            if themes['force'] and axis_index == -1: axes_styles.append({}) # create a dummy axis for a forced empty track
            posmap['pixel_width'] += themes["track_width"] + self.template["track_margin"]
            posmap['tracks_pixel_widths'].append(themes["track_width"])
            themes.pop()
        posmap['pixel_width'] -= self.template["track_margin"] # we don't need margin at the end
        if posmap['depth_track_number'] > 0: posmap['pixel_width'] += self.template['depth_axis_width'] # We'll need space

        # all stuff dependent on position could go here
        if xp is not None:
            posmap["pixel_width"] += layout["height"] # create a square for the crossplot
            if posmap['depth_auto_left']:
                posmap["pixel_width"] += self.template['depth_axis_width']
            posmap['xp_end'] = layout["height"] / (posmap["pixel_width"])
            xp_layout = xp.create_layout(container_width = posmap["pixel_width"], size = layout["height"]) # pre posmap
            layout[xp_y_axis] = xp_layout["yaxis1"]
            layout[xp_x_axis] = xp_layout["xaxis1"]
            layout[xp_x_axis]["domain"] = (0, posmap['xp_end'])
            posmap["xp_domain"] = layout[xp_x_axis]["domain"]
            layout["legend"]["x"] = posmap['xp_end'] * .8
            posmap['pixel_cursor'] += layout["height"]
            if posmap['depth_auto_left']: posmap['pixel_cursor'] += self.template['depth_axis_width']
        track = 0
        i = -1
        hackshapes = []
        for axis in axes_styles:
            dummy = len(axis) == 0
            if dummy:
                axis['visible'] = False
                axis['showgrid'] = False
                axis['zeroline'] = False
                axis['showline'] = False
                axis['fixedrange'] = True #scale anchor might be beter
                axis['side'] = 'top'
                axis['position'] = posmap['tracks_y_domain'][1]
                hackshape_x = (posmap['pixel_cursor']/posmap['pixel_width'],
                               (posmap['pixel_cursor']+posmap['tracks_pixel_widths'][track])/posmap['pixel_width'])
                hackshape = dict(xref='paper',
                                 x0 = hackshape_x[0],
                                 x1 =  hackshape_x[1],
                                 yref = 'paper',
                                 type= 'rect',
                                 y0= 1,
                                 y1= posmap['tracks_y_domain'][1],
                                 fillcolor=defaults['plotly']['paper_bgcolor'],
                                 line= {'width':0}
                                 )
                hackshapes.append(hackshape)
            i += 1
            if 'overlaying' in axis:
                axis['domain'] = axes_styles[i-1]['domain']
            else:
                axis['domain'] = (posmap['pixel_cursor']/posmap['pixel_width'],
                                  (posmap['pixel_cursor']+posmap['tracks_pixel_widths'][track])/posmap['pixel_width'])
                posmap['pixel_cursor'] += posmap['tracks_pixel_widths'][track]+self.template["track_margin"]
                posmap['tracks_x_domains'].append(axis['domain'])
                track+= 1
                if ( track < len(posmap['tracks_axis_numbers']) and
                    posmap['tracks_axis_numbers'][track] == 'depth'
                ): # never checks track 0, that's auto
                    track+=1
                    layout[tracks_y_axis]['position'] = (-4 + posmap['pixel_cursor'] + self.template['depth_axis_width'])/posmap['pixel_width']
                    posmap['tracks_x_domains'].append((posmap['pixel_cursor']/posmap['pixel_width'], layout[tracks_y_axis]['position']))
                    posmap['pixel_cursor'] += self.template['depth_axis_width']
            layout["xaxis" + str(i + 1 + int(xp is not None))] = axis
        if not show_depth:
            layout[tracks_y_axis]['showticklabels'] = False
            layout[tracks_y_axis]['ticklen'] = 0
            layout[tracks_y_axis]['ticks'] = ""
        elif posmap['depth_auto_right']:
            layout[tracks_y_axis]['position'] = 1 - posmap['x_annotation_pixel_width']/posmap['pixel_width']
        elif posmap['depth_auto_left'] and xp is not None:
            layout[tracks_y_axis]['position'] = posmap['xp_end'] + self.template['depth_axis_width']/posmap['pixel_width']
        layout[tracks_y_axis]['maxallowed'] = ymax
        layout[tracks_y_axis]['minallowed'] = ymin
        if depth_range is not None:
            layout[tracks_y_axis]['range'] = [depth_range[1], depth_range[0]]
        else:
            layout[tracks_y_axis]['range'] = [ymax, ymin]
        layout['width']=posmap['pixel_width']
        posmap['effectively_hidden'] = effectively_hidden


        # TODO: add verts and track depth/ranges, it could be condensed into just passing posmap
        depth_margin = 0
        if (posmap['depth_auto_left'] and posmap['with_xp']):
            depth_margin = self.template['depth_axis_width']/posmap['pixel_width']
        layout['shapes'] = []
        layout['annotations'] = []
        for note in itertools.chain(list(graph.note_dict.values()) + graph.note_list):
            s, a = self._process_note(note,
                                      xref="paper",
                                      yref=toTarget(posmap['track_y']),
                                      left_margin = posmap['xp_end']+depth_margin)
            if s: layout['shapes'].append(s)
            if a: layout['annotations'].append(a)

        themes = pzt.ThemeStack(pzt.default_theme, theme = override_theme)
        themes.append(graph.get_theme())
        if self._hidden(themes): return {}
        track_index = -1 + bool(posmap['with_xp'])# we can't use enumerate() becuase sometimes we skip iterations in the loop
        for track in graph.get_tracks():
            themes.append(track.get_theme())
            if not themes['force'] and ( self._hidden(themes, id(track) in effectively_hidden) or len(track) == 0 ): continue
            track_index += 1
            if not bool(posmap['with_xp']) and posmap['tracks_axis_numbers'][track_index] == "depth":
                track_index +=1
            for note in itertools.chain(list(track.note_dict.values()) + track.note_list):
                s, a = self._process_note(note,
                                          xref='x'+str(posmap['tracks_axis_numbers'][track_index][0]) + ' domain',
                                          yref=toTarget(posmap['track_y']))
                if s: layout['shapes'].append(s)
                if a: layout['annotations'].append(a)

        layout['shapes'].extend(hackshapes)
        posmap['layout'] = layout
        self._last_posmap = posmap
        return layout

    def get_traces(self, graph, yaxis='y1', xstart=1, **kwargs):
        override_theme = kwargs.pop("override_theme", None)
        override_theme = kwargs.pop("theme_override", override_theme)
        traces = []
        num_axes = xstart
        themes = pzt.ThemeStack(pzt.default_theme, theme = override_theme)
        themes.append(graph.get_theme())
        if self._hidden(themes): return []
        for track in graph:
            themes.append(track.get_theme())
            if not themes['force'] and self._hidden(themes): continue
            if themes['force'] and len(track) == 0:
                traces.append(
                        go.Scatter(
                            x=[0],
                            y=[0],
                            mode='markers',
                            xaxis='x' + str(num_axes),
                            yaxis=toTarget(yaxis),
                            showlegend=False,
                            opacity=0,
                            hoverinfo='skip',
                            )
                        )
                num_axes += 1
                continue
            for axis in track:
                themes.append(axis.get_theme())
                if self._hidden(themes): continue
                all_traces = []
                traces_exist = False
                for trace in axis:
                    themes.append(trace.get_theme())
                    if self._hidden(themes): continue
                    traces_exist = True
                    color = themes["color"]
                    with warnings.catch_warnings():
                        warnings.simplefilter("default")
                        warnings.filterwarnings(action='ignore', category=pint.UnitStrippedWarning, append=True)
                        fill = None
                        fillcolor = 'blue' if 'fillcolor' not in themes else themes['fillcolor']
                        heatmap = False
                        shadow_data = None
                        if 'fill' in themes:
                            if themes['fill'] == 'heatmap':
                                heatmap = True
                                fill = 'tozerox'
                                fillcolor = 'white'
                            else:
                                fill = themes['fill']
                        elif 'cross_axis_fill' in themes:
                            if isinstance(themes['cross_axis_fill'], (list, tuple)):
                                assert id(trace) in self._last_posmap['trace_id_to_axis_number']
                                caf_name = themes['cross_axis_fill'][0]
                                assert caf_name in self._last_posmap['cross_axis_fills']
                                sink_range = self._last_posmap['layout']['xaxis'+str(num_axes)]['range']
                                source_trace = self._last_posmap['cross_axis_fills'][caf_name]['source']
                                source_axis = self._last_posmap['trace_id_to_axis_number'][id(source_trace)]
                                source_range = self._last_posmap['layout']['xaxis' + str(source_axis)]['range']
                                sink_distance = sink_range[1] - sink_range[0]
                                source_distance = source_range[1] - source_range[0]
                                point_scale = sink_distance/source_distance
                                point_shift = sink_range[0] - (source_range[0] * point_scale)
                                shadow_data = source_trace.get_data(clean=True) * point_scale + point_shift
                                # we will lock both axes completely but it seems like mutual zoom operations are ok
                                # notes above on how to do that

                        all_traces.append(go.Scatter(
                            x=trace.get_data(clean=True),
                            y=trace.get_depth(clean=True),
                            mode='lines', # nope, based on data w/ default
                            line=dict(color=color, width=1), # needs to be better, based on data
                            xaxis='x' + str(num_axes),
                            yaxis=toTarget(yaxis),
                            name = trace.get_mnemonic(),
                            hovertemplate = default_hovertemplate,
                            showlegend = False,
                            fill = fill,
                            fillcolor = fillcolor,
                            ))
                        if shadow_data is not None:
                            all_traces.append(go.Scatter(
                                x=shadow_data,
                                y=trace.get_depth(clean=True),
                                mode='lines', # nope, based on data w/ default
                                line=dict(color='black', width=0), # needs to be better, based on data
                                xaxis='x' + str(num_axes),
                                yaxis=toTarget(yaxis),
                                name = source_trace.get_mnemonic() + "-shadow",
                                showlegend = False,
                                fill = 'tonextx',
                                fillcolor = fillcolor
                                ))
                        if heatmap:
                            data = trace.get_data(clean=True)
                            min = np.nanmin(data)
                            max = np.nanmax(data)
                            heatmap = go.Heatmap(
                                        z = [[x] for x in data],
                                        xaxis='x' + str(num_axes),
                                        yaxis=toTarget(yaxis),
                                        y = trace.get_depth(clean=True),
                                        x = [max*2,min],
                                        showlegend=False,
                                        showscale=False,
                                        hoverinfo='skip',
                                        )
                            all_traces.append(heatmap)
                    themes.pop()
                    if traces_exist: num_axes += 1
                    traces.extend(all_traces)
                themes.pop()
            themes.pop()
        return traces


    def summarize_curves(self, graph, selectors=None, **kwargs):
        theme = kwargs.pop("theme", "cangrejo")
        traces = {}
        def update(array):
            for item in array:
                if id(item) in traces: continue
                traces[id(item)] = item
        exclude = kwargs.get("exclude", None)
        depth = kwargs.get("depth", None)
        height= kwargs.get("height", None)

        if selectors is None or not selectors:
            update(graph.get_traces(exclude=exclude)) #exclude by position is buggy TODO
        else:
            for selector in selectors:
                if selector is None:
                    update(graph.get_traces(exclude=exclude))
                if isinstance(selector, pozo.Trace):
                    update([selector])
                elif isinstance(selector, (pozo.Axis, pozo.Track, pozo.Graph)):
                    update(selector.get_traces(exclude=exclude))
                else:
                    update(graph.get_traces(selector, exclude=exclude))
        temp_graph = pozo.Graph(list(traces.values()))
        temp_graph.set_theme(theme)
        layout = temp_graph.renderer.get_layout(
                temp_graph,
                xp=None,
                depth=depth,
                height=height,
                override_theme={"color": "black", "track_width": 300}
                )
        layout['yaxis1']['domain'] = (.2, layout['yaxis1']['domain'][1]) #
        posmap = temp_graph.renderer._last_posmap
        traces = temp_graph.renderer.get_traces(
                temp_graph,
                xstart=1,
                yaxis='yaxis1',
                override_theme={"color": "black", "track_width": 300}
                )
        for i, axis in posmap['axis_number_to_Axis'].items():
            trace = axis.get_trace()
            with warnings.catch_warnings():
                warnings.simplefilter("default")
                warnings.filterwarnings(action='ignore', category=pint.UnitStrippedWarning, append=True)
                if layout[f'xaxis{i}']['type'] != 'log':
                    new_trace = go.Violin(
                            x=trace.get_data(),
                            points='suspectedoutliers', #'all',
                            box_visible=False,
                            name="",
                            hovertemplate="%{x}",
                            hoveron="kde",
                            xaxis=f"x{i}",
                            yaxis=f"y{i+1}",
                            scalegroup=f'y{i+1}',
                            line_color='black',
                            fillcolor='rgba(0,0,0, .3)',
                            opacity=.7,
                            showlegend=False,
                            )
                else:
                    new_trace = go.Box(
                            x=trace.get_data(),
                            boxpoints='suspectedoutliers', #'all',
                            #box_visible=False,
                            name="",
                            hovertemplate="%{x}",
                            hoveron="points",
                            xaxis=f"x{i}",
                            yaxis=f"y{i+1}",
                            #scalegroup=f'y{i+1}',
                            line_color='black',
                            fillcolor='rgba(0,0,0, .3)',
                            opacity=.7,
                            showlegend=False,
                            pointpos=0,
                            )

            traces.append(new_trace)
            layout[f'yaxis{i+1}'] = dict(
                    domain=(0, .2),
                    anchor=f'x{i}',
                    )



        ret = go.FigureWidget(data=traces, layout=layout)
        return ret
        #TODO: add NAN percentage (within depth)



    def render(self, graph, static=False, depth=None, xp=None, **kwargs):
        xp_depth = kwargs.pop("xp_depth", None)
        xp_depth_by_index = kwargs.pop("xp_depth_by_index", None)
        depth_lock = False
        if xp_depth or xp_depth_by_index:
            depth_lock = True

        by_index = False
        if xp_depth_by_index:
            if xp_depth: raise ValueError("Specify xp_depth or xp_depth_by_index")
            xp_depth = xp_depth_by_index
            by_index = True
        elif not xp_depth:
            xp_depth = depth

        color_lock = kwargs.pop("color_lock", {})
        # kwargs: theme_override, override_theme (same thing)

        # this generates XP layout too, I don't love, would rather set axes
        # separating XP from here would be good but let's call it techdebt
        layout = self.get_layout(graph, xp=xp, depth=depth, **kwargs)
        posmap = self._last_posmap
        # what arguments do we need here now
        traces = self.get_traces(graph, xstart=2 if xp else 1, yaxis='yaxis2' if xp else 'yaxis1', **kwargs)
        if xp is not None:
            traces.extend(
                    xp.create_traces(
                        container_width=layout["width"],
                        depth_range=xp_depth,
                        by_index=by_index,
                        size = layout["height"],
                        static=static,
                        yaxis='y1',
                        color_lock=color_lock
                        )
                    )

        if static:
            self.last_fig = go.Figure(data=traces, layout=layout)
            return self.last_fig
        elif xp is None:
            self.last_fig = xpFigureWidget(data=traces, layout=layout)
            self.last_fig._posmap = posmap
            self.last_fig._lead_axis = "yaxis1"
        else:
            self.last_fig = xpFigureWidget(data=traces, layout=layout, renderer=xp, depth_lock=depth_lock)
            self.last_fig._posmap = posmap
            self.last_fig._lead_axis = "yaxis2"
            self.last_fig.link_depth_to(self.last_fig)
            xp.add_figure(self.last_fig)
        javascript() # double it up
        return self.last_fig

# Use this for all FigureWidgets, have way to return FigureWidget
class xpFigureWidget(go.FigureWidget):
    # pass the controlling graph here, and it will add a callback
    def link_depth_to(self, fig):
        if not isinstance(fig, go.FigureWidget):
            raise TypeError("Supplied fig argument bust be a go.FigureWidget ot have access to interactivity")
        fig.layout.on_change(self._depth_change_cb, fig._lead_axis+'.range', append=True)

    def __init__(self, data=None, layout=None, frames=None, skip_invalid=False, depth_lock=False, **kwargs):
        self._xp_renderer = kwargs.pop("renderer", None)
        self._depth_lock = depth_lock
        super().__init__(data=data, layout=layout, frames=frames, skip_invalid=skip_invalid, **kwargs)

    def _depth_change_cb(self, layout, new_range):
        if not self._depth_lock:
            self.set_depth_range(new_range)
        self._tracks_depth_range = new_range

    def lock_depth_range(self):
        if not self._xp_renderer: raise TypeError("lock_depth_range only applies to graphs with a crossplot")
        self._depth_lock = True

    def unlock_depth_range(self):
        if not self._xp_renderer: raise TypeError("unlock_depth_range only applies to graphs with a crossplot")
        self._depth_lock = False
        self.match_depth_range()

    def match_depth_range(self):
        if not self._xp_renderer: raise TypeError("match_depth_range only applies to graphs with a crossplot")
        self.set_depth_range(depth_range=self._tracks_depth_range)

    def set_depth_range(self, depth_range=None):
        if not self._xp_renderer: raise TypeError("set_depth_range only applies to graphs with a crossplot")
        depth_range = sorted(depth_range) if depth_range else None
        color_range_queue=[]
        with self.batch_update():
            for trace in self['data']:
                if not trace.meta or trace.meta.get("filter", None) != 'depth': continue
                trace.x = self._xp_renderer.x.get_data(slice_by_depth=depth_range)
                trace.y = self._xp_renderer.y.get_data(slice_by_depth=depth_range)
                color_data = trace.meta.get('color_data', None)
                if color_data == 'depth': # if xp were to change x or y, this would be wrong in renderer
                    trace.marker.color = self._xp_renderer.x.get_depth(slice_by_depth=(depth_range))
                elif color_data in self._xp_renderer._colors_by_id:
                    trace.marker.color = self._xp_renderer._colors_by_id[color_data].get_data(slice_by_depth=depth_range)
                if 'color_range' in trace.meta and trace.meta['color_range'] is not None: # no need for (None)?
                    color_range_queue.append((trace.name, trace.meta['color_range']))
        with self.batch_update(): # instead of two batches, color_range could take the new info as arguments
            for item in color_range_queue:
                self.set_color_range(item[0], color_range=item[1])

    # we have to set self._color_range so that can recalculate it when depth changes
    def set_color_range(self, name, color_range=(None), auto=False, lock=False):
        if not self._xp_renderer: raise TypeError("set_color_range only applies to graphs with a crossplot")
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
                    trace.meta[select_key] = trace.marker.colorscale # they must have selected that scale

                colorscale_selected = trace.meta[select_key]
                if auto or color_range==[None]:
                    trace.meta['color_range'] = (None)
                    if calc_key in trace.meta: del trace.meta[calc_key]
                    if select_key in trace.meta: del trace.meta[select_key]
                    trace.marker.colorscale = colorscale_selected
                    return

                data_min = np.nanmin(trace.marker.color)
                data_max = np.nanmax(trace.marker.color)
                if lock:
                    color_range = [data_min, data_max]
                trace.meta['color_range'] = color_range
                if color_range[0] is None: color_range[0] = data_min
                if color_range[1] is None: color_range[1] = data_max

                normalized_pairs = self._xp_renderer.project_color_scale(data_max, data_min, color_range, colorscale_selected)

                trace.marker.colorscale = tuple(normalized_pairs)
                trace.meta[calc_key] = tuple(normalized_pairs)
                # should ctime be the min max for the whole thing

# TODO: clean these values and see if warning-error goes away, but also let us know how many values were cleaned
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

    def _get_marker_with_color(self, array, title=None, colorscale="Viridis_r", container_width=None, size=None):
        if not size: size = self.size
        marker = self._get_marker_no_color()
        marker["color"] = array
        marker["showscale"] = True
        marker["colorscale"] = colorscale
        if container_width is not None:
            marker["colorbar"] = dict( # again, problem here, this should be in layout, but its in trace, and that sucks
                    title=title,
                    orientation='h',
                    thickness=20,
                    thicknessmode='pixels',
                    x=(self.size/(2.00)-45)/container_width,
                    xref='paper',
                    y=10/size, # 10% margin, does this really work for all sizes?
                    yref='paper',
                    len=size*.9,
                    lenmode='pixels')
        else:
            marker["colorbar"] = dict(
                    title=title,
                    orientation='h',
                    thickness=20,
                    thicknessmode='pixels')
        marker["opacity"] = self.fade
        return marker

    def _resolve_selector_to_data(self, selector):
        POZO_OBJS = (pozo.Graph, pozo.Track, pozo.Axis)
        if isinstance(selector, POZO_OBJS):
           data = selector.get_trace()
           if not data:
               raise ValueError(f"{selector} has no pozo.Trace object")
           return data
        elif isinstance(selector, pozo.Trace):
            if not is_array(selector.get_data()): raise TypeError(f"{selector}'s data seems weird: {selector.get_data()}")
            if not is_array(selector.get_depth()):raise TypeError(f"{selector}'s depth seems weird: {selector.get_depth()}")
            return selector
        raise TypeError(f"{selector} does not appear to be a pozo object, it's a {type(selector)}")

    def reinit(self, x = None, y = None, colors=[None], **kwargs):
        self.size                = kwargs.pop("size", self.size)
        self.depth_range         = kwargs.pop("depth_range", self.depth_range)
        self.xrange              = kwargs.pop("xrange", self.xrange)
        self.yrange              = kwargs.pop("yrange", self.yrange)
        if not is_array(colors): colors = [colors]
        self.colors = colors
        self.y              = y if y is not None else self.y
        self.x              = x if x is not None else self.x

    def __repr__(self):
        return f"x: {self.x}\ny: {self.y}\ncolors: {self.colors}"

    def __init__(self, x=None, y=None, colors=[None], **kwargs):
        # rendering defaults
        self.size                = kwargs.pop("size", 500)
        self.depth_range         = kwargs.pop("depth_range", [None])
        self.xrange              = kwargs.pop("xrange", None)
        self.yrange              = kwargs.pop("yrange", None)
        self.fade = 1
        if not is_array(colors): colors = [colors]
        self.colors = colors
        self.y = y
        self.x = x
        self._colors_by_id = {}
        self._figures_by_id = weakref.WeakValueDictionary() # Do figures contain their colors? so we can clear up _colors_by_id

    def add_figure(self, fig):
        self._figures_by_id[id(fig)] = fig

    def render(self, **kwargs):
        static = kwargs.pop("static", False)
        layout = self.create_layout(**kwargs) # container_width, size
        traces = self.create_traces(**kwargs) # container_width, depth_range, size, static

        if static:
            self.last_fig = go.Figure(data=traces, layout=layout)
            return self.last_fig
        fig = xpFigureWidget(data=traces, layout=layout, renderer=self)
        self.add_figure(fig)
        self.last_fig = fig

        return fig

    def create_layout(self, container_width=None, size=None, xaxis="xaxis1", yaxis="yaxis1"):
        if not size: size = self.size
        margin = (120) / size if container_width is not None else 0
        return {
            "width"       : size,
            "height"      : size,
            xaxis       : dict(
                            title = self.x.get_name(),
                            range = self.xrange,
                            linecolor = "#888",
                            linewidth = 1,
            ),
            yaxis       : dict(
                            title = self.y.get_name(),
                            range = self.yrange,
                            domain = (margin, 1),
                            linecolor = "#888",
                            linewidth = 1,
            ),
            "showlegend"  : True
        }

    def create_traces(self, depth_range=None, container_width=None, size=None, static=False, xaxis="xaxis1", yaxis="yaxis1", color_lock={}, by_index=False):
        if not size: size = self.size
        if not depth_range: depth_range = self.depth_range
        x_data = self.x.get_data()[slice(*depth_range)] if by_index else self.x.get_data(slice_by_depth=depth_range)
        y_data = self.y.get_data()[slice(*depth_range)] if by_index else self.y.get_data(slice_by_depth=depth_range)

        self._marker_symbol_index = 1

        # Doing some stats
        missing = (np.isnan(x_data) + np.isnan(y_data)).sum() # noqa TODO
        # TODO improve with more statistics, how many values are there, etc
        title = "Number of unplottable values: {missing} ({(100 * missing/len(x_data)):.1f}%)" # noqa TODO
        # title will be added but also updated whenever written so maybe this should be a function

        self._base_trace = dict(
            x = x_data,
            y = y_data,
            mode='markers',
            xaxis=toTarget(xaxis),
            yaxis=toTarget(yaxis),
        )

        # Make Traces
        trace_definitions = []
        plotly_traces     = []
        for color in self.colors:
            trace_definitions.append(
                    self.create_trace(
                        color,
                        container_width=container_width,
                        depth_range=depth_range,
                        size=size,
                        static=static,
                        by_index=by_index)
                    )
        if trace_definitions and 'visible' in trace_definitions[0]: del trace_definitions[0]['visible']

        for trace in trace_definitions:
            plotly_traces.append(go.Scattergl(trace))
            if trace['name'] in color_lock:
                # originally we did this post-process modification  because we didn't have plotly.colors.get_colorscale(str)
                # we could now do it in create trace
                color_range = color_lock[trace['name']]
                cs_sel = plotly_traces[-1]['marker']['colorscale'] # this is the selected
                data_min = np.nanmin(plotly_traces[-1]['marker']['color'])
                data_max = np.nanmax(plotly_traces[-1]['marker']['color'])
                cs_calc = self.project_color_scale(data_max, data_min, color_range, cs_sel)
                plotly_traces[-1]['marker']['colorscale'] = cs_calc
                plotly_traces[-1].meta['color_range'] = tuple(color_range)
                plotly_traces[-1].meta['colorscale_calculated'] = tuple(cs_calc)
                plotly_traces[-1].meta['colorscale_selected'] = tuple(cs_sel)
                # this should lock it, otherwise, it goes back to auto
        return plotly_traces


    def create_trace(self, color, container_width=None, depth_range=None, size=None, static=False, by_index=False):
        if not size: size = self.size
        trace = self._base_trace.copy()
        trace['meta']={'filter':'depth'}
        if color is not None:
            if isinstance(color, str) and color.lower() == "depth":
                trace['meta']['color_data'] = 'depth'
                color_array = self.x.get_depth()[slice(*depth_range)] if by_index else self.x.get_depth(slice_by_depth=depth_range)
            else:
                color_data = self._resolve_selector_to_data(color)
                color_array = color_data.get_data()[slice(*depth_range)] if by_index else color_data.get_data(slice_by_depth=depth_range)
                if not static: # no need to store if image will never update
                    trace['meta']['color_data'] = id(color)
                    self._colors_by_id[id(color)] = color

            name = color_data.get_name() if color != "depth" else "depth"
            trace['name'] = name
            trace['marker'] = self._get_marker_with_color(color_array, name, container_width=container_width, size=size)
            trace['hovertemplate'] = '%{x}, %{y}, %{marker.color}'
            trace['visible'] = 'legendonly'
        else:
            trace['marker'] = self._get_marker_no_color()
            trace['name'] = "x"
        return trace

    def project_color_scale(self, data_max, data_min, color_range, colorscale_selected):
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
                        if ub is None:
                            ub = pair
                            new_color = plotly.colors.label_rgb(
                                plotly.colors.find_intermediate_color(
                                    plotly.colors.hex_to_rgb(lb[1]) if lb[1][0] != 'r' else plotly.colors.unlabel_rgb(lb[1]),
                                    plotly.colors.hex_to_rgb(ub[1]) if ub[1][0] != 'r' else plotly.colors.unlabel_rgb(ub[1]),
                                    (-lb[0])/(ub[0]-lb[0]) # distance from 0
                                    ))
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
                        if lb is None:
                            lb = pair
                            new_color = plotly.colors.label_rgb(
                                plotly.colors.find_intermediate_color(
                                    plotly.colors.hex_to_rgb(lb[1]) if lb[1][0] != 'r' else plotly.colors.unlabel_rgb(lb[1]),
                                    plotly.colors.hex_to_rgb(ub[1]) if ub[1][0] != 'r' else plotly.colors.unlabel_rgb(ub[1]),
                                    (1-lb[0])/(ub[0]-lb[0]) # distance from 0
                                    ))
                            normalized_pairs = [(1, new_color)]
                        normalized_pairs.append(pair)
                    else:
                        ub = pair
                normalized_pairs = list(reversed(normalized_pairs))
        return normalized_pairs

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


def init_write_image(counter):
    global write_image_counter
    write_image_counter = counter

def write_image(gp):
    gp['graph'].write_image(gp['path'], engine="kaleido")
    with write_image_counter.get_lock():
        write_image_counter.value += 1

def make_xp_depth_video(folder_name, graph, start, window, end, xp=True, output="all.mp4", fps=30, cpus=None):
    try:
        write_image_counter
        raise Exception("Please only run make_frames once at a time, or restart the kernel")
    except NameError:
        pass
    if output:
        try:
            import imageio
        except ImportError:
            raise ImportError("Please install imageio. It must be installed like: pip install imageio[ffmpeg] or pip install imageio[pyav]")
    os.makedirs(folder_name, exist_ok=True)
    if xp is True: xp=graph.xp
    elif not isinstance(xp, CrossPlot): raise ValueError("Crossplot renderer not valid. xp=True (default) or another renderer)")
    trace = xp.x
    depth = trace.get_depth()
    start_index = trace.find_nearest(start)[0]
    window_index = trace.find_nearest(start+window)[0] - start_index
    end_index = trace.find_nearest(end)[0]
    frame_count = range(start_index, end_index-window_index, 1)
    gp = []
    render_counter = IntProgress(min=0, max=len(frame_count)-1, description="Rendering:")
    writer_counter = IntProgress(min=0, max=len(frame_count)-1, description="Writing:")
    display(render_counter)
    display(writer_counter)
    tail_size = math.floor(window_index*.2)
    tail = np.linspace(0,1,tail_size)
    fade = tail.tolist() + [1]*(window_index-tail_size)
    for i, cursor in enumerate(frame_count):
        render_counter.value += 1
        graph.note_dict['Depth Highlight-xxx'] = pozo.Note(
                (depth[cursor], depth[cursor+window_index]),
                show_text=False,
                )
        graph.xp.fade = fade
        gp.append(
                dict(
                    graph=graph.render(
                        height=800,
                        xp=True,
                        depth_position=1,
                        color_lock={'depth': [start, end]},
                        depth=[start, end],
                        xp_depth_by_index=[cursor, cursor+window_index],
                        static=True,
                        ),
                    path=folder_name+"/"+str(i)+".png",
                    )
                )
    del graph.note_dict['Depth Highlight-xxx']

    if not cpus: cpus = multiprocessing.cpu_count()
    if cpus == 1:
        for g in gp:
            g['graph'].write_image(g['path'], engine="kaleido")
            writer_counter.value += 1

    else:
        write_image_counter = multiprocessing.Value('I',0)
        with multiprocessing.Pool(initializer=init_write_image, initargs=(write_image_counter,), processes=cpus) as pool:
            p = pool.map_async(write_image, gp)
            while True:
                p.wait(.5)
                try:
                    p.successful()
                    break
                except ValueError:
                    writer_counter.value = write_image_counter.value
        writer_counter.value = len(frame_count)-1
        del write_image_counter
    if not output: return
    ims = [imageio.imread(p['path']) for p in gp]
    display("Writing movie from frames...")
    imageio.mimwrite(folder_name+"/" + output, ims, fps=fps)
