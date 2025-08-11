from __future__ import annotations

import html
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pint

    from pozo._utils import types


def _color(cell: int) -> str:
    style = " style='color:"
    if 0 <= cell <= 33:
        return style + "red'"
    elif 34 <= cell <= 66:
        return style + "#B95000'"
    else:
        return ""


def generate_html_table(data: types.CurveData) -> str:
    def n0(s: str | pint.Unit | int | None) -> str:
        return "" if s is None else str(s)

    keys = list(data.keys())
    headers = "".join(f"<th>{html.escape(k)}</th>" for k in keys)
    thead = f"<thead>\n<tr>{headers}</tr>\n</thead>"
    conf_index = keys.index("confidence")

    rows = [
        "".join(
            f"<td{_color(int(c)) if conf_index == i else ''}>{html.escape(n0(c))}</td>"
            for i, c in enumerate(row)
        )
        for row in zip(*(data[k] for k in keys))
    ]

    body_rows = "\n".join([f"<tr>{r}</tr>" for r in rows])
    return f"<table border='1'>\n{thead}\n<tbody>{body_rows}</tbody>\n</table>"
