# Sử dụng Python image chính thức
FROM python:3.10-slim

# Đặt thư mục làm việc
WORKDIR /app

# Sao chép các file vào container
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép mã nguồn
COPY . .

# Expose cổng 8000
EXPOSE 8000

# Chạy ứng dụng Flask bằng gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]
