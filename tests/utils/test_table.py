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
        data = ["label,confidence,min", f"A,{confidence},9.99"]
        delimiter = ","

        result = table.generate_html_table(data, delimiter)

        expected_cell = f"<td{f' {expected}' if expected else ''}>{confidence}</td>"
        assert expected_cell in result

    def test_generate_html_table_basic_structure(self):
        data = ["mnemonic,las unit,confidence", "DEFT,M,100"]
        delimiter = ","

        result = table.generate_html_table(data, delimiter)

        assert result.startswith("<table border='1'>")
        assert result.endswith("</table>")
        assert "<thead>" in result
        assert "</thead>" in result
        assert "<tbody>" in result
        assert "</tbody>" in result

    def test_generate_html_table_multiple_rows(self):
        data = [
            "mnemonic,las_unit,confidence",
            "DEPT,M,100",
            "ILD,OHMM,100",
            "GR,GAPI,100",
        ]
        delimiter = ","

        result = table.generate_html_table(data, delimiter)

        assert result.count("<tr>") == 4
        assert "<td>DEPT</td>" in result
        assert "<td>ILD</td>" in result
        assert "<td>GR</td>" in result
