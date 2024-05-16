def get_shadow_trace(last_posmap, themes, trace, num_axes, yaxis, fillcolor):
    assert id(trace) in last_posmap['trace_id_to_axis_number']
    caf_name = themes['cross_axis_fill'][0]
    assert caf_name in last_posmap['cross_axis_fills']
    sink_range = last_posmap['layout']['xaxis'+str(num_axes)]['range']
    source_trace = last_posmap['cross_axis_fills'][caf_name]['source']
    source_axis = last_posmap['trace_id_to_axis_number'][id(source_trace)]
    source_range = last_posmap['layout']['xaxis' + str(source_axis)]['range']
    sink_distance = sink_range[1] - sink_range[0]
    source_distance = source_range[1] - source_range[0]
    point_scale = sink_distance/source_distance
    point_shift = sink_range[0] - (source_range[0] * point_scale)
    shadow_data = source_trace.get_data(clean=True) * point_scale + point_shift
    shadow_trace = dict(
        x=shadow_data,
        y=trace.get_depth(clean=True),
        mode='lines', # nope, based on data w/ default
        line=dict(color='black', width=0), # needs to be better, based on data
        xaxis='x' + str(num_axes),
        yaxis=yaxis,
        name = source_trace.get_mnemonic() + "-shadow",
        showlegend = False,
        fill = 'tonextx',
        fillcolor = fillcolor
    )
    return shadow_trace
