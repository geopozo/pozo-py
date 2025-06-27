import re
from io import StringIO

import pandas as pd


def apply_color_styling(html_str: str, pattern: re.Pattern, color: str):
    for match in pattern.finditer(html_str):
        current_match = match.group()
        colored = f'<td style="color:{color}">' + current_match[4:]
        html_str = html_str.replace(current_match, colored)
    return html_str


def generate_html_table(data, delimiter):
    red_low = re.compile(r"<td>(.+)?(?:LOW|NONE)(.+)?</td>")
    orange_medium = re.compile(r"<td>(.+)?MEDIUM(.+)?</td>")
    post_result = "\n".join(data)

    output = pd.read_csv(StringIO(post_result), delimiter=delimiter, na_filter=False)
    html_output = output.to_html()
    html_output = apply_color_styling(html_output, red_low, "red")
    html_output = apply_color_styling(html_output, orange_medium, "#B95000")

    return html_output
