"""Step 1: Hướng dẫn + kiểm tra API key.

Hiển thị welcome block khi current_step == 1.
Tự động chuyển sang step 2 nếu gemini_api_key đã được cài đặt.
"""
import streamlit as st

from src.ui.components import empty_state, section_header


def render() -> None:
    """Render Step 1 page — chỉ hiển thị khi current_step == 1."""
    if st.session_state.get("current_step", 1) != 1:
        return

    # Welcome empty state
    empty_state(
        icon_name="sparkle",
        title="Chào mừng đến MinuteCraft",
        description=(
            "Hệ thống sẽ tự động nghe, phân tích và lập biên bản "
            "cho mọi cuộc họp của bạn. Hãy cấu hình API Key ở "
            "thanh bên trái để bắt đầu."
        ),
        cta_label=None,
    )

    # Hướng dẫn sử dụng
    section_header("Cách sử dụng", icon_name="clipboard", subtitle="3 bước đơn giản để lập biên bản họp")

    steps = [
        ("1", "Cấu hình API Key", "Nhập Gemini API Key của bạn ở thanh bên trái (chỉ cần làm một lần)."),
        ("2", "Tải file ghi âm", "Tải lên tệp âm thanh cuộc họp (.mp3, .wav, .m4a, .ogg)."),
        ("3", "Lập biên bản", "Bấm 'Bắt đầu Phân tích' để nhận biên bản họp chuyên nghiệp."),
    ]

    for num, title, desc in steps:
        col_num, col_text = st.columns([0.5, 9.5])
        with col_num:
            st.markdown(
                f'<div style="'
                f'background:var(--accent-blue);color:white;'
                f'width:32px;height:32px;border-radius:50%;'
                f'display:flex;align-items:center;justify-content:center;'
                f'font-weight:700;font-size:0.9rem;'
                f'margin-top:4px;">{num}</div>',
                unsafe_allow_html=True,
            )
        with col_text:
            st.markdown(f"**{title}**")
            st.markdown(f"<span style='color:var(--text-secondary);font-size:0.9rem;'>{desc}</span>", unsafe_allow_html=True)
        st.markdown("")

    st.markdown("---")

    # Tự động chuyển bước nếu key đã được cài đặt
    if st.session_state.get("gemini_api_key", ""):
        if st.button("Tiếp tục →", key="step1_continue"):
            st.session_state["current_step"] = 2
            st.rerun()
    else:
        st.info("👈 Nhập API Key ở thanh bên trái để tiếp tục.")
