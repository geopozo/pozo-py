import json
from pathlib import Path

import pytest

from pozo._utils import table

route = Path(__file__).parent / "table_data.json"
with route.open("r", encoding="utf-8") as file:
    json_data = json.load(file)


class TestGenerateHtmlTable:
    @pytest.mark.parametrize(
        ("data", "expected", "n_rows", "style"),
        list(
            zip(
                json_data["input"],
                json_data["output"],
                json_data["n_rows"],
                json_data["styles"],
            ),
        ),
        ids=json_data["tests"],
    )
    def test_generate_html_table_confidence_styles(self, data, expected, n_rows, style):
        result = table.generate_html_table(data)
        print(result)
        assert result in expected
        assert result.count("<tr") is n_rows
        assert style in result
