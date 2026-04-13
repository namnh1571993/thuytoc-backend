FROM python:3.11-slim

WORKDIR /app

# Cài dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code
COPY . .

# Tạo thư mục data nếu chưa có
RUN mkdir -p /data

EXPOSE 8000

CMD ["python", "server.py"]
