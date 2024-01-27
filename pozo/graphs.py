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
        render_keys = ['show_depth', 'depth_position', 'height', 'javascript', 'depth']
        for key in render_keys:
            temporary = kwargs.pop(key, None)
            if temporary is not None: self._render[key] = temporary

        # Be cool if we could use include to specify things be on the same track TODO
        self._name = kwargs.pop('name', 'unnamed')
        self.renderer = kwargs.pop('renderer', pzr.Plotly())
        my_kwargs = {} # Don't pass these to super, but still pass them down as kwargs
        my_kwargs["include"] = kwargs.pop('include', None)
        my_kwargs["exclude"] = kwargs.pop('exclude', None)
        my_kwargs["compare"] = kwargs.pop('compare', False)
        my_kwargs["yaxis"] = kwargs.pop('yaxis', None)
        my_kwargs["yaxis_name"] = kwargs.pop('yaxis_name', None)
        old_kwargs = kwargs.copy()
        if not isinstance(self._name, str):
            raise TypeError("Name must be a string")
        try:
            super().__init__(**kwargs)
        except TypeError as te:
            raise TypeError(f"One of the arguments here isn't valid: {list(old_kwargs.keys())}.") from te
        self.process_data(*args, **my_kwargs)

    def render(self, **kwargs):
        render_options = self._render.copy()
        for key in kwargs.keys():
            if key in render_options: del render_options[key]
        self.renderer.render(self, **kwargs, **render_options)

    def get_name(self):
        return self._name
    def set_name(self, name):
        self._name = name

    def set_render_setting(self, key, value):
        self._render[key] = value

    def show_depth(self, boolean):
        self.set_render_setting('show_depth', boolean)

    def set_depth_position(self, position):
        self.set_render_setting('depth_position', position)

    def set_height(self, height):
        self.set_render_setting('height', height)

    def set_depth(self, depth_range):
        self.set_render_setting('depth', depth_range)

    def get_render_settings(self):
        return self._render

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
        return good_tracks

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
        sink = self.get_track(selector, strict_index=False)
        if sink is None:
            if isinstance(selector, (pozo.Data, pozo.Axis, pozo.Track)):
                self.add_tracks(selector)
                sink = selector
            else:
                raise TypeError("The first argument must be a track that exists or a new track track/axes/data to add")
        for sel in selectors:
            if not self.has_track(sel) and isinstance(sel, pozo.Track):
                self.add_tracks(sel)
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
