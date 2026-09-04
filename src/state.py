"""Khởi tạo st.session_state với giá trị mặc định cho cả 4 bước."""
import streamlit as st

DEFAULT_STATE = {
    "current_step": 1,
    "gemini_api_key": "",
    "model_choice": "gemini-3.6-flash",
    "temperature": 0.1,
    "uploaded_file_bytes": None,
    "uploaded_filename": None,
    "uploaded_mime": None,
    "template_bytes": None,
    "template_filename": None,
    "focus_area": None,
    "custom_instructions": "",
    "analysis_result": None,
    "history": [],
}


def init_state():
    """Set default values for session state keys if they are not already set."""
    for key, default in DEFAULT_STATE.items():
        st.session_state.setdefault(key, default)
