from IPython.display import HTML, display


def show_content(content: str, *, html=False):
    return display(HTML(content) if html else content)
