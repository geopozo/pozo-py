import warnings
import numpy as np
import pozo
import pozo.units as pzu
import pozo.renderers as pzr
import pozo.themes as pzt
import ood
import ood.exceptions as ooderr

LAS_TYPE = "<class 'lasio.las.LASFile'>" # TODO this isn't going to work reliably
WELLY_WELL_TYPE = "<class 'welly.well.Well'>"
WELLY_PROJECT_TYPE = "<class 'welly.project.Project'>"

# TODO we want to make sure that your depth has no NAN values (and warn user)
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
        self.xp = kwargs.pop('xp', pzr.CrossPlot()) # kinda don't like doing this, making it point to a class


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
        xp = kwargs.get("xp", None)
        if xp == True:
            kwargs['xp'] = self.xp
        render_options = self._render.copy()
        for key in kwargs.keys():
            if key in render_options: del render_options[key]
        self.last_fig = self.renderer.render(self, **kwargs, **render_options)
        return self.last_fig

    def CrossPlot(self, x=None, y=None,**kwargs):
        self.xp.reinit(x=x, y=y, **kwargs) # TODO could add graph
        return self.xp

    def javascript(self):
        self.renderer.javascript()

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
            elif str(type(ar)) == WELLY_PROJECT_TYPE:
                if len(ar.get_wells()) != 1:
                    raise ValueError(f"If you use welly, you must supply a well (or a project that has exactly one well). This project has {len(ar.get_wells())} wells.")
                else:
                    self.add_welly_object(ar[0], **kwargs)
            elif str(type(ar)) == WELLY_WELL_TYPE:
                self.add_welly_object(ar, **kwargs)
            elif isinstance(ar, (pozo.Data, pozo.Axis, pozo.Track)):
                self.add_tracks(ar)
            else:
                warnings.warn(f"Unknown argument type passed: argument {i}, {type(ar)}. Ignored")

    def add_las_object(self, ar, **kwargs):
        include = kwargs.get('include', [])
        exclude = kwargs.get('exclude', [])
        yaxis = kwargs.get('yaxis', None)
        yaxis_name = kwargs.get('yaxis_name',"DEPTH")
        yaxis_unit = None
        if yaxis is not None: # this is a manually added y axis, don't parse it with LAS
            if yaxis_name is None and hasattr(yaxis, "mnemonic"): yaxis_name = yaxis.mnemonic
            if hasattr(yaxis, "unit"):
                yaxis_unit = yaxis.unit
            else:
                warnings.warn("Not sure what yaxis units are.")
            if hasattr(yaxis, "data"):
                yaxis = yaxis.data
            if len(yaxis) != len(ar.index):
                raise ValueError(f"Length of supplied yaxis ({len(yaxis)}) does not match length of LAS File index ({len(ar.index)})")
        elif yaxis_name in ar.curves.keys():
            yaxis = ar.curves[yaxis_name].data
            yaxis_unit = pzu.parse_unit_from_curve(ar.curves[yaxis_name])
        else:
            warnings.warn("No yaxis specified and 'DEPTH' not found: using index. Set explicitly with yaxis= OR yaxis_name=. Not sure what y-axis units are.")
            yaxis = ar.depth_m
            yaxis_unit = pzu.registry.parse_units("meter")


        for curve in ar.curves:
            if yaxis_name is not None and curve.mnemonic == yaxis_name: continue

            mnemonic = pozo.deLASio(curve.mnemonic)
            if include and len(include) != 0 and curve.mnemonic not in include:
                continue
            elif exclude and len(exclude) != 0 and curve.mnemonic in exclude:
                continue
            unit = None
            if curve.unit is None:
                warnings.warn(f"No units found for mnemonic {mnemonic}") # TODO Handle percentages/lookup mnemonics
            else: unit = pzu.parse_unit_from_curve(curve)

            if ooderr.NameConflictException(level=self._name_conflict) is None:
                name = mnemonic
            else:
                name = curve.mnemonic

            data = pozo.Data(curve.data, depth=yaxis, mnemonic=mnemonic, name=name, unit=unit, depth_unit=yaxis_unit)
            self.add_tracks(data)
        if include and len(include) != 0:
            self.reorder_all_tracks(include)

    def add_welly_object(self, ar, **kwargs):
        include = kwargs.get('include', [])
        exclude = kwargs.get('exclude', [])
        yaxis = kwargs.get('yaxis', None)
        yaxis_name = kwargs.get('yaxis_name',"DEPTH")
        yaxis_unit = kwargs.get('yaxis_unit', None)

        if yaxis is not None:
            if yaxis_name and hasattr(yaxis, "mnemonic"): yaxis_name = yaxis.mnemonic
            if hasattr(yaxis, "units"):
                yaxis_unit = pzu.registry.parse_unit_from_context(pozo.deLASio(yaxis.mnemonic), yaxis.units, yaxis.values)
            else:
                warnings.warn("Not sure what yaxis units are.") # TODO
            if hasattr(yaxis, "values"): yaxis = yaxis.values
        elif yaxis_name in ar.data.keys():
            yaxis = ar.data[yaxis_name]
            yaxis_unit = pzu.registry.parse_unit_from_context(pozo.deLASio(yaxis.mnemonic), yaxis.units, yaxis.values)
        else:
            raise ValueError("No yaxis specified and 'DEPTH' not found. Set explicitly with yaxis= OR yaxis_name=.")
        for curve in ar.data.values():
            if yaxis_name is not None and curve.mnemonic == yaxis_name: continue

            mnemonic = pozo.deLASio(curve.mnemonic)
            if include and len(include) != 0 and curve.mnemonic not in include:
                continue
            elif exclude and len(exclude) != 0 and curve.mnemonic in exclude:
                continue

            unit = None
            if curve.units is None:
                warnings.warn(f"No units found for mnemonic {mnemonic}")
            else: unit = pzu.registry.parse_unit_from_context(mnemonic, curve.units, curve.values) # TODO is curve correct?

            if ooderr.NameConflictException(level=self._name_conflict) is None:
                name = mnemonic
            else:
                name = curve.mnemonic
            depth = None
            depth_unit = None
            if yaxis is not None:
                depth = yaxis
                depth_unit = yaxis_unit
            else:
                depth = curve.index
                depth_unit = pzu.parse_unit_from_context(pozo.deLASio(curve.index_name), curve.index_name, curve.index)

            data = pozo.Data(curve.values, depth=depth, mnemonic=mnemonic, name=name, unit=unit, depth_unit=depth_unit)
            self.add_tracks(data)
        if include and len(include) != 0:
            self.reorder_all_tracks(include)


    def _check_types(self, *tracks):
        accepted_types = (pozo.Axis, pozo.Data, pozo.Track)
        raw_return = []
        for track in tracks:
            if isinstance(track, (list)):
                raw_return.extend(self._check_types(*tracks))
            elif not isinstance(track, accepted_types):
                raise TypeError("Axis.add_tracks() only accepts axes, tracks, and data: pozo objects")
            intermediate = track
            if isinstance(intermediate, pozo.Data):
                intermediate = pozo.Axis(intermediate, name=intermediate.get_name())
            if isinstance(intermediate, pozo.Axis):
                intermediate = pozo.Track(intermediate, name=intermediate.get_name())
            if isinstance(intermediate, pozo.Track):
                raw_return.append(intermediate)
        return raw_return

    # add_items
    def add_axes(self, *axes, **kwargs):
        good_axes = self._check_types(*axes)
        super().add_items(*good_axes, **kwargs)
        return good_axes
    # add_items
    def add_tracks(self, *tracks, **kwargs): # axis can take axes... and other axis?
        good_tracks = self._check_types(*tracks)
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
