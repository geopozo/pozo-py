"""Display util functions."""

from IPython.display import HTML, display


def show_html(content: str, *, html: bool = False) -> None:
    """Display text or HTML content in an IPython environment."""
    display(HTML(content) if html else content)
