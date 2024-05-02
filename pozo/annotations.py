import pozo
import plotly.graph_objects as go
from abc import ABC

#TODO this doesn't handle units
#TODO xp doesn't handle units or check indices
#TODO what else doesn't handle units
class Note(ABC):
    def __init__(self, *, line={}, width=1, fillcolor = 'lightskyblue', opacity=.5):
        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        # TODO add further constraints on changes
        self.line       = line
        self.fillcolor  = fillcolor
        self.opacity    = opacity
        self.width      = width

class DepthNote(Note): #EN DESARROLLO
    def __init__(self,
                 depth,
                 *,
                 line={},
                 text="",
                 width=1,
                 fillcolor = 'lightskyblue',
                 opacity=.5,
                 show_text=True
                 ):

        super().__init__(self, line, width, fillcolor, opacity)
        if not ((pozo.is_array(depth) and len(depth) == 2 ) or pozo.is_scalar_number(depth)):
            raise TypeError(
                "depth must be two numbers in a tuple or list or just one number"
                )
        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        self.depth      = depth
        self.show_text  = show_text
        self.text       = text

class PolygonNote(Note): #EN DESARROLLO
    def __init__(self,
                 x=[],
                 y=[],
                 xaxis="xaxis1",
                 yaxis="yaxis1",
                 fill="toself",
                 line={},
                 **kwargs
                 ):

        width = kwargs.pop("width", 1)
        fillcolor = kwargs.pop("fillcolor", 'lightskyblue')
        fillgradient = kwargs.pop("fillgradient", None)
        fillpattern = kwargs.pop("fillpattern", None)
        opacity = kwargs.pop("opacity", .5)
        bgcolor = kwargs.pop("bgcolor", None)
        bgcolorsrc = kwargs.pop("bgcolorsrc", None)
        bordercolor = kwargs.pop("bordercolor", None)
        bordercolorsrc = kwargs.pop("bordercolorsrc", None)
        font = kwargs.pop("font", None)
        groupnorm = kwargs.pop("groupnorm", None)
        hoverinfo = kwargs.pop("hoverinfo", None)
        hoverinfosrc = kwargs.pop("hoverinfosrc", None)
        hoverlabel = kwargs.pop("hoverlabel", None)
        hoveron = kwargs.pop("hoveron", None)
        hovertemplate = kwargs.pop("hovertemplate", None)
        hovertemplatesrc = kwargs.pop("hovertemplatesrc", None)
        hovertext = kwargs.pop("hovertext", None)
        hovertextsrc = kwargs.pop("hovertextsrc", None)
        legend = kwargs.pop("legend", None)
        legendgroup = kwargs.pop("legendgroup", None)
        legendgrouptitle = kwargs.pop("legendgrouptitle", None)
        legendrank = kwargs.pop("legendrank", None)
        legendwidth = kwargs.pop("legendwidth", None)
        ids = kwargs.pop("ids", None)

        Note.__init__(self, line, width, fillcolor, opacity)
        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        self.x = x
        self.y = y
        self.yaxis = xaxis
        self.xaxis = yaxis
        self.fill = fill
        self.fillgradient=fillgradient,
        self.fillpattern=fillpattern,
        self.bgcolor=bgcolor,
        self.bgcolorsrc=bgcolorsrc,
        self.bordercolor=bordercolor,
        self.bordercolorsrc=bordercolorsrc,
        self.font=font,
        self.groupnorm=groupnorm,
        self.hoverinfo=hoverinfo,
        self.hoverinfosrc=hoverinfosrc,
        self.hoverlabel=hoverlabel,
        self.hoveron=hoveron,
        self.hovertemplate=hovertemplate,
        self.hovertemplatesrc=hovertemplatesrc,
        self.hovertext=hovertext,
        self.hovertextsrc=hovertextsrc,
        self.legend=legend,
        self.legendgroup=legendgroup,
        self.legendgrouptitle=legendgrouptitle,
        self.legendrank=legendrank,
        self.legendwidth=legendwidth
        self.ids=ids

class LineNote(Note, go.Scatter): #EN DESARROLLO
    def __init__(self,
                 x0=0,
                 y0=0,
                 x1=None,
                 y1=None,
                 xref="xaxis1",
                 yref="yref1",
                 line={},
                 **kwargs
                 ):

        width = kwargs.pop("width", 1)
        fillcolor = kwargs.pop("fillcolor", 'lightskyblue')
        opacity = kwargs.pop("opacity", .5)
        hoverinfo = kwargs.pop("hoverinfo", None)
        hoverinfosrc = kwargs.pop("hoverinfosrc", None)
        hoverlabel = kwargs.pop("hoverlabel", None)
        hovertemplate = kwargs.pop("hovertemplate", None)
        hovertemplatesrc = kwargs.pop("hovertemplatesrc", None)
        hovertext = kwargs.pop("hovertext", None)
        hovertextsrc = kwargs.pop("hovertextsrc", None)
        ids = kwargs.pop("ids", None)

        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        if y1 is None or x1 is None:
            raise ValueError("You must use values for x1 and y1")

        Note.__init__(self, line=line, width=width, fillcolor=fillcolor, opacity=opacity)
        go.Scatter.__init__(self,
                            x0=x0,
                            y0=y0,
                            x1=x1,
                            y1=y1,
                            xref=xref,
                            yref=yref,
                            line=line,
                            width=width,
                            fillcolor=fillcolor,
                            opacity=opacity,
                            hoverinfo=hoverinfo,
                            hoverinfosrc=hoverinfosrc,
                            hoverlabel=hoverlabel,
                            hovertemplate=hovertemplate,
                            hovertemplatesrc=hovertemplatesrc,
                            hovertext=hovertext,
                            hovertextsrc=hovertextsrc,
                            ids=ids
                            )

