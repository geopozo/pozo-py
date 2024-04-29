import pozo

#TODO this doesn't handle units
#TODO xp doesn't handle units or check indices
#TODO what else doesn't handle units
class Note():
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

class DepthNote(Note):
    def __init__(self, depth, *, line={}, text="", width=1, fillcolor = 'lightskyblue', opacity=.5, show_text=True):
        Note.__init__(self, *, line, width, fillcolor, opacity, show_text)
        if not ( ( pozo.is_array(depth) and len(depth) == 2 ) or pozo.is_scalar_number(depth) ):
            raise TypeError("depth must be two numbers in a tuple or list or just one number")
        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        self.depth      = depth
        self.line       = line
        self.fillcolor  = fillcolor
        self.opacity    = opacity
        self.show_text  = show_text
        self.text       = text
        self.width      = width

class PolygonNote(Note):
    def __init__(self, *, x=[], y=[], xaxis="xaxis1", yaxis="yaxis1", fill="toself", line={}, width=1, fillcolor = 'lightskyblue', opacity=.5):
        Note.__init__(self, *, line, width, fillcolor, opacity)
        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        self.x = x
        self.y = y
        self.yaxis = xaxis
        self.xaxis = yaxis
        self.fill = fill
        self.line = line
        self.opacity = opacity

class LineNote(Note):
    def __init__(self, *, x0=0, y0=0, x1=None, y1=None, xref="xaxis1", yref="yref1", line={}, width=1, fillcolor = 'lightskyblue', opacity=.5):
        Note.__init__(self, *, line, width, fillcolor, opacity)
        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        if y1 == None or x1 == None:
            raise ValueError("You must use values for x1 and y1")
        self.x0 = x0
        self.y0 = y0
        self.x1 = x1
        self.y1 = y1
        self.yref = xref
        self.xref = yref
        self.line = line
        self.opacity = opacity
        self.fillcolor = fillcolor
