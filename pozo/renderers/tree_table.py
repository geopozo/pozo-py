import pozo.renderers as pzr
from IPython.core.display import HTML, display, Javascript
import html

def javascript():
    add_scroll = '''var css = '.jp-Cell-outputArea { overflow: auto; }',
head = document.getElementsByTagName('head')[0],
style = document.createElement('style');

style.type = 'text/css';
if (style.styleSheet){
  style.styleSheet.cssText = css;
} else {
  style.appendChild(document.createTextNode(css));
}
console.log("Executed javascript()")
head.appendChild(style);'''
    display(Javascript(add_scroll))

class TreeTable(pzr.Renderer):
    def _put_theme(self, dict_instance, item):
        theme = item.get_theme()
        dict_instance["theme"] = str(theme)
        dict_instance["theme_type"] = type(theme).__name__
        dict_instance["theme_context"] = "\n".join([f"{key}:{value}" for key, value in theme.get_context().items()])

    def _get_basic(self, item, **kwargs):
        with_theme = kwargs.get("with_theme", False)
        name = item.get_name() # dict
        ret = {}
        ret["name"] = name
        if with_theme:
            self._put_theme(ret, item)
        ret["children"] = []
        return ret

    def _get_graph_dict(self, graph, **kwargs):
        graph_node = self._get_basic(graph, **kwargs)
        return graph_node

    def _get_track_dict(self, track, **kwargs):
        track_node = self._get_basic(track, **kwargs)
        return track_node

    def _get_axis_dict(self, axis, **kwargs):
        axis_node = self._get_basic(axis, **kwargs)
        return axis_node

    def _get_trace_dict(self, trace, **kwargs):
        mnemonic = trace.get_mnemonic()
        values_t = type(trace.get_data()).__name__
        depth_t = type(trace.get_depth()).__name__
        length = len(trace.get_data())
        trace_dict = self._get_basic(trace, **kwargs)
        trace_dict["name, mnemonic"] = trace_dict["name"] + f", {mnemonic}"
        del trace_dict["name"]
        trace_dict["data"] = f"{values_t}\n{trace.get_unit()}"
        trace_dict["depth"] = f"{depth_t}\n{trace.get_depth_unit()}"
        trace_dict["length"] = length
        return trace_dict

    def render(self, graph, **kwargs):
        graph_node = self._get_graph_dict(graph, **kwargs)
        total_traces = 0
        for track in graph:
            track_node = self._get_track_dict(track, **kwargs)
            for axis in track:
                axis_node = self._get_axis_dict(axis, **kwargs)
                for trace in axis:
                    trace_node = self._get_trace_dict(trace, **kwargs)
                    axis_node["children"].append(trace_node)
                    total_traces += 1
                if not axis_node["children"]:
                    axis_node["children"] = [{'name':"dummy"}]
                    total_traces += 1
                track_node["children"].append(axis_node)
            if not track_node["children"]:
                track_node["children"] = [{'children':[{'name':"dummy"}]}]
                total_traces += 1
            graph_node["children"].append(track_node)

        style = "\"border: 1px solid gray; text-align:center\""
        depre_style = "\"background-color:transparent; text-align:left;\""
        output = "<table>"

        output += "<tr>"
        output += f"<td colspan=\"{total_traces}\" style={style}>"
        output += "<h3>Graph</h3>"

        tracks = []
        output += "<table style=\"margin:auto\">"
        for key, value in graph_node.items():
            if key != "children":
                output += f"<tr><td>{html.escape(str(key))}</td><td><pre style={depre_style}>{html.escape(str(value))}</pre></td></tr>"
            else:
                tracks = value # tracks is just a list of tracks
        output += "</table>"
        output += f"CrossPlot:<pre style={depre_style}>{html.escape(str(graph.xp))}</pre>"
        output += "</td></tr>"

        output += "<tr>"
        axes = []
        for track in tracks:
            colspan = 0
            for axis in track['children']:
                colspan += len(axis['children'])
            output += f"<td colspan=\"{colspan}\" style={style}>"
            output += "<h6>Track</h6>"
            output += "<table style=\"margin:auto\">"
            for key, value in track.items():
                if key != "children":
                    output += f"<tr><td>{html.escape(str(key))}</td><td><pre style={depre_style}>{html.escape(str(value))}</pre></td></tr>"
                else:
                    axes.append(value) # axes is a list of lists of axes
            output += "</table>"
            output += "</td>"
        output += "</tr>"

        output += "<tr>"
        traces = []
        for axes_list in axes:
            for axis in axes_list:
                output += f"<td colspan=\"{len(axis['children'])}\" style={style}>"
                output += "<h6>Axis</h6>"
                output += "<table style=\"margin:auto\">"
                for key, value in axis.items():
                    if key != "children":
                        output += f"<tr><td>{html.escape(str(key))}</td><td><pre style={depre_style}>{html.escape(str(value))}</pre></td></tr>"
                    else:
                        traces.append(value)
                output += "</table>"
                output += "</td>"
        output += "</tr>"

        for traces_list in traces:
            for trace in traces_list:
                output += f"<td style={style}>"
                output += "<h6>Data</h6>"
                output += "<table style=\"margin:auto\">"
                td_style = "text-align:center"
                for key, value in trace.items():
                    if key != "children":
                        output += f"<tr><td style=\"{td_style};font-weight:bold\" style=\"font-weight:bold\">{html.escape(str(key))}</td></tr><tr><td style=\"{td_style}\"><pre style={depre_style}>{html.escape(str(value))}</pre></td></tr>"
                    else:
                        pass
                output += "</table>"
                output += "</td>"
        output += "</tr>"
        output += "</table>"
        display(HTML(output))
        javascript()

