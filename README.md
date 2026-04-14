# 🌊 THUY TOC - Web & CRM System

Dự án quản lý bán hàng và Marketing tự động cho Thuỷ Tộc.

## 🚀 Hướng dẫn Deploy lên VPS Linux

### 1. Cài đặt môi trường
Đảm bảo VPS đã cài đặt Python 3.10+:
```bash
sudo apt update
sudo apt install python3-pip python3-venv nginx
```

### 2. Cài đặt dự án
```bash
git clone <your-repo-url>
cd THUY-TOC-LandingPage
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Cấu hình biến môi trường
Tạo file `.env` từ mẫu sau:
```bash
PORT=8000
RESEND_API_KEY=your_resend_api_key
FROM_EMAIL=your_verified_email@domain.com
FROM_NAME=Thuỷ Tộc
```

### 4. Chạy Server
Sử dụng Gunicorn để chạy ổn định hơn:
```bash
pip install gunicorn
gunicorn -w 1 -b 0.0.0.0:8000 server:AdminHandler
```
*(Lưu ý: handler trong server.py là AdminHandler)*

### 5. Cấu hình Nginx (Reverse Proxy)
Chỉnh sửa cấu hình Nginx để forward port 80 sang 8000.

### 6. Cấu hình SePay Webhook
Trỏ Webhook URL trên SePay về: `https://your-domain.com/api/sepay-webhook`

---
*Dự án thuộc chuỗi AI Challenge - Ngày 12.*
