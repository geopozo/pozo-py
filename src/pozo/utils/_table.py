import re

from pozo.utils import _stats


def _apply_color_styling(
    html_str: str,
    pattern: re.Pattern,
    color: str,
) -> str:
    for match in pattern.finditer(html_str):
        current_match = match.group()
        colored = f'<td style="color:{color}">' + current_match[4:]
        html_str = html_str.replace(current_match, colored)
    return html_str


def generate_html_table(
    data: list,
    delimiter: str,
) -> str:
    red_low = re.compile(r"<td>\s*(?:[0-9]|[1-2][0-9]|3[0-3])\s*</td>")
    orange_medium = re.compile(r"<td>\s*(?:3[4-9]|[4-5]\d|6[0-6])\s*</td>")
    post_result = "\n".join(data)

    output = _stats.format_csv(post_result, delimiter)
    html_output = output.to_html()
    html_output = _apply_color_styling(html_output, red_low, "red")
    html_output = _apply_color_styling(html_output, orange_medium, "#B95000")

    return html_output
