"""Reusable UI components: card, section_header, kpi_box, kpi_strip, step_indicator,
empty_state, tone_badge, action_row, error_banner.

Tất cả hàm chấp nhận key= khi wrap st.button/st.download_button để tránh
lỗi duplicate-key khi rerun.
"""
from contextlib import contextmanager
from typing import Optional

import streamlit as st

from src.ui import icons as ico

# ---------------------------------------------------------------------------
# Card context manager
# ---------------------------------------------------------------------------

@contextmanager
def card(title: str, icon_name: Optional[str] = None):
    """Context manager: mở card div, yield, đóng div sau.

    Usage:
        with card("Tiêu đề", "clipboard"):
            st.write("Nội dung...")
    """
    icon_svg = ico.icon(icon_name, 20) if icon_name else ""
    st.markdown(f'<div class="prod-card"><div class="prod-card-title">{icon_svg}{title}</div>', unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown("</div>", unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Section header
# ---------------------------------------------------------------------------

def section_header(title: str, icon_name: Optional[str] = None, subtitle: Optional[str] = None) -> None:
    """H3 section header với SVG icon tùy chọn."""
    icon_svg = ico.icon(icon_name, 22) if icon_name else ""
    sub = f'<p style="color:var(--text-secondary);margin:.25rem 0 0;font-size:.9rem;">{subtitle}</p>' if subtitle else ""
    st.markdown(f'<div style="display:flex;align-items:center;gap:10px;margin-top:.5rem;margin-bottom:.75rem;">{icon_svg}<h3 style="margin:0;color:var(--text-primary);font-weight:700;font-size:1.25rem;">{title}</h3></div>{sub}', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# KPI
# ---------------------------------------------------------------------------

def kpi_box(label: str, value: str, icon_name: Optional[str] = None) -> None:
    """Một KPI box đơn lẻ."""
    icon_svg = ico.icon(icon_name, 16) if icon_name else ""
    st.markdown(f'<div class="kpi-box"><div class="kpi-box-label">{icon_svg} {label}</div><div class="kpi-box-value">{value}</div></div>', unsafe_allow_html=True)


def kpi_strip(items: list[dict]) -> None:
    """Render 2-4 KPI boxes trong một hàng."""
    cols = st.columns(len(items))
    for col, item in zip(cols, items):
        with col:
            kpi_box(item.get("label", ""), item.get("value", ""), item.get("icon"))


# ---------------------------------------------------------------------------
# Step indicator
# ---------------------------------------------------------------------------

def step_indicator(current: int, completed: int = 0) -> None:
    """Thanh step indicator ngang."""
    labels = ["Cấu hình", "Upload", "Tùy chọn", "Kết quả"]
    parts = ""
    for i, label in enumerate(labels, 1):
        cls = "step-item step-item--done" if i <= completed else ("step-item step-item--active" if i == current else "step-item step-item--locked")
        inner = f"{ico.check()} {i}. {label}" if i <= completed else f"{i}. {label}"
        parts += f'<div class="{cls}">{inner}</div>'
        if i < len(labels):
            parts += '<div class="step-sep"></div>'
    st.markdown(f'<div class="step-indicator">{parts}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Empty state
# ---------------------------------------------------------------------------

def empty_state(icon_name: str, title: str, description: str,
                 cta_label: Optional[str] = None, cta_action: Optional[callable] = None) -> None:
    """Empty state block với icon, title, description và CTA button tùy chọn."""
    icon_svg = ico.icon(icon_name, 48)
    st.markdown(f'<div class="empty-state"><div class="empty-state-icon">{icon_svg}</div><div class="empty-state-title">{title}</div><p style="margin:.5rem 0 0;max-width:500px;">{description}</p></div>', unsafe_allow_html=True)
    if cta_label and cta_action and st.button(cta_label, key="empty_state_cta"):
        cta_action()


# ---------------------------------------------------------------------------
# Tone badge
# ---------------------------------------------------------------------------

_TONE_COLORS = {
    "chuyên nghiệp": ("#dbeafe", "#1d4ed8"),
    "căng thẳng":    ("#fee2e2", "#dc2626"),
    "cởi mở":       ("#dcfce7", "#16a34a"),
    "khẩn trương":   ("#ffedd5", "#ea580c"),
}


def tone_badge(text: str) -> str:
    """HTML string cho badge màu theo tone text."""
    colors = _TONE_COLORS.get(text.lower().strip(), ("#f1f5f9", "#475569"))
    return f'<span class="badge-tone" style="background:{colors[0]};color:{colors[1]};">{text}</span>'


# ---------------------------------------------------------------------------
# Action row
# ---------------------------------------------------------------------------

def action_row(task: str, assignee: str, deadline: str) -> None:
    """Một action item row với task, assignee, deadline."""
    st.markdown(f'<div class="action-row"><div class="action-row-task">{ico.check()} {task}</div><div class="action-row-assignee">👤 {assignee}</div><div class="action-row-deadline">📅 {deadline}</div></div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Error banner
# ---------------------------------------------------------------------------

_ERRORS = {
    "INVALID_KEY":     ("error-banner--yellow", "Sai API Key. Mở [AI Studio](https://aistudio.google.com/app/apikey) để cấp key mới.", "Xóa key đã lưu", "clear"),
    "RATE_LIMIT":      ("error-banner--orange", "Đang đợi throttling... vui lòng bấm Thử lại sau 20 giây.", "Thử lại", "retry"),
    "NETWORK":         ("error-banner--red",    "Mất kết nối. Kiểm tra mạng rồi thử lại.", "Thử lại", "retry"),
    "AUDIO_TOO_LARGE": ("error-banner--red",    "Tệp quá lớn để gửi. Hãy nén (mp3 64kbps) hoặc tách cuộc họp.", None, None),
    "MODEL_NOT_FOUND": ("error-banner--gray",   "Tất cả model đều tạm thời không khả dụng. Thử lại sau ít phút.", "Thử lại", "retry"),
}


def error_banner(error_code: str, recover_action: Optional[callable] = None) -> None:
    """Banner lỗi màu theo mã lỗi với nút hồi phục tùy chọn."""
    css, msg, btn_label, action = _ERRORS.get(error_code, _ERRORS["NETWORK"])
    if btn_label:
        if action == "clear" and st.button(btn_label, key="err_banner_clear"):
            from src.services import api_key as ak
            ak.clear_key()
            st.session_state["gemini_api_key"] = ""
            st.rerun()
        elif recover_action and st.button(btn_label, key="err_banner_recover"):
            recover_action()
    st.markdown(f'<div class="error-banner {css}">{msg}</div>', unsafe_allow_html=True)
