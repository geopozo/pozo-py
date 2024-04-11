import pozo

#TODO this doesn't handle units
#TODO xp doesn't handle units or check indices
#TODO what else doesn't handle units
class DepthNote():
    def __init__(self, depth, *, line={}, text="", width=1, fillcolor = None, opacity=.5, show_text=True):
        if not ( ( pozo.is_array(depth) and len(depth) == 2 ) or pozo.is_scalar_number(depth) ):
            raise TypeError("depth must be two numbers in a tuple or list or just one number")
        if not isinstance(line, dict):
            raise TypeError("line must be a dictionary")
        if width < -1 or width > 1:
            raise ValueError("width must be between -1 and 1")
        # TODO add further constraints on changes
        self.depth      = depth
        self.line       = line
        self.fillcolor  = 'lightskyblue'
        self.opacity    = None
        self.show_text  = True
        self.text       = text
        self.width      = width

        ...
    def _make_shape(self, xref, yref):
        x_lower_bound = 0
        x_upper_bound = 1
        if self.width > 0:
            x_lower_bound = self.width
        elif self.width < 0:
           x_upper_bound += self.width

        shape = dict(
                xref    =  xref,
                x0      =  x_lower_bound,
                x1      =  x_upper_bound,
                yref    =  yref
                )
        default_line = dict(
                color   = 'black',
                width   = 1,
                dash    = 'dot',
        )
        if pozo.is_array(self.depth) and len(self.depth) == 2:
            shape['type']       = 'rect'
            shape['y0']         = self.depth[0]
            shape['y1']         = self.depth[1] # to get
            default_line['width'] = 0
            shape['line']       = default_line.update(self.line) # to get
            shape['fillcolor']  = self.fillcolor
            shape['layer']      = "below",
            shape['opacity']    = .5,
        elif pozo.is_scalar_number(self.depth):
            shape['type']               = 'line'
            shape['y0'] = shape['y1']   = self.depth
            shape['line']               = default_line.update(self.line)
        else:
            raise TypeError("Range must be a number or two numbers in a tuple or list")
        return shape
    def _make_note(self, xref, yref, is_line): # if graph,
        annotation = dict(
            text=self.text,
            xref=xref, # could be domain or paper
            x=1,
            yref=yref,
            y=self.depth if is_line else self.depth[0],
            yshift=-5,
            showarrow=False,
        )
        return annotation
    def render(self, xref, yref):
        shape = self._make_shape(xref, yref)
        annotation = None
        if self.show_text:
            annotation = self._make_note(xref, yref, shape['type'] == 'line')
        return shape, annotation
