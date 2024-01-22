import warnings

import pozo
import pozo.units as pzu
import pozo.renderers as pzr
import pozo.themes as pzt
import ood
import ood.exceptions as ooderr

LAS_TYPE = "<class 'lasio.las.LASFile'>" # TODO this isn't going to work reliably

class Graph(ood.Observer, pzt.Themeable):
    _type="graph"
    _child_type="track"

    def __init__(self, *args, **kwargs):
        self._render = {}
        _depth_ = kwargs.pop('depth', None)
        if _depth_ is not None: self._render['depth'] = _depth_
        _depth_position_ = kwargs.pop('depth_position', None)
        if _depth_position_ is not None: self._render['depth_position'] = _depth_position_
        _height_ = kwargs.pop('height', None)
        if _height_ is not None: self._render['height']: self._render['height'] = _height_
        _javascript_ = kwargs.pop('javascript', None)
        if _javascript_ is not None: self._render['javascript']: self._render['javascript'] = _javascript_
        # Be cool if we could use include to specify things be on the same track TODO
        old_kwargs = kwargs.copy()
        self._name = kwargs.pop('name', 'unnamed')
        self.renderer = kwargs.pop('renderer', pzr.Plotly())
        my_kwargs = {} # Don't pass these to super, but still pass them down as kwargs
        my_kwargs["include"] = kwargs.pop('include', None)
        my_kwargs["exclude"] = kwargs.pop('exclude', None)
        my_kwargs["compare"] = kwargs.pop('compare', False)
        my_kwargs["yaxis"] = kwargs.pop('yaxis', None)
        my_kwargs["yaxis_name"] = kwargs.pop('yaxis_name', None)
        if not isinstance(self._name, str):
            raise TypeError("Name must be a string")
        try:
            super().__init__(**kwargs)
        except TypeError as te:
            raise TypeError(f"One of the arguments here isn't valid: {list(old_kwargs.keys())}.") from te
        self.process_data(*args, **my_kwargs)

    def render(self, **kwargs):
        self.renderer.render(self, **kwargs)

    def get_name(self):
        return self._name
    def set_name(self, name):
        self._name = name

    def process_data(self, *args, **kwargs): # Add ways to add data
        for i, ar in enumerate(args):
            if str(type(ar)) == LAS_TYPE:
                self.add_las_object(ar, **kwargs)
            elif isinstance(ar, (pozo.Data, pozo.Axis, pozo.Track)):
                self.add_tracks(ar)
            else:
                warnings.warn("Unknown argument type passed: argument {i}, {type(ar)}. Ignored")

    def add_las_object(self, ar, **kwargs):
        include = kwargs.get('include', [])
        exclude = kwargs.get('exclude', [])
        yaxis = kwargs.get('yaxis', None)
        yaxis_name = kwargs.get('yaxis_name',"DEPTH")
        yaxis_unit = None
        if yaxis is not None: # this is a manually added y axis, don't parse it with LAS
            yaxis_name = None
            if hasattr(yaxis, "unit"):
                yaxis_unit = yaxis.unit
            else:
                warnings.warn("Not sure what yaxis units are.") # TODO
            if len(yaxis) != len(ar.index):
                raise ValueError(f"Length of supplied yaxis ({len(yaxis)}) does not match length of LAS File index ({len(ar.index)})")
        elif yaxis_name in ar.curves.keys():
            yaxis = ar.curves[yaxis_name].data
            yaxis_unit = pzu.parse_unit_from_curve(ar.curves[yaxis_name])
        else:
            warnings.warn("No yaxis specified and 'DEPTH' not found: using index. Set explicitly with yaxis= OR yaxis_name=. Not sure what y-axis units are.")
            yaxis = ar.index
            yaxis_name = None


        for curve in ar.curves:
            if yaxis_name is not None and curve.mnemonic == yaxis_name:
                continue

            mnemonic = pozo.deLASio(curve.mnemonic)
            if include and len(include) != 0 and curve.mnemonic not in include:
                continue
            elif exclude and len(exclude) != 0 and curve.mnemonic in exclude:
                continue

            if curve.unit is None:
                warnings.warn(f"No units found for mnemonic {mnemonic}") # TODO Handle percentages/lookup mnemonics
            unit = pzu.parse_unit_from_curve(curve)

            if ooderr.NameConflictException(level=self._name_conflict) is None:
                name = mnemonic
            else:
                name = curve.mnemonic

            data = pozo.Data(curve.data, depth=yaxis, mnemonic=mnemonic, name=name, unit=unit, depth_unit=yaxis_unit)
            self.add_tracks(data)
        if include and len(include) != 0:
            self.reorder_all_tracks(include)

    # add_items
    def add_tracks(self, *tracks, **kwargs): # axis can take axes... and other axis?
        accepted_types = (pozo.Axis, pozo.Data, pozo.Track)
        good_tracks = []
        for track in tracks:
            if isinstance(track, list) and all(isinstance(item, accepted_types) for item in track):
                good_tracks.extend(track) # it'll be out of order
            elif not isinstance(track, accepted_types):
                raise TypeError("Axis.add_tracks() only accepts axes, tracks, and data: pozo objects")

            intermediate = track
            if isinstance(intermediate, pozo.Data):
                intermediate = pozo.Axis(intermediate, name=intermediate.get_name())
            if isinstance(intermediate, pozo.Axis):
                intermediate = pozo.Track(intermediate, name=intermediate.get_name())
            if isinstance(intermediate, pozo.Track):
                good_tracks.append(intermediate)
        super().add_items(*good_tracks, **kwargs)

    # get_items
    def get_tracks(self, *selectors, **kwargs):
        return super().get_items(*selectors, **kwargs)

    # get_item
    def get_track(self, selector, **kwargs):
        return super().get_item(selector, **kwargs)

    # pop items
    def pop_tracks(self,  *selectors, **kwargs):
        return super().pop_items(*selectors, **kwargs)

    def combine_tracks(self, selector, *selectors):
        sink = self.get_track(selector)
        source = self.pop_tracks(*selectors, sort=False)
        for track in source:
            axes = track.pop_axes()
            sink.add_axes(axes)

    # what about whitelabelling all the other stuff
    def has_track(self, selector):
        return super().has_item(selector)

    def reorder_all_tracks(self, order):
        super().reorder_all_items(order)

    def move_tracks(self, *selectors, **kwargs):
        super().move_items(*selectors, **kwargs)

    def get_axes(self, *selectors, **kwargs):
        all_axes = []
        for track in self.get_tracks():
            all_axes.extend(track.get_axes(*selectors, **kwargs))
        return all_axes

    def get_data(self, *selectors, **kwargs):
        all_data = []
        for track in self.get_tracks():
            all_data.extend(track.get_data(*selectors, **kwargs))
        return all_data

    def get_theme(self):
        context = { "type":"graph",
                   "name": self._name,
                   }
        return self._get_theme(context=context)
