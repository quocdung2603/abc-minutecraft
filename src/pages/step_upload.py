"""Step 2: Dropzone + preview audio.

Chỉ render khi current_step == 2.
Sau khi upload thành công, lưu file vào session_state và chuyển sang step 3.
"""
import io

import streamlit as st

from src.ui.components import section_header, card
from src.ui import icons as ico
from src.config import SUPPORTED_AUDIO_EXT


def _format_size(size_bytes: int) -> str:
    """Format bytes as human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.2f} MB"


def _get_audio_duration(file_bytes: bytes, mime: str) -> str:
    """Try to extract duration using mutagen if available, else return ''."""
    try:
        import mutagen
        import mutagen.mp3
        import mutagen.wave
        bio = io.BytesIO(file_bytes)
        if mime.startswith("audio/mp3") or mime == "audio/mpeg":
            audio = mutagen.mp3.MP3(bio)
        else:
            audio = mutagen.File(bio)
        if audio and audio.info.length:
            mins, secs = divmod(int(audio.info.length), 60)
            return f"{mins}:{secs:02d}"
    except Exception:
        pass
    return ""


def render() -> None:
    """Render Step 2 page — chỉ hiển thị khi current_step == 2."""
    if st.session_state.get("current_step", 1) != 2:
        return

    # Nút quay lại
    if st.button("← Quay lại", key="step2_back"):
        st.session_state["current_step"] = 1
        st.rerun()

    section_header("Tải Lên File Ghi Âm", icon_name="upload", subtitle="Hỗ trợ mp3, wav, m4a, ogg (tối đa 100MB)")

    # Dropzone style file uploader
    uploaded_file = st.file_uploader(
        "Kéo thả hoặc chọn tệp âm thanh cuộc họp",
        type=list(SUPPORTED_AUDIO_EXT),
        help="Kéo thả tệp hoặc bấm để chọn",
        key="step2_file_uploader",
    )

    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        mime = getattr(uploaded_file, "type", "audio/mp3") or "audio/mp3"
        filename = uploaded_file.name

        # Lưu vào session_state
        st.session_state["uploaded_file_bytes"] = file_bytes
        st.session_state["uploaded_filename"] = filename
        st.session_state["uploaded_mime"] = mime

        # File info card
        with card("Thông tin tệp ghi âm", icon_name="audio"):
            col_name, col_size, col_dur = st.columns(3)
            with col_name:
                st.markdown(f"**Tên:** `{filename}`")
            with col_size:
                st.markdown(f"**Kích thước:** {_format_size(len(file_bytes))}")
            with col_dur:
                duration = _get_audio_duration(file_bytes, mime)
                if duration:
                    st.markdown(f"**Thời lượng:** {duration}")
                else:
                    st.markdown("**Thời lượng:** —")

        # Audio player
        st.audio(file_bytes, format=mime)

        # Nút chuyển bước
        st.markdown("")
        col_prev, col_next = st.columns([1, 1])
        with col_prev:
            if st.button("← Quay lại", key="step2_back2"):
                st.session_state["current_step"] = 1
                st.rerun()
        with col_next:
            if st.button("Tiếp tục →", key="step2_next"):
                st.session_state["current_step"] = 3
                st.rerun()
    else:
        # Xóa file đã lưu nếu không có file mới
        st.session_state["uploaded_file_bytes"] = None
        st.session_state["uploaded_filename"] = None
        st.session_state["uploaded_mime"] = None
