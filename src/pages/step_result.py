"""Step 4: Hiển thị biên bản + KPI + tabs + download.

Chỉ render khi current_step == 4.
Cho phép xem lịch sử, tải docx/md, sao chép markdown.
"""
import io

import streamlit as st

from src.config import HISTORY_LIMIT
from src.services import docx_export
from src.services import markdown_export
from src.ui.components import (
    section_header, card, kpi_strip, tone_badge,
    action_row, error_banner,
)
from src.ui import icons as ico


def _format_size(size_bytes: int) -> str:
    if size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    return f"{size_bytes / (1024 * 1024):.2f} MB"


def _build_csv(actions: list) -> str:
    lines = ["Nhiệm vụ,Người phụ trách,Hạn chót"]
    for a in actions:
        task = a.get("task", "").replace('"', '""')
        assignee = a.get("assignee", "").replace('"', '""')
        deadline = a.get("deadline", "").replace('"', '""')
        lines.append(f'"{task}","{assignee}","{deadline}"')
    return "\n".join(lines)


def _safe_result() -> dict:
    return st.session_state.get("analysis_result", {}) or {}


def render() -> None:
    """Render Step 4 page — chỉ hiển thị khi current_step == 4."""
    if st.session_state.get("current_step", 1) != 4:
        return

    result = _safe_result()
    meeting_title = result.get("meeting_title", "Cuộc họp không có tiêu đề")
    tone = result.get("meeting_tone", "Chuyên nghiệp")
    actions = result.get("action_items", []) or []
    decisions = result.get("decisions", []) or []
    topics = result.get("key_topics", []) or []
    summary = result.get("summary", "Không có tóm tắt.")

    file_bytes = st.session_state.get("uploaded_file_bytes")
    file_size = _format_size(len(file_bytes)) if file_bytes else "—"

    # --- Header ---
    col_title, col_btns = st.columns([3, 1])
    with col_title:
        st.markdown(f"## {meeting_title}")
        st.markdown(tone_badge(tone), unsafe_allow_html=True)
    with col_btns:
        if st.button("🔄 Phân tích lại", key="result_rerun"):
            st.session_state["current_step"] = 2
            st.rerun()
        if st.button("➕ Bắt đầu mới", key="result_new"):
            # Clear all state
            for key in list(st.session_state.keys()):
                if key not in ("current_step",):
                    del st.session_state[key]
            from src.state import DEFAULT_STATE
            for k, v in DEFAULT_STATE.items():
                st.session_state.setdefault(k, v)
            st.session_state["current_step"] = 1
            st.rerun()

    st.markdown("")

    # --- KPI strip ---
    kpi_strip([
        {"label": "Không khí", "value": tone, "icon": "audio"},
        {"label": "Action Items", "value": f"{len(actions)} Công việc", "icon": "clipboard"},
        {"label": "Quyết định", "value": f"{len(decisions)} Quyết định", "icon": "check"},
        {"label": "Kích thước file", "value": file_size, "icon": "document"},
    ])

    # --- Tóm tắt ---
    with card("Tóm tắt tổng quan", icon_name="clipboard"):
        st.write(summary)

    # --- Tabs ---
    tab_topics, tab_decisions, tab_actions = st.tabs([
        "📋 Chủ đề", "✅ Quyết định", "📌 Action Items",
    ])

    with tab_topics:
        if topics:
            for idx, topic in enumerate(topics):
                t_name = topic.get("topic_name", f"Chủ đề {idx+1}") if isinstance(topic, dict) else str(topic)
                t_points = topic.get("discussion_points", "") if isinstance(topic, dict) else ""
                with st.expander(f"Chủ đề {idx+1}: {t_name}", expanded=True):
                    st.write(t_points)
        else:
            st.info("Không phát hiện chủ đề thảo luận cụ thể.")

    with tab_decisions:
        if decisions:
            for dec in decisions:
                st.markdown(f"- **{dec}**")
        else:
            st.info("Chưa ghi nhận quyết định thống nhất chính thức nào.")

    with tab_actions:
        if actions:
            st.markdown("**Danh sách công việc:**")
            for act in actions:
                if isinstance(act, dict):
                    action_row(
                        act.get("task", "Chưa rõ"),
                        act.get("assignee", "Chưa chỉ định"),
                        act.get("deadline", "Chưa rõ"),
                    )
            st.markdown("")

            # Export buttons
            col_csv, col_md = st.columns(2)
            csv_data = _build_csv(actions)
            with col_csv:
                st.download_button(
                    "📋 Sao chép CSV",
                    data=csv_data,
                    file_name="action_items.csv",
                    mime="text/csv",
                    key="result_csv_btn",
                )
            with col_md:
                md_text = markdown_export.build_markdown_report(result, meeting_title)
                st.code(md_text, language="markdown", key="result_md_code")
        else:
            st.info("Không phát hiện nhiệm vụ được giao cụ thể trong cuộc họp.")

    st.markdown("---")

    # --- Lịch sử phiên ---
    history = st.session_state.get("history", [])
    if len(history) > 1:
        with st.expander("📜 Lịch sử phiên này"):
            options = [f"{i+1}. {h.get('filename', 'file')}" for i, h in enumerate(history)]
            selected_idx = st.selectbox(
                "Xem kết quả trước:",
                range(len(options)),
                format_func=lambda i: options[i],
                key="history_select",
            )
            hist_item = history[selected_idx]
            hist_result = hist_item.get("result", {})
            hist_title = hist_result.get("meeting_title", "Kết quả trước")
            hist_tone = hist_result.get("meeting_tone", "")
            hist_actions = hist_result.get("action_items", []) or []
            hist_decisions = hist_result.get("decisions", []) or []
            hist_topics = hist_result.get("key_topics", []) or []
            hist_summary = hist_result.get("summary", "")

            st.markdown(f"### {hist_title}")
            st.markdown(tone_badge(hist_tone), unsafe_allow_html=True)
            st.markdown(hist_summary)
            st.markdown(f"**Quyết định:** {len(hist_decisions)} | **Actions:** {len(hist_actions)}")

    st.markdown("---")

    # --- Download buttons ---
    section_header("Tải Xuống Biên Bản", icon_name="download")

    template_bytes = st.session_state.get("template_bytes")
    sanitized = markdown_export.sanitize_filename(meeting_title)

    col_docx, col_md = st.columns(2)
    with col_docx:
        docx_bytes = docx_export.generate_docx_report(result, meeting_title, template_bytes)
        st.download_button(
            "📄 Tải Word (.docx)",
            data=docx_bytes,
            file_name=f"Bien_ban_hop_{sanitized}.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            use_container_width=True,
            key="result_docx_btn",
        )
    with col_md:
        md_bytes = markdown_export.build_markdown_report(result, meeting_title).encode("utf-8")
        st.download_button(
            "📝 Tải Markdown (.md)",
            data=md_bytes,
            file_name=f"Bien_ban_hop_{sanitized}.md",
            mime="text/markdown",
            use_container_width=True,
            key="result_md_btn",
        )

    st.markdown("")

    # Clipboard copy via st.code
    md_full = markdown_export.build_markdown_report(result, meeting_title)
    st.code(md_full, language="markdown", key="result_clipboard_code")
    st.caption("↑ Sao chép nội dung Markdown ở trên để dán vào nơi khác.")
