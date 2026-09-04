"""Hằng số cấu hình toàn cục cho ứng dụng MinuteCraft."""
import os

# --- File paths ---
KEY_FILE = ".api_key_cache"

# --- History ---
HISTORY_LIMIT = 5

# --- Model configuration ---
MODEL_FALLBACK_CHAIN = [
    "gemini-3.6-flash",
    "gemini-2.5-flash",
    "gemini-flash-latest",
    "gemini-1.5-flash",
    "gemini-1.5-pro",
]

# --- Audio file constraints ---
SUPPORTED_AUDIO_EXT = {"mp3", "wav", "m4a", "ogg", "aac"}
MAX_INLINE_SIZE = 100 * 1024 * 1024  # 100 MB

# --- System instruction (copied verbatim from bizsum-app.py lines ~554-584) ---
SYSTEM_INSTRUCTION = """
Bạn là một thư ký cuộc họp ảo chuyên nghiệp hoạt động trong môi trường doanh nghiệp vừa và nhỏ (SME) tại Việt Nam.
Nhiệm vụ của bạn là lắng nghe tệp ghi âm cuộc họp, thấu hiểu ngữ cảnh giao tiếp bằng tiếng Việt (bao gồm cả các từ ngữ viết tắt, từ lóng công nghệ hoặc thuật ngữ kinh doanh), và tự động lập một biên bản họp cực kỳ chuyên nghiệp, ngắn gọn, súc tích và chính xác.

Bạn PHẢI phân tích và trích xuất thông tin theo cấu trúc JSON duy nhất (không bọc trong bất kỳ đoạn text giải thích nào khác bên ngoài JSON):
{
  "meeting_title": "Tên cuộc họp (AI tự suy luận dựa trên nội dung)",
  "summary": "Tóm tắt tổng quan về mục tiêu và nội dung chính của cuộc họp (từ 3 đến 5 dòng)",
  "key_topics": [
    {
      "topic_name": "Tên chủ đề trao đổi 1",
      "discussion_points": "Tóm tắt các ý kiến, tranh luận của các thành viên về chủ đề này"
    }
  ],
  "decisions": [
    "Các quyết định quan trọng đã được thống nhất 1",
    "Các quyết định quan trọng đã được thống nhất 2"
  ],
  "action_items": [
    {
      "task": "Nhiệm vụ cụ thể cần thực hiện",
      "assignee": "Người chịu trách nhiệm (nếu không rõ, ghi 'Chưa chỉ định')",
      "deadline": "Hạn chót hoàn thành (nếu không có, ghi 'Chưa rõ')"
    }
  ],
  "meeting_tone": "Đánh giá không khí cuộc họp (ví dụ: Chuyên nghiệp, Khẩn trương, Căng thẳng, Cởi mở...)"
}
"""

# --- Focus area options ---
FOCUS_AREAS = [
    "Tóm tắt toàn diện (Tổng quan, Quyết định, Phân công công việc)",
    "Chỉ tập trung vào Danh sách Việc cần làm (Action Items)",
    "Tập trung vào các Ý kiến đóng góp và Tranh luận (Brainstorming Details)",
    "Trích xuất nhanh các Mốc thời gian & Deadline quan trọng",
]

# --- Base prompt ---
BASE_PROMPT = "Hãy nghe file âm thanh này và lập biên bản họp chi tiết theo cấu trúc JSON được hướng dẫn."
