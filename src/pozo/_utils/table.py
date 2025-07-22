from html import escape

from pozo._utils import stats


def _color(cell: int) -> str:
    style = " style='color:"
    if 0 <= cell <= 33:
        return style + "red'"
    elif 34 <= cell <= 66:
        return style + "#B95000'"
    else:
        return ""


def generate_html_table(
    data: list,
    delimiter: str,
) -> str:
    post_result = "\n".join(data)
    rows = stats.read_csv(post_result, delimiter)
    headers = "".join(f"<th>{escape(h)}</th>" for h in rows[0])
    conf_index = rows[0].index("confidence")
    thead = f"<thead>\n<tr>{headers}</tr>\n</thead>"

    def render_row(row: list[str]) -> str:
        cells = "".join(
            f"<td{_color(int(c)) if conf_index == i else ''}>{escape(c)}</td>"
            for i, c in enumerate(row)
        )
        return f"<tr>{cells}</tr>"

    body_rows = "\n".join(map(render_row, rows[1:]))
    return f"<table border='1'>\n{thead}\n<tbody>{body_rows}</tbody>\n</table>"
