import streamlit as st
from bokeh.models import Div


def streamlit_run_js(js_code: str) -> None:
    """Runs javascript code at this step in streamlit.

    Uses bokeh (and it is a dependency).

    Args:
        js_code: Javascript code to run
    """
    # passing js code to the onerror handler of an img tag with no src
    # triggers an error and allows automatically running our code
    html = f'<img src onerror="{js_code}">'

    # in contrast to st.write, this seems to allow passing javascript
    div = Div(text=html)
    st.bokeh_chart(div)
