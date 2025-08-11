"""Display util functions."""

from __future__ import annotations

import sys

import marimo as mo
from IPython.display import HTML, display


def show_html(content: str, *, html: bool = False) -> mo.Html | None:
    """Display text or HTML content in an IPython environment."""
    if "marimo" in sys.modules and "ipykernel" not in sys.modules:
        return mo.Html(content)
    else:
        display(HTML(content) if html else content)
        return None
