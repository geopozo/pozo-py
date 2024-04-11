import warnings
import lasio # quiero quitar esto pero en el futuro
import pozo
import pozo.units as pzu
import pozo.renderers as pzr
import pozo.themes as pzt
import ood

import re
desc_wo_num = re.compile(r'^(?:\s*\d+\s+)?(.*)$')
LAS_TYPE = "<class 'lasio.las.LASFile'>"
WELLY_WELL_TYPE = "<class 'welly.well.Well'>"
WELLY_PROJECT_TYPE = "<class 'welly.project.Project'>"


# TODO we want to make sure that your depth has no NAN values (and warn user)
class Graph(ood.Observer, pzt.Themeable):
    _type = "graph"
    _child_type = "track"

    def declare_graph(self, las, structure):
        yaxis, yaxis_name, yaxis_unit = self.get_yaxis_from_las_object(las)
        tracks = []
        for track in structure:
            axes = []
            for axis_name, axis_options in track.items():
                n_keys = 1
                if 'mnemonics' not in axis_options:
                    raise TypeError("axis options must contain 'mnemonics'")
                if 'optional' in axis_options:
                    n_keys += 1
                if len(axis_options.keys()) != n_keys:
                    raise TypeError("axis keys can be 'mnemonics' and 'optional'")
                found_curve = None
                for mnemonic in axis_options['mnemonics']: # looking for one option
                    for curve in las.curves: # lookin in all las
                        if curve.original_mnemonic == mnemonic:
                            found_curve = curve
                            break
                    if found_curve is not None: # LAS CURVES EVAL FALSE WHY
                        break
                if found_curve is None:
                    if ('optional' in axis_options and axis_options['optional']):
                        continue
                    raise RuntimeError(f"Missing any mnemonics for {axis_name}")
                unit = pozo.units.parse_unit_from_curve(found_curve)
                axes.append(pozo.Axis(pozo.Trace(
                        found_curve.data,
                        depth = yaxis,
                        mnemonic = mnemonic,
                        unit = unit,
                        depth_unit = yaxis_unit), name = axis_name))
            if axes: tracks.append(pozo.Track(axes))
        if not tracks: raise RuntimeError("No tracks were created")
        return tracks

    def __init__(self, *args, **kwargs):

        self._name = kwargs.pop("name", "unnamed") # why do graphs have a name? for a title?
        self.renderer = kwargs.pop("renderer", pzr.Plotly())
        self.xp = kwargs.pop("xp", pzr.CrossPlot())

        my_kwargs = {}  # Don't pass these to super, but still pass them down as kwargs
        include = my_kwargs["include"] = kwargs.pop("include", None)
        my_kwargs["exclude"] = kwargs.pop("exclude", None)
        my_kwargs["compare"] = kwargs.pop("compare", False)
        my_kwargs["yaxis"] = kwargs.pop("yaxis", None)
        my_kwargs["yaxis_name"] = kwargs.pop("yaxis_name", None)
        my_kwargs["unit_map"] = kwargs.pop("unit_map", None)
        my_kwargs["declare"] = kwargs.pop("declare", None)
        old_kwargs = kwargs.copy()
        if not isinstance(self._name, str):
            raise TypeError("Name must be a string")
        try:
            super().__init__(**kwargs)
        except TypeError as te:
            raise TypeError(
                f"One of the arguments here isn't valid: {list(old_kwargs.keys())}."
            ) from te
        self.process_data(*args, **my_kwargs)
        if len(args) == 1 and include and len(include) != 0:
            self.reorder_all_tracks(include)
        self.note_dict = {}
        self.note_list = []

    def summarize_curves(self, *selectors, **kwargs):
        return self.renderer.summarize_curves(self, selectors=selectors, **kwargs)

    def render(self, **kwargs):
        xp = kwargs.get("xp", None)
        if xp is True: # noqa this can also but something that evals to True but is not exactly true
            kwargs["xp"] = self.xp
        self.last_fig = self.renderer.render(self, **kwargs)
        return self.last_fig

    def CrossPlot(self, x=None, y=None, **kwargs):
        self.xp.reinit(x=x, y=y, **kwargs)  # TODO could add graph
        return self.xp

    def get_name(self):
        return self._name

    def set_name(self, name):
        self._name = name

    def process_data(self, *args, **kwargs):  # Add ways to add data
        _no_loop = kwargs.pop("_no_list", False)
        for i, ar in enumerate(args):
            if str(type(ar)) == LAS_TYPE:
                if kwargs['declare']:
                    tracks = self.declare_graph(ar, kwargs['declare'])
                    self.add_tracks(*tracks)
                else:
                    self.add_las_object(ar, **kwargs)
            elif str(type(ar)) == WELLY_PROJECT_TYPE:
                if len(ar.get_wells()) != 1:
                    raise ValueError(
                        f"If you use welly, you must supply a well (or a project that has exactly one well). This project has {len(ar.get_wells())} wells."
                    )
                else:
                    self.add_welly_object(ar[0], **kwargs)
            elif str(type(ar)) == WELLY_WELL_TYPE:
                self.add_welly_object(ar, **kwargs)
            elif isinstance(ar, (pozo.Trace, pozo.Axis, pozo.Track)):
                self.add_tracks(ar)
            elif isinstance(ar, (set, list, tuple)):
                if _no_loop: raise RuntimeError(f"Found a list in a list to process, please don't pass any nested lists: {ar}")
                self.process_data(*ar, **kwargs, _no_loop=True)
            else:
                warnings.warn(
                    f"Unknown argument type passed: argument {i}, {type(ar)}. Ignored"
                )

    def get_yaxis_from_las_object(self, ar, **kwargs):
        yaxis = kwargs.get("yaxis", None)
        yaxis_name = kwargs.get("yaxis_name", None)
        yaxis_unit = kwargs.get("yaxis_unit", None)
        if yaxis:
            if yaxis_name is None and hasattr(yaxis, "mnemonic"):
                yaxis_name = yaxis.mnemonic
            if not yaxis_unit and hasattr(yaxis, "unit"):
                yaxis_unit = yaxis.unit
            else:
                warnings.warn("Not sure what yaxis units are.", pozo.PozoWarning)
            if hasattr(yaxis, "data"):
                yaxis = yaxis.data
            if len(yaxis) != len(ar.index):
                raise ValueError(
                    f"Length of supplied yaxis ({len(yaxis)}) does not match length of LAS File index ({len(ar.index)})"
                )
        elif yaxis_name in ar.curves.keys():
            yaxis = ar.curves[yaxis_name].data
            yaxis_unit = pzu.parse_unit_from_curve(ar.curves[yaxis_name]) if not yaxis_unit else yaxis_unit
        else:
            yaxis = ar.index
            yaxis_unit = pzu.registry.parse_unit_from_context("DEPT", ar.index_unit, ar.index) if not yaxis_unit else yaxis_unit

        return yaxis, yaxis_name, yaxis_unit

    def add_las_object(self, ar, **kwargs):
        include = kwargs.get("include", [])
        exclude = kwargs.get("exclude", [])
        unit_map = kwargs.pop("unit_map", None)

        yaxis, yaxis_name, yaxis_unit = self.get_yaxis_from_las_object(ar, **kwargs)

        for curve in ar.curves:
            if yaxis_name is not None and curve.mnemonic == yaxis_name:
                continue

            mnemonic = pozo.deLASio(curve.mnemonic)
            if include and len(include) != 0 and curve.mnemonic not in include:
                continue
            elif exclude and len(exclude) != 0 and curve.mnemonic in exclude:
                continue
            unit = None
            if unit_map and (curve.mnemonic in unit_map or mnemonic in unit_map):
                if curve.mnemonic in unit_map:
                    unit = pzu.registry.parse_units(unit_map[curve.mnemonic])
                elif mnemonic in unit_map:
                    unit = pzu.registry.parse_units(unit_map[mnemonic])
            elif curve.unit is None:
                warnings.warn(
                    f"No units found for mnemonic {mnemonic}"
                )  # TODO should return proper type of error
            else:
                unit = pzu.parse_unit_from_curve(curve)

            trace = pozo.Trace(
                curve.data,
                depth=yaxis,
                mnemonic=mnemonic,
                unit=unit,
                depth_unit=yaxis_unit,
            )
            trace.original_data = curve
            self.add_tracks(trace)

    def add_welly_object(self, ar, **kwargs):
        include = kwargs.get("include", [])
        exclude = kwargs.get("exclude", [])
        yaxis = kwargs.get("yaxis", None)
        yaxis_name = kwargs.get("yaxis_name", None)
        yaxis_unit = kwargs.get("yaxis_unit", None)
        unit_map = kwargs.pop("unit_map", None)

        if yaxis:
            if yaxis_name and hasattr(yaxis, "mnemonic"):
                yaxis_name = yaxis.mnemonic
            if not yaxis_unit and hasattr(yaxis, "units"):
                yaxis_unit = pzu.registry.parse_unit_from_context(
                    pozo.deLASio(yaxis.mnemonic), yaxis.units, yaxis.values
                )
            else:
                warnings.warn("Not sure what yaxis units are.")
            if hasattr(yaxis, "values"):
                yaxis = yaxis.values
        elif yaxis_name and yaxis_name in ar.data.keys():
            yaxis = ar.data[yaxis_name]
            yaxis_unit = pzu.registry.parse_unit_from_context(
                pozo.deLASio(yaxis.mnemonic), yaxis.units, yaxis.values
            )

        for curve in ar.data.values():
            if yaxis_name is not None and curve.mnemonic == yaxis_name:
                continue

            mnemonic = pozo.deLASio(curve.mnemonic)
            if include and len(include) != 0 and curve.mnemonic not in include:
                continue
            elif exclude and len(exclude) != 0 and curve.mnemonic in exclude:
                continue

            unit = None

            if unit_map and (curve.mnemonic in unit_map or mnemonic in unit_map):
                if curve.mnemonic in unit_map:
                    unit = pzu.registry.parse_units(unit_map[curve.mnemonic])
                elif mnemonic in unit_map:
                    unit = pzu.registry.parse_units(unit_map[mnemonic])
            if curve.units is None:
                warnings.warn(f"No units found for mnemonic {mnemonic}")
            else:
                unit = pzu.registry.parse_unit_from_context(
                    mnemonic, curve.units, curve.values
                )  # TODO is curve correct?

            depth = None
            depth_unit = None
            if yaxis:
                depth = yaxis
                depth_unit = yaxis_unit
            else:
                depth = curve.index
                depth_unit = pzu.parse_unit_from_context(
                    pozo.deLASio(curve.index_name), curve.index_name, curve.index
                )

            trace = pozo.Trace(
                curve.values,
                depth=depth,
                mnemonic=mnemonic,
                unit=unit,
                depth_unit=depth_unit,
            )
            trace.original_data = curve
            self.add_tracks(trace)

    def _check_types(self, *tracks):
        accepted_types = (pozo.Axis, pozo.Trace, pozo.Track)
        raw_return = []
        for track in tracks:
            if isinstance(track, (list)):
                raw_return.extend(self._check_types(*tracks))
            elif not isinstance(track, accepted_types):
                raise TypeError(
                    f"Axis.add_tracks() only accepts axes, tracks, and traces: pozo objects, not {type(track)}"
                )
            intermediate = track
            if isinstance(intermediate, pozo.Trace):
                intermediate = pozo.Axis(intermediate, name=intermediate.get_name())
            if isinstance(intermediate, pozo.Axis):
                intermediate = pozo.Track(intermediate, name=intermediate.get_name())
            if isinstance(intermediate, pozo.Track):
                raw_return.append(intermediate)
        return raw_return

    def replace_tracks(self, *tracks, **kwargs): # this interface sucks, maybe just use name
        mnemonics = []
        good_tracks = []
        for track in tracks:
            if isinstance(track, (tuple, list)) and len(track) == 2:
                self.pop_tracks({'name':track[0]}, strict_index=False)
                good_tracks.append(track[1])
                continue
            else:
                good_tracks.append(track)
            for trace in track.get_traces():
                mnemonics.append(trace.get_mnemonic())
        if len(mnemonics) > 0: self.pop_tracks(*mnemonics, strict_index=False, exclude=kwargs.get('exclude', None))
        self.add_tracks(*good_tracks, **kwargs)

    # TODO: exclude and
    def replace_traces(self, *traces, **kwargs):
        if 'exclude' in kwargs: raise RuntimeError("exclude is nto valid for replace traces")
        mnemonics = {}
        for trace in traces:
            if trace.get_mnemonic() in mnemonics:
                raise ValueError("Please don't use replace_traces to replace or add two traces with the same mnemonic. It's ambiguous. Pease delete, add, and combine specifically what you want")
            mnemonics[trace.get_mnemonic()] = trace
        total_popped = {}
        for axis in self.get_axes():
            if len(mnemonics) > 0: popped = axis.pop_traces(*mnemonics, strict_index=False) # we've removed all the traces that we want to replace
            for trace_popped in popped: # for each that we've removed, add the replacement
                total_popped[trace_popped.get_mnemonic()] = True
                axis.add_traces(mnemonics[trace_popped.get_mnemonic()])
        for trace in traces:
            if trace.get_mnemonic() not in total_popped:
                self.add_tracks(trace) # create new track for those that weren't repaced


    # add_items
    def add_tracks(self, *tracks, **kwargs):  # axis can take axes... and other axis?
        good_tracks = self._check_types(*tracks)
        super().add_items(*good_tracks, **kwargs)
        return good_tracks

    # get_items
    def get_tracks(self, *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        return super().get_items(*selectors, **kwargs)

    # get_item
    def get_track(self, selector=0, **kwargs):
        selector = pozo.str_to_HasLog(selector)
        return super().get_item(selector, **kwargs)

    # pop items
    def pop_tracks(self, *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        return super().pop_items(*selectors, **kwargs)

    def combine_tracks(self, selector, *selectors):
        selector = pozo.str_to_HasLog(selector)
        selectors = pozo.str_to_HasLog(selectors)
        sink = self.get_track(selector, strict_index=False)
        if sink is None:
            if isinstance(selector, (pozo.Trace, pozo.Axis, pozo.Track)):
                self.add_tracks(selector)
                sink = selector
            else:
                raise TypeError(
                    "The first argument must be a track that exists or a new track track/axis/trace to add"
                )
        for sel in selectors:
            if isinstance(sel, pozo.Track) and not self.has_track(sel):
                self.add_tracks(sel)
        source = self.pop_tracks(*selectors, sort=False, exclude=[sink])
        for track in source:
            if track == sink: continue
            axes = track.pop_axes()
            sink.add_axes(axes)

    # what about whitelabelling all the other stuff
    def has_track(self, selector):
        selector = pozo.str_to_HasLog(selector)
        return super().has_item(selector)

    def reorder_all_tracks(self, order):
        order = pozo.str_to_HasLog(order)
        super().reorder_all_items(order)

    def move_tracks(self, *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        super().move_items(*selectors, **kwargs)

    def get_axes(self, *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        all_axes = []
        for track in self.get_tracks():
            all_axes.extend(track.get_axes(*selectors, **kwargs))
        return all_axes

    def get_axis(self, selector=0, **kwargs):
        ret = self.get_axes(selector, **kwargs)
        if len(ret) == 0: return None
        return ret[0]

    def get_traces(self, *selectors, **kwargs):
        selectors = pozo.str_to_HasLog(selectors)
        all_traces = []
        for track in self.get_tracks():
            all_traces.extend(track.get_traces(*selectors, **kwargs))
        return all_traces

    def get_trace(self, selector=0, **kwargs):
        ret = self.get_traces(selector, **kwargs)
        if len(ret) == 0: return None
        return ret[0]

    def get_theme(self):
        context = {
            "type": "graph",
            "name": self._name,
        }
        return self._get_theme(context=context)


    def depth_to_las_CurveItem(self, trace):
        mnemonic = "DEPT"
        unit = pzu.registry.resolve_SI_unit_to_las(mnemonic, trace.get_unit())
        descr = "Depth"
        return lasio.CurveItem(mnemonic=mnemonic, unit=unit, value="", descr=descr, data=trace.get_depth())

    # to_las_CurveItems use 5 parameters to can transform data from pozo.Trace
    # to a list with the data as lasio.CurveItem
    def to_las_CurveItems(self, *selectors, **kwargs):
        values = kwargs.pop('values', None)
        descriptions = kwargs.pop('descriptions', None) # Mix of plural and singular AP
        units = kwargs.pop('units', None)

        # Didn't have the original_data we include in all the traces - AP


        traces = self.get_traces(*selectors) # Check after collecting, more complete - AP
        if not traces: raise KeyError("It appears there are no traces to add, aborting") # KeyError - AP

        lasio_list = []
        for index, trace in enumerate(traces):
            data = trace.get_data()
            mnemonic = trace.get_mnemonic()

            # LAS objects resolve False, not sure why
            if units: # accepting anything other than an array doesn't make sense, how often will all unit be the same - AP
                # pzm (pozomath) is a private repository, public users of this repository won't have access to it - AP
                if not pozo.verify_array_len(units, traces):
                    raise ValueError(f"If you are using an array for units, it must be the same size as traces: {len(traces)}")
                unit = units[index]
            else:
                unit = pzu.registry.resolve_SI_unit_to_las(mnemonic, trace.get_unit())
                if unit is None: unit = str(trace.get_unit())

            unit = unit.upper() # las standard all uppercase

            if values:
                if not pozo.verify_array_len(values, traces):
                    raise ValueError("If you are using an array for values, it must be the same size as traces")
                value = values[index]
            elif ( trace.original_data is not None and
                  ( 'value' in trace.original_data or hasattr(trace.original_data, 'value') ) ):
                value = trace.original_data['value']
            else: value = ""

            if descriptions:
                if pozo.is_array(descriptions):
                    if not pozo.verify_array_len(descriptions, traces):
                        raise ValueError("If you are using an array for description, it must be the same size as traces")
                    descr = descriptions[index]
                else: descr = descriptions
            elif ( trace.original_data is not None and
                  ( 'descr' in trace.original_data or hasattr(trace.original_data, 'descr') ) ):
                descr = trace.original_data['descr']
                find_desc = desc_wo_num.findall(descr)
                descr = find_desc[0] if len(find_desc) > 0 else descr
            elif ( trace.original_data is not None and
                  ( 'description' in trace.original_data or hasattr(trace.original_data, 'description') ) ):
                descr = trace.original_data['description']
                find_desc = desc_wo_num.findall(descr)
                descr = find_desc[0] if len(find_desc) > 0 else descr
            else:
                descr = ""

            lasio_obj = lasio.CurveItem(mnemonic=mnemonic, unit=unit, value=value, descr=descr, data=data)
            lasio_list.append(lasio_obj)

        return lasio_list

    # to_las use 2 parameters to can transform data from pozo object or
    # lasio.CurveItem to a lasio.LASFile
    def to_las(self, *selectors, **kwargs):
        template = kwargs.pop("template", lasio.LASFile()) #
        strategy = kwargs.pop("strategy", "pozo-only")
        priority_new = kwargs.pop("priority_new", True)

        # Bad vibes feeding random stuff to a .read(file), also increasing surface area of attack and dependency - AP
        # TypeError, not value error - AP
        if template and str(type(template)) != LAS_TYPE:
            raise TypeError("Templates must be a lasio LAS Object")
        else:
            strategy = "pozo-only"

        pozo_curves = self.to_las_CurveItems(*selectors, plate=template, **kwargs)

        if strategy == "merge":
            double_mnemonics = {}
            for curve in template.curves:
                if curve.original_mnemonic != curve.mnemonic:
                    double_mnemonics[curve.original_mnemonic] = True
            for curve in pozo_curves:
                if curve.mnemonic in double_mnemonics:
                    warnings.warn(f"Ambiguous merge: there are several curves in this template with mnemonic {curve.mnemonic}. Please delete one or more manually with las.delete_curve")
                if curve.mnemonic in template.curves:
                    if not priority_new: continue # give priority to old, don't delete, don't append
                    template.delete_curve(curve.mnemonic)
                template.append_curve_item(curve)

        elif strategy == "add":
            for curve in pozo_curves:
                template.append_curve_item(curve)

        elif strategy == "pozo-only": # this isn't correct, you need to delete curves AP
            all_curves = []
            for curve in template.curves: # could probably copy .keys()
                all_curves.append(curve.mnemonic)
            for mnemonic in all_curves:
                template.delete_curve(mnemonic)
            for curve in [ self.depth_to_las_CurveItem(self.get_traces(*selectors)[0]) ]+ pozo_curves:
                template.append_curve_item(curve)
        else:
            raise ValueError("Avaialble strategies are merge, add, and pozo-only")

        for i, curve in enumerate(template.curves):
            descr = curve.descr
            find_desc = desc_wo_num.findall(descr)
            curve.descr = str(i + 1) + " " + find_desc[0] if len(find_desc) > 0 else descr

        return template
