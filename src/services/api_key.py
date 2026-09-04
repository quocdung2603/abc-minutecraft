"""Quản lý API key — load / save / clear từ file .api_key_cache."""
import os
import streamlit as st
from src.config import KEY_FILE


def load_key() -> str:
    """Đọc API key từ file cache. Trả về chuỗi rỗng nếu không tìm thấy."""
    if os.path.exists(KEY_FILE):
        try:
            with open(KEY_FILE, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            return ""
    return ""


def save_key(key: str) -> None:
    """Ghi API key xuống file cache."""
    try:
        with open(KEY_FILE, "w", encoding="utf-8") as f:
            f.write(key)
    except Exception:
        pass


def clear_key() -> None:
    """Xóa file cache chứa API key."""
    if os.path.exists(KEY_FILE):
        try:
            os.remove(KEY_FILE)
        except Exception:
            pass
