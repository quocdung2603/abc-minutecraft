"""
Dịch vụ xử lý file âm thanh và chuẩn bị payload cho Gemini API.

Module này cung cấp hàm `prepare_audio_payload` để chuyển đổi file âm thanh thành
payload phù hợp cho `model.generate_content([payload, prompt])` của Gemini.

Có hai nhánh xử lý:
- Inline (<= MAX_INLINE_SIZE bytes): đóng gói bytes trực tiếp vào dict `{"mime_type", "data"}`.
- File API (> MAX_INLINE_SIZE bytes): ghi file ra temp disk, upload lên Gemini File API,
  và poll trạng thái cho đến khi PROCESSING hoàn tất hoặc FAILED.

Side-effects:
- Tạo file tạm trên disk khi file > MAX_INLINE_SIZE. Caller CÓ TRÁCH NHIỆM xóa file
  này sau khi dùng xong (`os.unlink(tmp_path)`).
- Upload file lên Gemini File API (có thể mất vài giây cho file lớn).
- Không tự động xóa genai.File — caller phải gọi `genai.delete_file(gemini_file.name)`.

Raises:
    AudioUploadFailed: khi Gemini File API trả về trạng thái FAILED sau khi poll.
"""
import os
import tempfile
import time
from typing import Optional, Union

import google.generativeai as genai
from google.generativeai.types import File as GeminiFile

from src.config import MAX_INLINE_SIZE


# ---------------------------------------------------------------------------
# Custom exception
# ---------------------------------------------------------------------------

class AudioUploadFailed(Exception):
    """
    Exception raised khi việc upload file âm thanh lên Gemini File API thất bại
    (trạng thái FAILED sau khi chờ PROCESSING xong).

    Attributes:
        file_name: Tên file mà việc upload thất bại.
    """

    def __init__(self, message: str, file_name: Optional[str] = None):
        super().__init__(message)
        self.file_name = file_name


# ---------------------------------------------------------------------------
# MIME type helpers
# ---------------------------------------------------------------------------

# Bản đồ extension → MIME type chuẩn. Chỉ dùng khi không có mime_type_hint hợp lệ.
_EXTENSION_MIME_MAP = {
    ".mp3": "audio/mp3",
    ".wav": "audio/wav",
    ".m4a": "audio/m4a",
    ".aac": "audio/m4a",     # Gemini không phân biệt m4a/aac
    ".ogg": "audio/ogg",
}

# Các MIME type mà Gemini/File API chấp nhận cho audio (dùng để kiểm tra mime_type_hint)
_RECOGNIZED_AUDIO_MIMES = frozenset({
    "audio/mp3",
    "audio/mpeg",
    "audio/wav",
    "audio/m4a",
    "audio/aac",
    "audio/ogg",
    "audio/x-m4a",
})


def _detect_mime_type(filename: str, mime_type_hint: str) -> str:
    """
    Xác định MIME type cuối cùng cho file âm thanh.

    Ưu tiên:
    1. mime_type_hint nếu nằm trong danh sách recognized audio MIME types.
    2. Tự động detect từ extension của filename.
    3. Fallback: "audio/mp3".

    Args:
        filename: Tên file gốc (để extract extension).
        mime_type_hint: MIME type do caller cung cấp.

    Returns:
        Chuỗi MIME type hợp lệ, ví dụ "audio/mp3", "audio/wav".
    """
    if mime_type_hint and mime_type_hint in _RECOGNIZED_AUDIO_MIMES:
        return mime_type_hint

    ext = os.path.splitext(filename)[1].lower()
    return _EXTENSION_MIME_MAP.get(ext, "audio/mp3")


# ---------------------------------------------------------------------------
# Main function
# ---------------------------------------------------------------------------

def prepare_audio_payload(
    file_bytes: bytes,
    filename: str,
    mime_type_hint: str,
) -> tuple[Union[dict, GeminiFile], Optional[str], Optional[GeminiFile]]:
    """
    Chuẩn bị audio payload cho `model.generate_content([payload, prompt])`.

    Logic:
    - Nếu `len(file_bytes) <= MAX_INLINE_SIZE`: đóng gói inline (`{"mime_type", "data"}`).
      Không tạo file tạm, `tmp_path=None`, `gemini_file=None`.
    - Nếu `len(file_bytes) > MAX_INLINE_SIZE`: ghi ra temp file, upload lên Gemini,
      poll trạng thái mỗi 2 giây cho đến khi state != PROCESSING.
      Nếu state == FAILED → raise AudioUploadFailed.
      Trả về `gemini_file` object để caller cleanup.

    Args:
        file_bytes: Nội dung nhị phân của file âm thanh.
        filename: Tên file gốc (dùng để detect MIME type và suffix cho temp file).
        mime_type_hint: MIME type do caller gợi ý. Sẽ được tin tưởng nếu hợp lệ.

    Returns:
        Tuple gồm 3 phần tử:
        - payload: dict `{"mime_type": str, "data": bytes}` cho inline,
                   HOẶC `genai.File` object cho File API.
        - tmp_path: Đường dẫn file tạm trên disk (None nếu inline).
                   Caller PHẢI gọi `os.unlink(tmp_path)` sau khi dùng xong.
        - gemini_file: `genai.File` object đã upload (None nếu inline).
                       Caller PHẢI gọi `genai.delete_file(gemini_file.name)` sau khi dùng xong.

    Raises:
        AudioUploadFailed: Khi upload lên Gemini File API thất bại (state == FAILED).
        OSError: Khi ghi file tạm thất bại (ví dụ disk full).
    """
    mime_type = _detect_mime_type(filename, mime_type_hint)
    file_size = len(file_bytes)

    # Nhánh inline: file nhỏ, đóng gói trực tiếp
    if file_size <= MAX_INLINE_SIZE:
        payload: Union[dict, GeminiFile] = {
            "mime_type": mime_type,
            "data": file_bytes,
        }
        return payload, None, None

    # Nhánh File API: file lớn, cần upload lên Gemini
    ext = os.path.splitext(filename)[1].lower()
    fd, tmp_path = tempfile.mkstemp(suffix=ext)
    try:
        # Ghi file_bytes ra file tạm (fd là file descriptor, cần đóng sau khi viết)
        with os.fdopen(fd, "wb") as fh:
            fh.write(file_bytes)

        # Upload lên Gemini File API
        gemini_file = genai.upload_file(path=tmp_path, mime_type=mime_type)

        # Poll cho đến khi không còn PROCESSING
        while gemini_file.state.name == "PROCESSING":
            time.sleep(2)
            gemini_file = genai.get_file(gemini_file.name)

        # Kiểm tra trạng thái cuối cùng
        if gemini_file.state.name == "FAILED":
            raise AudioUploadFailed(
                f"Upload audio file '{filename}' to Gemini File API failed "
                f"(state=FAILED). File size: {file_size} bytes.",
                file_name=filename,
            )

        # Thành công: trả về File handle để caller tự cleanup
        return gemini_file, tmp_path, gemini_file

    except AudioUploadFailed:
        # Re-raise AudioUploadFailed nguyên vẹn
        raise
    except Exception as exc:
        # Dọn dẹp temp file nếu có lỗi khác xảy ra trước khi trả về
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass  # ignore cleanup failure
        raise
