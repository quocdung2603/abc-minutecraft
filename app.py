"""MinuteCraft — Entry point cho ứng dụng refactored."""
import streamlit as st

from src.ui.styles import inject_css
from src.ui.layout import render_header, render_sidebar, render_step_bar
from src.state import init_state
from src.pages import step_config, step_upload, step_options, step_result

st.set_page_config(
    page_title="MinuteCraft",
    page_icon=":memo:",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_state()
inject_css()

with st.sidebar:
    render_sidebar()

render_header()
render_step_bar()

step = st.session_state.get("current_step", 1)
if step == 1:
    step_config.render()
elif step == 2:
    step_upload.render()
elif step == 3:
    step_options.render()
else:
    step_result.render()
