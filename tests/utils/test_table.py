import pytest

from pozo._utils import table


class TestGenerateHtmlTable:
    @pytest.mark.parametrize(
        ("confidence", "expected"),
        [
            (10, "style='color:red'"),
            (33, "style='color:red'"),
            (34, "style='color:#B95000'"),
            (66, "style='color:#B95000'"),
            (67, ""),
            (100, ""),
        ],
    )
    def test_generate_html_table_confidence_styles(self, confidence, expected):
        data = ["label,confidence,score", f"A,{confidence},9.99"]
        delimiter = ","

        result = table.generate_html_table(data, delimiter)

        expected_cell = f"<td{f' {expected}' if expected else ''}>{confidence}</td>"
        assert expected_cell in result
