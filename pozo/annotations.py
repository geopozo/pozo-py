import pozo
import plotly.graph_objects as go
from abc import ABC

#TODO this doesn't handle units
#TODO xp doesn't handle units or check indices
#TODO what else doesn't handle units
class Note(ABC):
    def __init__(self, *, line={}, width=1, fillcolor = 'lightskyblue', opacity=.5,):
        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        # TODO add further constraints on changes
        self.line       = line
        self.fillcolor  = fillcolor
        self.opacity    = None
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
                 *,
                 x=[],
                 y=[],
                 xaxis="xaxis1",
                 yaxis="yaxis1",
                 fill="toself",
                 line={},
                 width=1,
                 fillcolor = 'lightskyblue',
                 fillgradient=None,
                 fillpattern=None,
                 opacity=.5,
                 bgcolor=None,
                 bgcolorsrc=None,
                 bordercolor=None,
                 bordercolorsrc=None,
                 font=None,
                 groupnorm=None,
                 hoverinfo=None,
                 hoverinfosrc=None,
                 hoverlabel=None,
                 hoveron=None,
                 hovertemplate=None,
                 hovertemplatesrc=None,
                 hovertext=None,
                 hovertextsrc=None,
                 legend=None,
                 legendgroup=None,
                 legendgrouptitle=None,
                 legendrank=None,
                 legendwidth=None
                 ids=None
                 ):

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
        self.line = line
        self.opacity = opacity
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

class LineNote(Note, go.Scatter): #EN DESARROLLO
    def __init__(self,
                 *,
                 x0=0,
                 y0=0,
                 x1=None,
                 y1=None,
                 xref="xaxis1",
                 yref="yref1",
                 line={},
                 width=1,
                 fillcolor = 'lightskyblue',
                 opacity=.5,
                 hoverinfo=None,
                 hoverinfosrc=None,
                 hoverlabel=None,
                 hovertemplate=None,
                 hovertemplatesrc=None,
                 hovertext=None,
                 hovertextsrc=None,
                 ids=None
                 ):

        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        if y1 == None or x1 == None:
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

