# Sử dụng Python 3.12-slim làm nền tảng
FROM python:3.12-slim

# Thiết lập thư mục làm việc trong container
WORKDIR /app

# Sao chép file requirements và cài đặt các thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn ứng dụng vào container
COPY . .

# Mở cổng 8080 phù hợp tiêu chuẩn Google Cloud Run
EXPOSE 8080

# Chạy ứng dụng Streamlit MinuteCraft
CMD ["streamlit", "run", "bizsum-app.py", "--server.port=8080", "--server.address=0.0.0.0"]
