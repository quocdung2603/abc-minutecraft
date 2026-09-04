# MinuteCraft

Nền tảng tự động hóa biên bản ghi chép cuộc họp cho doanh nghiệp SME Việt Nam.
Nghe, phân tích và lập biên bản họp tự động bằng AI Gemini.

## Cài đặt

```bash
pip install -r requirements.txt
```

## Chạy ứng dụng

```bash
streamlit run app.py
```

## Tính năng

- 🎙️ **Tải file âm thanh** (.mp3, .wav, .m4a, .ogg) — tối đa 100MB
- 🤖 **Phân tích AI** bằng Gemini API — hỗ trợ tiếng Việt
- 📋 **Tóm tắt cuộc họp** — tiêu đề, chủ đề, quyết định, action items
- 🏷️ **Đánh giá không khí cuộc họp** (tone detection)
- 📄 **Xuất Word (.docx)** — có thể dùng mẫu công ty
- 📝 **Xuất Markdown (.md)**
- 🌙 **Dark mode tự động**

## Cấu trúc dự án

```
minutecraft/
├── app.py                          # Entry point chính (Streamlit)
├── src/
│   ├── config.py                   # Hằng số, model chain, system instruction
│   ├── state.py                    # Khởi tạo session_state cho 4 bước
│   ├── services/
│   │   ├── api_key.py             # Load / save / clear API key
│   │   ├── audio.py               # Chuẩn bị audio payload (inline / File API)
│   │   ├── gemini.py              # Gọi Gemini với fallback chain
│   │   ├── docx_export.py         # Tạo file Word (.docx)
│   │   └── markdown_export.py     # Build Markdown report
│   ├── ui/
│   │   ├── styles.py              # CSS tokens + inject_css()
│   │   ├── icons.py               # SVG icon helpers
│   │   ├── components.py          # card, kpi_box, step_indicator, error_banner...
│   │   └── layout.py              # render_header, render_sidebar, render_step_bar
│   └── pages/
│       ├── step_config.py          # Bước 1: Hướng dẫn + kiểm tra API key
│       ├── step_upload.py         # Bước 2: Dropzone + preview audio
│       ├── step_options.py         # Bước 3: Focus area + trigger analysis
│       └── step_result.py          # Bước 4: Hiển thị biên bản + download
├── bizsum-app.py                   # File gốc (monolithic, 786 dòng)
└── .api_key_cache                 # File cache API key (không commit)
```

## Luồng nghiệp vụ 4 bước

```
[1. Cấu hình] → [2. Upload] → [3. Tùy chọn & Phân tích] → [4. Kết quả]
    API Key        File audio      Focus area + Gemini API       Biên bản + Tải xuống
```

## Yêu cầu

- Python 3.10+
- Streamlit
- google-generativeai
- python-docx
- mutagen (tùy chọn, để hiển thị thời lượng audio)

---

## Refactor Verification (Sep 4, 2026)

### Modules

| File | Mô tả |
|------|--------|
| `app.py` | Entry point — routing 4 bước qua `st.session_state.current_step` |
| `src/config.py` | Hằng số, model chain, prompt, system instruction |
| `src/state.py` | `init_state()` — khởi tạo session_state mặc định |
| `src/pages/step_config.py` | Step 1: hướng dẫn + kiểm tra API key |
| `src/pages/step_upload.py` | Step 2: dropzone + preview audio + chọn model/temperature |
| `src/pages/step_options.py` | Step 3: focus area + custom instructions + trigger Gemini |
| `src/pages/step_result.py` | Step 4: KPI strip + tabs + download docx/md/csv |
| `src/services/api_key.py` | `load_key / save_key / clear_key` |
| `src/services/audio.py` | `prepare_audio_payload` — inline dict hoặc Gemini File API |
| `src/services/gemini.py` | `generate_minutes` — gọi Gemini + fallback chain + domain errors |
| `src/services/docx_export.py` | `generate_docx_report` — tạo/tô điển .docx từ result JSON |
| `src/services/markdown_export.py` | `build_markdown_report` + `sanitize_filename` |
| `src/ui/styles.py` | CSS tokens + `inject_css()` |
| `src/ui/icons.py` | `icon(name, size)` — inline SVG helpers |
| `src/ui/components.py` | card, kpi_box, step_indicator, error_banner, tone_badge… |
| `src/ui/layout.py` | `render_header / render_sidebar / render_step_bar` |

### Line-count table (≤ 250 dòng mỗi file ✅)

| File | Lines |
|------|-------|
| app.py | 33 |
| src/config.py | 62 |
| src/state.py | 24 |
| src/pages/step_config.py | 62 |
| src/pages/step_upload.py | 106 |
| src/pages/step_options.py | 209 |
| src/pages/step_result.py | 203 |
| src/services/api_key.py | 33 |
| src/services/audio.py | 184 |
| src/services/gemini.py | 177 |
| src/services/docx_export.py | 204 |
| src/services/markdown_export.py | 192 |
| src/ui/styles.py | 65 |
| src/ui/icons.py | 128 |
| src/ui/components.py | 144 |
| src/ui/layout.py | 128 |

App khởi động thành công trên cổng 8080 (`streamlit run app.py`) — không có regression.
