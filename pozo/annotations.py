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
        Note.__init__(self, *, line={}, width=1, fillcolor = 'lightskyblue', opacity=.5, show_text=True)
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
    def __init__(self, depth, *, line={}, text="", width=1, fillcolor = 'lightskyblue', opacity=.5, show_text=True):
        Note.__init__(self, depth, *, line={}, text="", width=1, fillcolor = 'lightskyblue', opacity=.5, show_text=True)
        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        self.x
        self.y
        self.yaxis
        self.xaxis
        self.fill
        self.line
