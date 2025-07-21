"""Tests for display util functions."""


## muchas de estas pruebas no son necesarias
## primero, son funciones visuals y estamás usand
## "assert_not_called" y eso realmente...
## no es asambroso
## tambien solo que hay demasiado codigo
## todo sobre-divido
## no estoy seguro que estamos realmente probando coses que debemos o
## necesitamos probar
## quien importa que una function en particular esta llamada?
## y no vamos a cambaiar eso en el futuro de todos modos
## y tenemos que cambiar todas las pruebas?
## mal

from unittest.mock import MagicMock, patch
# raro usar unittest? no es algo que realmente usamos
# tienes que explicar un poco

import pytest

from pozo.utils.display import show_content  # important funciones directo
from tests.data_types import make_param_list

_display_ipython = "pozo.utils.display.display"
_display_html = "pozo.utils.display.HTML"


class TestShowContent:
    """Test the show_content function."""

    @patch(_display_ipython)
    @patch(_display_html)
    def test_show_content_text(self, mock_html, mock_display):
        """Test show_content with text content."""
        content = "Hello, world!"
        show_content(content)

        mock_html.assert_not_called()
        mock_display.assert_called_once_with(content)

    @patch(_display_ipython)
    @patch(_display_html)
    def test_show_content_html_true(self, mock_html, mock_display):
        """Test show_content with HTML content and html=True."""
        content = "<h1>Hello, world!</h1>"
        mock_html_instance = MagicMock()
        mock_html.return_value = mock_html_instance

        show_content(content, html=True)

        mock_html.assert_called_once_with(content)
        mock_display.assert_called_once_with(mock_html_instance)

    @patch(_display_ipython)
    @patch(_display_html)
    def test_show_content_html_false(self, mock_html, mock_display):
        """Test show_content with HTML content and html=False."""
        content = "<h1>Hello, world!</h1>"
        show_content(content, html=False)

        mock_html.assert_not_called()
        mock_display.assert_called_once_with(content)

    @pytest.mark.parametrize(
        ("content", "html_flag", "expected_display_arg"),
        make_param_list(
            ["Plain text", "Another text", ""],
            [False, False, False],
            ["Plain text", "Another text", ""],
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
        show_content(content, html=html_flag)
        mock_display.assert_called_once_with(expected_display_arg)
        # ???? está

    @pytest.mark.parametrize(
        ("content", "html_flag"),
        make_param_list(
            [
                "<p>HTML content</p>",
                "<div>Another HTML</div>",
                "<script>alert('test')</script>",
            ],
            [True, True, True],
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

        show_content(content, html=html_flag)

        mock_html.assert_called_once_with(content)
        mock_display.assert_called_once_with(mock_html_instance)

    @patch(_display_ipython)
    def test_show_content_display_error(self, mock_display):
        """Test show_content when display raises an error."""
        mock_display.side_effect = Exception("Display error")

        with pytest.raises(Exception, match="Display error"):
            show_content("test content")

    @patch(_display_ipython)
    @patch(_display_html)
    def test_show_content_html_error(self, _, mock_html):
        """Test show_content when HTML raises an error."""
        mock_html.side_effect = Exception("HTML error")

        with pytest.raises(Exception, match="HTML error"):
            show_content("<p>test</p>", html=True)
