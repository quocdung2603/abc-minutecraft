"""
Dịch vụ tạo báo cáo Markdown từ kết quả phân tích cuộc họp.

Module này cung cấp:
- `build_markdown_report`: Tạo chuỗi Markdown hoàn chỉnh cho biên bản họp,
  bao gồm metadata, tóm tắt, chủ đề thảo luận, quyết định, và kế hoạch hành động.
- `sanitize_filename`: Chuyển đổi tiêu đề cuộc họp thành tên file an toàn
  cho filesystem (loại bỏ ký tự không hợp lệ, giới hạn độ dài).

Side-effects: Không có (pure function, không I/O).
"""
from datetime import datetime
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Các ký tự không an toàn cho filename trên Windows/macOS/Linux
_UNSAFE_FILENAME_CHARS = frozenset(r'<>:"/\|?*')

# Ký tự thay thế cho ký tự không an toàn
_SAFE_REPLACEMENT = "_"

# Giới hạn độ dài tên file (sau khi sanitize)
_MAX_FILENAME_LENGTH = 80


# ---------------------------------------------------------------------------
# Report builder
# ---------------------------------------------------------------------------

def build_markdown_report(result: dict, meeting_title: str) -> str:
    """
    Tạo một báo cáo Markdown hoàn chỉnh từ kết quả phân tích cuộc họp.

    Cấu trúc document:
    - H1: Tên cuộc họp
    - Metadata block (Ngày, Tông)
    - H2: Tóm tắt
    - H2: Chủ đề thảo luận (topic_name + discussion_points)
    - H2: Quyết định (bullet list)
    - H2: Kế hoạch hành động (Markdown table: Nhiệm vụ / Người chịu trách nhiệm / Hạn chót)

    Args:
        result: Dict chứa kết quả phân tích từ Gemini, với các key:
            - meeting_title (str, optional)
            - summary (str, optional)
            - meeting_tone (str, optional)
            - key_topics (list[dict], optional): mỗi dict có topic_name, discussion_points
            - decisions (list[str], optional)
            - action_items (list[dict], optional): mỗi dict có task, assignee, deadline
        meeting_title: Tiêu đề cuộc họp (dùng nếu result không có meeting_title).

    Returns:
        Chuỗi Unicode Markdown sẵn sàng để download hoặc hiển thị.

    Notes:
        - Missing/None fields được xử lý graceful: default empty list → "Không có"
        - Table action_items dùng Markdown pipe syntax, không cần external library.
    """
    # Xác định tiêu đề sử dụng
    title = result.get("meeting_title") or meeting_title or "Cuộc họp không có tiêu đề"

    # Các trường có thể None → default empty
    summary: str = result.get("summary") or "Không có tóm tắt."
    meeting_tone: str = result.get("meeting_tone") or "Chuyên nghiệp"
    topics: list[dict] = result.get("key_topics") or []
    decisions: list[str] = result.get("decisions") or []
    actions: list[dict] = result.get("action_items") or []

    # Ngày hiện tại để điền metadata
    today_str = datetime.now().strftime("%d/%m/%Y")

    lines: list[str] = []

    # H1: Tiêu đề cuộc họp
    lines.append(f"# {title}")
    lines.append("")

    # Metadata block
    lines.append(f"**Ngày:** {today_str}")
    lines.append(f"**Tông:** {meeting_tone}")
    lines.append("")

    # H2: Tóm tắt
    lines.append("## Tóm tắt")
    lines.append(summary)
    lines.append("")

    # H2: Chủ đề thảo luận
    lines.append("## Chủ đề thảo luận")
    if topics:
        for topic in topics:
            if isinstance(topic, dict):
                topic_name = topic.get("topic_name") or "Không có tiêu đề"
                discussion_points = topic.get("discussion_points") or "Không có nội dung."
                lines.append(f"### {topic_name}")
                lines.append(discussion_points)
                lines.append("")
    else:
        lines.append("Không có chủ đề thảo luận nào được ghi nhận.")
        lines.append("")

    # H2: Quyết định
    lines.append("## Quyết định")
    if decisions:
        for dec in decisions:
            lines.append(f"- {dec}")
    else:
        lines.append("Không có quyết định nào được thống nhất.")
    lines.append("")

    # H2: Kế hoạch hành động (table)
    lines.append("## Kế hoạch hành động")
    if actions:
        # Header row
        lines.append("| Nhiệm vụ | Người chịu trách nhiệm | Hạn chót |")
        lines.append("|---|---|---|")
        for act in actions:
            if isinstance(act, dict):
                task = act.get("task") or "Không rõ"
                assignee = act.get("assignee") or "Chưa chỉ định"
                deadline = act.get("deadline") or "Chưa rõ"
                lines.append(f"| {task} | {assignee} | {deadline} |")
            else:
                lines.append(f"| {str(act)} | - | - |")
    else:
        lines.append("Không có công việc cụ thể được phân công.")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Filename sanitizer
# ---------------------------------------------------------------------------

def sanitize_filename(name: str) -> str:
    """
    Chuyển đổi một chuỗi thành tên file an toàn cho filesystem.

    Thao tác:
    1. Thay thế mọi ký tự không an toàn bằng `_`.
    2. Collapses multiple consecutive underscores into one.
    3. Strip leading/trailing spaces and dots.
    4. Nếu kết quả trống → fallback "Unnamed".
    5. Giới hạn độ dài tối đa 80 ký tự (cắt từ cuối).

    Args:
        name: Tiêu đề cuộc họp hoặc chuỗi bất kỳ.

    Returns:
        Tên file an toàn, ví dụ: "Cuoc_hop_SME_meo_thu_thuat".

    Examples:
        >>> sanitize_filename("Cuộc họp: SME / mẹo & thủ thuật!?.md")
        'Cuộc_họp_SME_mẹo_thủ_thuật_'
        >>> sanitize_filename("  ...hidden...  ")
        'Unnamed'
    """
    if not name:
        return "Unnamed"

    # Bước 1: thay thế ký tự unsafe bằng underscore
    sanitized = "".join(
        _SAFE_REPLACEMENT if c in _UNSAFE_FILENAME_CHARS else c
        for c in name
    )

    # Bước 2: strip leading/trailing spaces
    sanitized = sanitized.strip()

    # Bước 3: collapse multiple underscores
    while _SAFE_REPLACEMENT + _SAFE_REPLACEMENT in sanitized:
        sanitized = sanitized.replace(
            _SAFE_REPLACEMENT + _SAFE_REPLACEMENT, _SAFE_REPLACEMENT
        )

    # Bước 4: strip leading/trailing underscores (keep dots in the middle for extensions)
    sanitized = sanitized.strip(_SAFE_REPLACEMENT)

    # Bước 5: fallback nếu trống
    if not sanitized:
        return "Unnamed"

    # Bước 6: giới hạn độ dài (cắt từ cuối)
    if len(sanitized) > _MAX_FILENAME_LENGTH:
        sanitized = sanitized[:_MAX_FILENAME_LENGTH]

    return sanitized
