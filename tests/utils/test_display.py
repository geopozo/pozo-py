"""Tests for display util functions."""

from unittest.mock import MagicMock, patch

import pytest

from pozo.utils import display

_display_ipython = "pozo.utils.display.display"
_display_html = "pozo.utils.display.HTML"


class TestShowContent:
    """Test the show_content function."""

    @patch(_display_ipython)
    @patch(_display_html)
    def test_show_content_text(self, mock_html, mock_display):
        """Test show_content with text content."""
        content = "Hello, world!"
        display.show_html(content)

        mock_html.assert_not_called()
        mock_display.assert_called_once_with(content)

    @patch(_display_ipython)
    @patch(_display_html)
    def test_show_content_html_true(self, mock_html, mock_display):
        """Test show_content with HTML content and html=True."""
        content = "<h1>Hello, world!</h1>"
        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance

        display.show_html(content, html=True)

        mock_html.assert_called_once_with(content)
        mock_display.assert_called_once_with(mock_html_instance)

    @patch(_display_ipython)
    @patch(_display_html)
    def test_show_content_html_false(self, mock_html, mock_display):
        """Test show_content with HTML content and html=False."""
        content = "<h1>Hello, world!</h1>"
        display.show_html(content, html=False)

        mock_html.assert_not_called()
        mock_display.assert_called_once_with(content)

    @pytest.mark.parametrize(
        ("content", "html_flag", "expected_display_arg"),
        list(
            zip(
                ["Plain text", "Another text", ""],
                [False, False, False],
                ["Plain text", "Another text", ""],
            ),
        ),
    )
    @patch("pozo.utils.display.display")
    def test_show_content_parametrized_text(
        self,
        mock_display,
        content,
        html_flag,
        expected_display_arg,
    ):
        """Test show_content with various text inputs."""
        display.show_html(content, html=html_flag)
        mock_display.assert_called_once_with(expected_display_arg)

    @pytest.mark.parametrize(
        ("content", "html_flag"),
        list(
            zip(
                [
                    "<p>HTML content</p>",
                    "<div>Another HTML</div>",
                    "<script>alert('test')</script>",
                ],
                [True, True, True],
            ),
        ),
    )
    @patch(_display_ipython)
    @patch(_display_html)
    def test_show_content_parametrized_html(
        self,
        mock_html,
        mock_display,
        content,
        html_flag,
    ):
        """Test show_content with various HTML inputs."""
        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance

        display.show_html(content, html=html_flag)

        mock_html.assert_called_once_with(content)
        mock_display.assert_called_once_with(mock_html_instance)

    @patch(_display_ipython)
    def test_show_content_display_error(self, mock_display):
        """Test show_content when display raises an error."""
        mock_display.side_effect = Exception("Display error")

        with pytest.raises(Exception, match="Display error"):
            display.show_html("test content")
