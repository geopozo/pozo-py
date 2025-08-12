import pozo

#TODO this doesn't handle units
#TODO xp doesn't handle units or check indices
#TODO what else doesn't handle units
class Note():
    def __init__(self, depth, *, line={}, text="", width=1, fillcolor = 'lightskyblue', opacity=.5, show_text=True):
        if not ( ( pozo.is_array(depth) and len(depth) == 2 ) or pozo.is_scalar_number(depth) ):
            raise TypeError("depth must be two numbers in a tuple or list or just one number")
        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        # TODO add further constraints on changes
        self.depth      = depth
        self.line       = line
        self.fillcolor  = fillcolor
        self.opacity    = None
        self.show_text  = True
        self.text       = text
        self.width      = width

