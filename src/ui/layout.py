"""Layout helpers: render_sidebar(), render_header(), render_step_bar()."""
import streamlit as st

from src.config import MODEL_FALLBACK_CHAIN
from src.services import api_key as ak
from src.ui import icons as ico


def render_sidebar() -> None:
    """Render the left sidebar with API key, model config, and quick-start guide.

    Khi người dùng nhập key:
    - Lưu xuống file cache qua ak.save_key().
    - Kiểm tra độ dài > 20 để xác nhận đã lưu.
    - Nếu key hợp lệ và current_step == 1, tự động chuyển sang step 2.
    """
    # Tiêu đề sidebar
    st.sidebar.markdown(
        f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:1rem;">'
        f'{ico.icon("gear", 22)}'
        f'<h3 style="margin:0;color:var(--text-primary);font-weight:700;font-size:1.2rem;">'
        f'Cấu Hình Hệ Thống</h3></div>',
        unsafe_allow_html=True,
    )

    # --- API Key ---
    st.sidebar.markdown("### Gemini API Key")
    saved_key = ak.load_key()
    current_key = st.session_state.get("gemini_api_key", "") or saved_key

    api_key_input = st.sidebar.text_input(
        "Khóa API của bạn",
        value=current_key,
        type="password",
        placeholder="AIza...",
        help="Khóa API được tự động lưu cho các lần truy cập sau.",
        key="sidebar_api_key_input",
    )
    if api_key_input and api_key_input != current_key:
        st.session_state["gemini_api_key"] = api_key_input.strip()
        ak.save_key(api_key_input.strip())

    # Trạng thái kết nối
    active_key = st.session_state.get("gemini_api_key", "")
    if active_key and len(active_key) > 20:
        st.sidebar.success("✓ Đã lưu (chưa kiểm tra)")
        if st.sidebar.button("Xóa API Key đã lưu", key="sidebar_clear_key"):
            ak.clear_key()
            st.session_state["gemini_api_key"] = ""
            st.rerun()
        # Tự động chuyển bước nếu đang ở bước 1
        if st.session_state.get("current_step", 1) == 1:
            st.session_state["current_step"] = 2
    elif active_key:
        st.sidebar.warning("⚠ Đã lưu (chưa kiểm tra)")

    st.sidebar.markdown("---")

    # --- Model config ---
    st.sidebar.markdown("### Thông số Mô hình AI")
    model_idx = 0
    current_model = st.session_state.get("model_choice", MODEL_FALLBACK_CHAIN[0])
    if current_model in MODEL_FALLBACK_CHAIN:
        model_idx = MODEL_FALLBACK_CHAIN.index(current_model)

    model_choice = st.sidebar.selectbox(
        "Mô hình AI",
        MODEL_FALLBACK_CHAIN,
        index=model_idx,
        help="gemini-3.6-flash là mới nhất, được khuyến nghị.",
        key="sidebar_model_select",
    )
    st.session_state["model_choice"] = model_choice

    temperature = st.sidebar.slider(
        "Độ sáng tạo (Temperature)",
        min_value=0.0, max_value=1.0,
        value=st.session_state.get("temperature", 0.1),
        step=0.1,
        help="Mức 0.1 đảm bảo biên bản họp chính xác, bám sát thực tế.",
        key="sidebar_temp_slider",
    )
    st.session_state["temperature"] = temperature

    # --- Custom instructions accordion ---
    with st.sidebar.expander("📝 Hướng dẫn tuỳ chỉnh", expanded=False):
        st.session_state["custom_instructions"] = st.text_area(
            "Yêu cầu bổ sung (tùy chọn):",
            value=st.session_state.get("custom_instructions", ""),
            placeholder="VD: Định dạng ngày DD/MM/YYYY...",
            label_visibility="collapsed",
            key="sidebar_instructions",
        )

    st.sidebar.markdown("---")

    # --- Hướng dẫn nhanh ---
    st.sidebar.markdown("### Hướng dẫn nhanh")
    st.sidebar.info(
        "1. Nhập API Key một lần duy nhất.\n"
        "2. Tải lên tệp âm thanh (tối đa 100MB).\n"
        "3. Bấm **Bắt đầu Phân tích**."
    )


def render_header() -> None:
    """Render the main app header with logo and title."""
    st.markdown(
        f'<div style="display:flex;align-items:center;gap:12px;margin-bottom:0.25rem;">'
        f'{ico.icon("document", 34)}'
        f'<span class="main-title">MinuteCraft</span>'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='subtitle'>"
        "Nền tảng tự động hóa biên bản ghi chép cuộc họp cho doanh nghiệp SME"
        "</div>",
        unsafe_allow_html=True,
    )


def render_step_bar() -> None:
    """Render the horizontal step indicator bar using current_step from session_state."""
    from src.ui.components import step_indicator as _si
    step = st.session_state.get("current_step", 1)
    completed = max(0, step - 1)
    _si(current=step, completed=completed)
