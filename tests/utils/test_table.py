from unittest.mock import Mock, patch

import pytest

from pozo._utils import table

_table_basic = "<table><tr><td>25</td><td>40</td></tr></table>"
_table_empty = "<table></table>"
_red_style = '<td style="color:red">'
_orange_style = '<td style="color:#B95000">'
_format_csv_patch = "pozo._utils.table.stats.read_csv"


class TestGenerateHtmlTable:
    @patch(_format_csv_patch)
    def test_generate_html_table_basic(self, mock_format_csv):
        mock_df = Mock()
        mock_df.to_html.return_value = _table_basic
        mock_format_csv.return_value = mock_df

        data = ["a,b", "25,40"]
        result = table.generate_html_table(data, ",")

        mock_format_csv.assert_called_once_with("a,b\n25,40", ",")
        assert f"{_red_style}25</td>" in result
        assert f"{_orange_style}40</td>" in result

    @patch(_format_csv_patch)
    def test_generate_html_table_no_color_matches(self, mock_format_csv):
        mock_df = Mock()
        no_color_table = "<table><tr><td>100</td><td>200</td></tr></table>"
        mock_df.to_html.return_value = no_color_table
        mock_format_csv.return_value = mock_df

        data = ["a,b", "100,200"]
        result = table.generate_html_table(data, ",")

        mock_format_csv.assert_called_once_with("a,b\n100,200", ",")
        assert result == no_color_table

    @patch(_format_csv_patch)
    def test_generate_html_table_red_range(self, mock_format_csv):
        mock_df = Mock()
        red_table = "<table><tr><td>0</td><td>15</td><td>33</td></tr></table>"
        mock_df.to_html.return_value = red_table
        mock_format_csv.return_value = mock_df

        data = ["a,b,c", "0,15,33"]
        result = table.generate_html_table(data, ",")

        assert f"{_red_style}0</td>" in result
        assert f"{_red_style}15</td>" in result
        assert f"{_red_style}33</td>" in result

    @patch(_format_csv_patch)
    def test_generate_html_table_orange_range(self, mock_format_csv):
        mock_df = Mock()
        orange_table = "<table><tr><td>34</td><td>50</td><td>66</td></tr></table>"
        mock_df.to_html.return_value = orange_table
        mock_format_csv.return_value = mock_df

        data = ["a,b,c", "34,50,66"]
        result = table.generate_html_table(data, ",")

        assert f"{_orange_style}34</td>" in result
        assert f"{_orange_style}50</td>" in result
        assert f"{_orange_style}66</td>" in result

    @patch(_format_csv_patch)
    def test_generate_html_table_mixed_ranges(self, mock_format_csv):
        mock_df = Mock()
        mixed_table = "<table><tr><td>25</td><td>40</td><td>70</td></tr></table>"
        mock_df.to_html.return_value = mixed_table
        mock_format_csv.return_value = mock_df

        data = ["a,b,c", "25,40,70"]
        result = table.generate_html_table(data, ",")

        assert f"{_red_style}25</td>" in result
        assert f"{_orange_style}40</td>" in result
        assert "<td>70</td>" in result

    @patch(_format_csv_patch)
    def test_generate_html_table_different_delimiters(self, mock_format_csv):
        mock_df = Mock()
        single_table = "<table><tr><td>25</td></tr></table>"
        mock_df.to_html.return_value = single_table
        mock_format_csv.return_value = mock_df

        data = ["a;b", "25;40"]
        table.generate_html_table(data, ";")
        mock_format_csv.assert_called_with("a;b\n25;40", ";")

        data = ["a\tb", "25\t40"]
        table.generate_html_table(data, "\t")
        mock_format_csv.assert_called_with("a\tb\n25\t40", "\t")

    @patch(_format_csv_patch)
    def test_generate_html_table_empty_data(self, mock_format_csv):
        mock_df = Mock()
        mock_df.to_html.return_value = _table_empty
        mock_format_csv.return_value = mock_df

        data = []
        result = table.generate_html_table(data, ",")

        mock_format_csv.assert_called_once_with("", ",")
        assert result == _table_empty

    @patch(_format_csv_patch)
    def test_generate_html_table_format_csv_error(self, mock_format_csv):
        mock_format_csv.side_effect = Exception("CSV parsing error")

        data = ["invalid,data"]

        with pytest.raises(Exception, match="CSV parsing error"):
            table.generate_html_table(data, ",")

    @patch(_format_csv_patch)
    def test_generate_html_table_to_html_error(self, mock_format_csv):
        mock_df = Mock()
        mock_df.to_html.side_effect = Exception("HTML generation error")
        mock_format_csv.return_value = mock_df

        data = ["a,b", "1,2"]

        with pytest.raises(Exception, match="HTML generation error"):
            table.generate_html_table(data, ",")

    @pytest.mark.parametrize(
        ("data", "delimiter", "expected_join"),
        list(
            zip(
                [["line1", "line2", "line3"], ["a,b", "1,2"], ["single_line"]],
                [",", ",", "\t"],
                ["line1\nline2\nline3", "a,b\n1,2", "single_line"],
            ),
        ),
    )
    @patch(_format_csv_patch)
    def test_generate_html_table_data_joining(
        self,
        mock_format_csv,
        data,
        delimiter,
        expected_join,
    ):
        mock_df = Mock()
        mock_df.to_html.return_value = _table_empty
        mock_format_csv.return_value = mock_df

        table.generate_html_table(data, delimiter)

        mock_format_csv.assert_called_once_with(expected_join, delimiter)
