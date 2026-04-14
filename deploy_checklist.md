# 🚀 DEPLOY CHECKLIST - THUY TOC PROJECT

Dự án đã sẵn sàng để đưa lên VPS Linux. Dưới đây là kết quả kiểm tra toàn bộ thư mục.

## 1. Ngôn ngữ & Framework
- **Backend:** Python 3 (sử dụng thư viện chuẩn `http.server` đã tùy biến).
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla).
- **Database:** SQLite 3 (`brain.db`).
- **Dịch vụ tích hợp:** 
    - **Resend:** Gửi email tự động.
    - **SePay:** Xử lý thanh toán qua Webhook.

## 2. Các file cần bổ sung / Chỉnh sửa
- [x] **`.env`**: Đã tạo và cấu hình đầy đủ.
- [x] **`.gitignore`**: Đã thêm để bảo vệ các file nhạy cảm.
- [x] **`README.md`**: Đã soạn thảo hướng dẫn Deploy chi tiết.
- [x] **`requirements.txt`**: Đã cập nhật đầy đủ các thư viện cần thiết.

## 3. Cảnh báo bảo mật (Secret Keys) ✅
- [x] **Phát hiện:** `resend_config.txt` đang chứa API Key thật của Resend.
- [x] **Action:** Đã xóa file và chuyển thông tin vào `.env`.

## 4. Danh sách chuẩn bị trước khi Deploy
1. **VPS:** Đã có IP và quyền truy cập SSH (Root/Sudo).
2. **Domain:** Đã có tên miền trỏ về IP VPS.
3. **Nginx:** Cần cài đặt để làm Reverse Proxy (chuyển hướng từ port 80/443 vào port 8000).
4. **Python Environ:** Cài đặt `python3-pip` và `python3-venv` trên VPS.
5. **SSL:** Cài đặt Certbot (Let's Encrypt) để chạy HTTPS.
6. **SePay Webhook:** Cập nhật URL Webhook trên bảng điều khiển SePay từ `localhost` thành domain thật của bạn (ví dụ: `https://yourdomain.com/api/sepay-webhook`).

---
**Tình trạng:** 🟡 Cần xử lý các mục được tick trống ở trên để đảm bảo an toàn.
