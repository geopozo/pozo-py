import pozo.renderers as pzr
from IPython.core.display import HTML
import html

class TreeTable(pzr.Renderer):
    def _get_basic(self, item):
        name = item.get_name() # dict
        theme = item.get_theme() # dict
        theme_t = type(theme)
        theme_context = theme.get_context() # dict
        return {
                "name": name,
                "theme": theme,
                "theme_type": theme_t,
                "theme_context": theme_context,
                "children": [],
                }

    def _get_graph_dict(self, graph):
        graph_node = self._get_basic(graph)
        return graph_node

    def _get_track_dict(self, track):
        track_node = self._get_basic(track)
        return track_node

    def _get_axis_dict(self, axis):
        axis_node = self._get_basic(axis)
        return axis_node

    def _get_datum_dict(self, datum):
        mnemonic = datum.get_mnemonic()
        values_t = type(datum.get_data())
        depth_t = type(datum.get_depth())
        length = len(datum.get_data())
        datum_dict = self._get_basic(datum)
        datum_dict["mnemonic"] = mnemonic
        datum_dict["data_type"] = values_t
        datum_dict["depth_type"] = depth_t
        datum_dict["data_unit"] = datum.get_unit()
        datum_dict["depth_unit"] = datum.get_depth_unit()
        datum_dict["length"] = length
        return datum_dict

    def render(self, graph, **kwargs):
        graph_node = self._get_graph_dict(graph)
        total_data = 0
        for track in graph:
            track_node = self._get_track_dict(track)
            for axis in track:
                axis_node = self._get_axis_dict(axis)
                for datum in axis:
                    datum_node = self._get_datum_dict(datum)
                    axis_node["children"].append(datum_node)
                    total_data += 1
                track_node["children"].append(axis_node)
            graph_node["children"].append(track_node)


        style = "\"border: 1px solid gray; text-align:center\""
        output = "<table>"

        output += "<tr>"
        output += f"<td colspan=\"{total_data}\" style={style}>"
        output += "<h3>Graph</h3>"

        tracks = []
        for key, value in graph_node.items():
            if key != "children":
                output += f"<p style=\"text-align:center\">{html.escape(str(key))}: {html.escape(str(value))}</p>"
            else:
                tracks = value # tracks is just a list of tracks
        output += "</td></tr>"

        output += "<tr>"
        axes = []
        for track in tracks:
            colspan = 0
            for axis in track['children']:
                colspan += len(axis['children'])
            output += f"<td colspan=\"{colspan}\" style={style}>"
            output += "<h6>Track</h6>"
            for key, value in track.items():
                if key != "children":
                    output += f"<p style=\"text-align:center\">{html.escape(str(key))}: {html.escape(str(value))}</p>"
                else:
                    axes.append(value) # axes is a list of lists of axes
            output += "</td>"
        output += "</tr>"

        output += "<tr>"
        data = []
        for axes_list in axes:
            for axis in axes_list:
                output += f"<td colspan=\"{len(axis['children'])}\" style={style}>"
                output += "<h6>Axis</h6>"
                for key, value in axis.items():
                    if key != "children":
                        output += f"<p style=\"text-align:center\">{html.escape(str(key))}: {html.escape(str(value))}</p>"
                    else:
                        data.append(value)
                output += "</td>"
        output += "</tr>"

        for data_list in data:
            for datum in data_list:
                output += f"<td style={style}>"
                output += "<h6>Data</h6>"
                for key, value in datum.items():
                    if key != "children":
                        output += f"<p style=\"text-align:center\">{html.escape(str(key))}: {html.escape(str(value))}</p>"
                    else:
                        pass
                output += "</td>"
        output += "</tr>"
        output += "</table>"
        display(HTML(output))

