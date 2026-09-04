"""Step 3: Focus area + template + custom instructions + trigger analysis.

Chỉ render khi current_step == 3.
Gọi Gemini API, hiển thị progress, xử lý lỗi, lưu kết quả và chuyển sang step 4.
"""
import time

import streamlit as st

import google.generativeai as genai

from src.config import FOCUS_AREAS, BASE_PROMPT, SYSTEM_INSTRUCTION, HISTORY_LIMIT
from src.services import gemini as gm
from src.services import audio as audio_svc
from src.services import api_key as ak
from src.ui.components import section_header, card, error_banner
from src.ui import icons as ico


def render() -> None:
    """Render Step 3 page — chỉ hiển thị khi current_step == 3."""
    if st.session_state.get("current_step", 1) != 3:
        return

    if st.button("← Quay lại", key="step3_back"):
        st.session_state["current_step"] = 2
        st.run()

    section_header("Tùy Chỉnh Phân Tích", icon_name="gear", subtitle="Chọn trọng tâm và tải mẫu Word tùy chọn")

    # --- Focus area cards ---
    st.markdown("**Chọn trọng tâm phân tích:**")
    cols = st.columns(len(FOCUS_AREAS))
    current_focus = st.session_state.get("focus_area", FOCUS_AREAS[0])
    focus_idx = FOCUS_AREAS.index(current_focus) if current_focus in FOCUS_AREAS else 0

    # Dùng radio ngầm qua selectbox để chọn
    selected_focus = st.selectbox(
        "Trọng tâm phân tích",
        FOCUS_AREAS,
        index=focus_idx,
        label_visibility="collapsed",
        key="step3_focus_select",
    )
    st.session_state["focus_area"] = selected_focus

    st.markdown("")

    # --- Template uploader ---
    with card("Mẫu Word tùy chọn (.docx)", icon_name="document"):
        template_file = st.file_uploader(
            "Tải lên mẫu biên bản Word của công ty (không bắt buộc)",
            type=["docx"],
            help="Hệ thống sẽ điền dữ liệu vào placeholder {{TEN_CUOC_HOP}}, {{TOM_TAT}}...",
            key="step3_template_uploader",
        )
        if template_file:
            st.session_state["template_bytes"] = template_file.getvalue()
            st.session_state["template_filename"] = template_file.name
            st.success(f"Đã chọn: {template_file.name}")
        else:
            st.session_state["template_bytes"] = None
            st.session_state["template_filename"] = None

    # --- Custom instructions ---
    with card("Yêu cầu bổ sung", icon_name="clipboard"):
        custom_instr = st.text_area(
            "Hướng dẫn tuỳ chỉnh (không bắt buộc):",
            value=st.session_state.get("custom_instructions", ""),
            placeholder="VD: Định dạng ngày DD/MM/YYYY; sử dụng thuật ngữ chuyên ngành...",
            label_visibility="collapsed",
            key="step3_instructions",
        )
        st.session_state["custom_instructions"] = custom_instr

    st.markdown("")

    # --- Sticky analyze button ---
    st.markdown("---")
    if not st.button("🚀 Bắt đầu Phân tích", key="step3_analyze", use_container_width=True):
        return

    # === Analysis flow ===
    api_key = st.session_state.get("gemini_api_key", "")
    if not api_key:
        error_banner("INVALID_KEY")
        return

    genai.configure(api_key=api_key)

    file_bytes = st.session_state.get("uploaded_file_bytes")
    filename = st.session_state.get("uploaded_filename", "meeting.mp3")
    mime = st.session_state.get("uploaded_mime", "audio/mp3")

    if not file_bytes:
        st.error("Không tìm thấy tệp âm thanh. Vui lòng tải lại.")
        return

    model_choice = st.session_state.get("model_choice", "gemini-3.6-flash")
    temperature = st.session_state.get("temperature", 0.1)
    focus = st.session_state.get("focus_area", FOCUS_AREAS[0])
    custom_instr = st.session_state.get("custom_instructions", "")

    # Build prompt
    prompt = BASE_PROMPT
    if focus == "Chỉ tập trung vào Danh sách Việc cần làm (Action Items)":
        prompt += " Đặc biệt tập trung bóc tách chi tiết các nhiệm vụ được giao."
    elif focus == "Tập trung vào các Ý kiến đóng góp và Tranh luận (Brainstorming Details)":
        prompt += " Đặc biệt tập trung ghi nhận chi tiết các luồng tranh biện."
    elif focus == "Trích xuất nhanh các Mốc thời gian & Deadline quan trọng":
        prompt += " Đặc biệt chú ý các cột mốc thời gian và thời hạn hoàn thành."
    if custom_instr:
        prompt += f" Lưu ý: {custom_instr}"

    tmp_path = None
    gemini_file = None

    try:
        # Phase 1: Upload audio
        with st.status("Đang tải tệp...", state="running", expanded=True) as status:
            status.update(label="1️⃣ Đang tải tệp lên...", state="running")
            payload, tmp_path, gemini_file = audio_svc.prepare_audio_payload(
                file_bytes, filename, mime,
            )
            status.update(label="✓ Tải tệp thành công!", state="complete")

        st.progress(0.25)

        # Phase 2: Send to Gemini
        with st.status("Đang gửi tới Gemini...", state="running", expanded=True) as status2:
            status2.update(label="2️⃣ Đang gửi tới Gemini...", state="running")
            status2.update(label="✓ Đã gửi! Đang chờ phân tích...", state="running")

        st.progress(0.5)

        # Phase 3: Analyze
        with st.status("Đang phân tích...", state="running", expanded=True) as status3:
            status3.update(label="3️⃣ Đang phân tích nội dung cuộc họp...", state="running")
            try:
                result, _ = gm.generate_minutes(
                    audio_payload=payload,
                    prompt=prompt,
                    temperature=temperature,
                    system_instruction=SYSTEM_INSTRUCTION,
                    preferred_model=model_choice,
                )
                status3.update(label="✓ Phân tích hoàn tất!", state="complete")
            except Exception as anal_err:
                err_str = str(anal_err)
                if any(x in err_str for x in ["429", "Quota", "RESOURCE_EXHAUSTED"]):
                    error_banner("RATE_LIMIT")
                    st.stop()
                elif any(x in err_str for x in ["404", "not found", "no longer available"]):
                    error_banner("MODEL_NOT_FOUND")
                    st.stop()
                elif any(x in err_str for x in ["INVALID_API_KEY", "API_KEY_INVALID"]):
                    error_banner("INVALID_KEY")
                    st.stop()
                else:
                    error_banner("NETWORK")
                    st.stop()

        st.progress(0.75)

        # Phase 4: Save result
        with st.status("Đang lưu kết quả...", state="running") as status4:
            status4.update(label="4️⃣ Đang lưu kết quả...", state="running")

            st.session_state["analysis_result"] = result

            # Push to history
            history = st.session_state.get("history", [])
            history.insert(0, {"result": result, "filename": filename})
            history = history[:HISTORY_LIMIT]
            st.session_state["history"] = history

            status4.update(label="✓ Hoàn tất!", state="complete")

        st.progress(1.0)
        st.balloons()
        st.success("Đã hoàn thành biên bản họp tự động!")

        # Chuyển sang step 4
        st.session_state["current_step"] = 4
        st.rerun()

    except Exception as e:
        err_str = str(e)
        if "429" in err_str or "Quota" in err_str:
            error_banner("RATE_LIMIT")
        elif "INVALID_API_KEY" in err_str or "API_KEY_INVALID" in err_str:
            error_banner("INVALID_KEY")
        else:
            error_banner("NETWORK")

    finally:
        # Cleanup tmp file
        if tmp_path:
            try:
                import os
                os.unlink(tmp_path)
            except Exception:
                pass
        # Cleanup Gemini file
        if gemini_file:
            try:
                genai.delete_file(gemini_file.name)
            except Exception:
                pass
