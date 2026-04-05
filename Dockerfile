# Dùng bản Python nhẹ
FROM python:3.9-slim

WORKDIR /app

# Copy và cài đặt thư viện trước
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào
COPY . .

# Render tự động map cổng, nhưng ta khai báo cho rõ ràng
EXPOSE 10000

# Lệnh khởi chạy
CMD ["python", "app.py"]
