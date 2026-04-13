import http.server
import socketserver
import json
import urllib.parse
import sqlite3
import re
from datetime import datetime
import os
import threading
import time

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    print('[EMAIL] ⚠️  Package resend chưa cài. Chạy: pip3 install resend')


def load_resend_config():
    """Đọc API Key và cấu hình từ resend_config.txt"""
    config = {}
    cfg_path = os.path.join(DIRECTORY, 'resend_config.txt')
    try:
        with open(cfg_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    config[k.strip()] = v.strip()
    except Exception as e:
        print(f'[EMAIL] ⚠️  Không đọc được resend_config.txt: {e}')
    return config


def get_resend_client():
    """Set up Resend API key từ config file"""
    if not RESEND_AVAILABLE:
        return None
    cfg = load_resend_config()
    api_key = cfg.get('RESEND_API_KEY', '')
    if not api_key or api_key == 'PASTE_YOUR_API_KEY_HERE':
        print('[EMAIL] ⚠️  Chưa có API Key Resend trong resend_config.txt')
        return None
    resend.api_key = api_key
    return cfg


def send_email(to_email, subject, html_body, from_name='Thuỷ Tộc Water Sports', from_email='onboarding@resend.dev'):
    """Gửi email qua Resend API"""
    cfg = get_resend_client()
    if cfg is None:
        print(f'[EMAIL] ❌ Bỏ qua gửi email đến {to_email} — chưa cấu hình Resend')
        return False
    # Dùng from email từ config nếu có
    from_email = cfg.get('FROM_EMAIL', from_email)
    from_name  = cfg.get('FROM_NAME', from_name)
    try:
        params = {
            'from': f'{from_name} <{from_email}>',
            'to': [to_email],
            'subject': subject,
            'html': html_body,
        }
        result = resend.Emails.send(params)
        email_id = result.get('id', '?')
        print(f'[EMAIL] \u2705 \u0110\u00e3 g\u1eedi "{subject}" \u2192 {to_email} | id={email_id}')
        return True
    except Exception as e:
        print(f'[EMAIL] ❌ Lỗi gửi đến {to_email}: {e}')
        return False


def make_email_1(name):
    subject = 'Mình rất vui vì bạn ở đây 🌊'
    html = f'''
    <div style="font-family:Georgia,serif;max-width:580px;margin:0 auto;color:#1a1a1a;line-height:1.8">
      <p style="font-size:1rem">Chào {name},</p>
      <p>Mình là Thuỷ Tộc.</p>
      <p>Không phải một trung tâm thể thao biển thông thường — mà là nơi mình tin rằng nước biển dạy cho người ta rất nhiều thứ mà sách không dạy được.</p>
      <p>Cảm giác lần đầu đứng lên ván giữa sóng. Khoảnh khắc gió diều kéo người ra khỏi mặt nước. Hay chỉ đơn giản là ngồi trên SUP nhìn mặt trời lặn ở Phú Quốc.</p>
      <p>Bạn vừa đăng ký — điều đó có nghĩa là bạn đang tìm kiếm điều gì đó.</p>
      <p><strong>Mình sẽ ở đây, cùng bạn tìm.</strong></p>
      <p>Vài ngày tới mình sẽ chia sẻ thêm — không phải quảng cáo, mà là những thứ mình thực sự học được từ biển.</p>
      <p>Cứ reply email này nếu có câu hỏi. Mình đọc và trả lời từng cái.</p>
      <p style="margin-top:32px">Hẹn gặp ngoài biển,<br><strong>Thuỷ Tộc 🌊</strong></p>
    </div>'''
    return subject, html


def make_email_2(name):
    subject = 'Điều biển dạy mình mà 10 năm sống trên cạn không dạy được'
    html = f'''
    <div style="font-family:Georgia,serif;max-width:580px;margin:0 auto;color:#1a1a1a;line-height:1.8">
      <p>Chào {name},</p>
      <p>Có một thứ mình học được sau hàng trăm buổi lướt ván.</p>
      <p><strong>Biển không quan tâm bạn là ai.</strong></p>
      <p>Bạn giàu hay nghèo. Giỏi hay dở. Tự tin hay lo lắng — sóng vẫn vỡ đúng như thế.</p>
      <p>Và đó là lý do mình yêu biển. Vì khi ra ngoài đó, bạn không còn là "người quản lý" hay "sinh viên" hay "bà mẹ bận rộn" nữa. Bạn chỉ là một người — đang học cách giữ thăng bằng.</p>
      <p style="font-style:italic">Cả nghĩa đen lẫn nghĩa bóng.</p>
      <p>Mình quan sát điều này ở hầu hết học viên. Người lo lắng nhất trước khi xuống nước, thường là người cười nhiều nhất sau buổi học. Vì họ vừa chứng minh cho chính mình thấy: mình làm được.</p>
      <p>Không có gì thay thế được khoảnh khắc đó.</p>
      <p>Đó là thứ Thuỷ Tộc muốn trao cho bạn — không phải kỹ năng, mà là cái cảm giác đó.</p>
      <p style="margin-top:32px">Hẹn gặp ở bước tiếp theo,<br><strong>Thuỷ Tộc 🌊</strong></p>
    </div>'''
    return subject, html


def make_email_3(name):
    subject = 'Một chỗ còn trống — dành cho bạn nếu muốn'
    html = f'''
    <div style="font-family:Georgia,serif;max-width:580px;margin:0 auto;color:#1a1a1a;line-height:1.8">
      <p>Chào {name},</p>
      <p>Mình không giỏi bán hàng. Nhưng mình rất thật.</p>
      <p>Và thật lòng mà nói — khoá <strong>SUP & Foil tại Phú Quốc</strong> của Thuỷ Tộc đang có chỗ trống. Không nhiều.</p>
      <p>Đây là khoá mình tự hướng dẫn. 1 kèm 1 hoàn toàn. Ở ngay mặt nước Phú Quốc — nơi sóng êm, nắng vừa phải, và bạn có thể học mà không sợ gì cả.</p>
      <p>💰 <strong>Giá: 2.000đ</strong> <span style="color:#888;font-size:0.9em">(ưu đãi lần đầu — trải nghiệm trước khi quyết định)</span></p>
      <p>Mình không muốn bạn chi nhiều tiền vào thứ chưa biết mình có thích không. Nên mình làm giá này.</p>
      <p style="margin:28px 0">
        <a href="https://thuytoc.com/thanh-toan.html" style="background:#0096ff;color:#fff;padding:14px 28px;border-radius:8px;text-decoration:none;font-weight:bold;font-family:sans-serif">
          👉 Giữ chỗ ngay
        </a>
      </p>
      <p>Nếu chưa sẵn sàng — không sao. Mình vẫn ở đây khi bạn cần.</p>
      <p style="margin-top:32px">Hẹn gặp ngoài biển,<br><strong>Thuỷ Tộc 🌊</strong></p>
    </div>'''
    return subject, html


def schedule_email_sequence(to_email, name, test_mode=False):
    """Gửi 3 email theo lịch. test_mode=True → gửi cả 3 ngay lập tức."""
    def run():
        # Email 1 — gửi ngay
        s1, h1 = make_email_1(name)
        send_email(to_email, s1, h1)

        if test_mode:
            # Chế độ test: gửi cả 3 ngay (delay 3 giây giữa mỗi cái)
            time.sleep(3)
            s2, h2 = make_email_2(name)
            send_email(to_email, s2, h2)
            time.sleep(3)
            s3, h3 = make_email_3(name)
            send_email(to_email, s3, h3)
            print(f'[EMAIL] 🧪 Test mode: đã gửi cả 3 email đến {to_email}')
        else:
            # Email 2 — sau 2 ngày (172800 giây)
            time.sleep(172800)
            s2, h2 = make_email_2(name)
            send_email(to_email, s2, h2)
            # Email 3 — sau thêm 1 ngày (86400 giây)
            time.sleep(86400)
            s3, h3 = make_email_3(name)
            send_email(to_email, s3, h3)

    t = threading.Thread(target=run, daemon=True)
    t.start()


def send_order_confirmation(to_email, name, product_name, amount):
    """Gửi email xác nhận đơn hàng"""
    amount_fmt = f"{int(amount):,} đ".replace(',', '.')
    subject = '✅ Đặt chỗ thành công — mình đã nhận được rồi'
    html = f'''
    <div style="font-family:Georgia,serif;max-width:580px;margin:0 auto;color:#1a1a1a;line-height:1.8">
      <p>Chào {name},</p>
      <p>Mình xác nhận bạn đã giữ chỗ thành công. 🎉</p>
      <div style="background:#f0f9ff;border-left:4px solid #0096ff;padding:16px 20px;border-radius:8px;margin:20px 0">
        <p style="margin:0"><strong>Chi tiết đơn hàng:</strong></p>
        <p style="margin:8px 0 0">• Khoá học: <strong>{product_name}</strong></p>
        <p style="margin:4px 0 0">• Số tiền: <strong>{amount_fmt}</strong></p>
      </div>
      <p><strong>Bước tiếp theo:</strong><br>Mình sẽ liên hệ trong vòng 24 giờ để xác nhận lịch và địa điểm cụ thể.</p>
      <p>Trong lúc chờ — nếu có câu hỏi gì, cứ reply thẳng vào email này. Mình đọc và trả lời từng cái.</p>
      <p>Cảm ơn vì đã tin tưởng Thuỷ Tộc. 🙏</p>
      <p style="margin-top:32px">Hẹn gặp ngoài biển,<br><strong>Thuỷ Tộc 🌊</strong></p>
    </div>'''
    threading.Thread(target=send_email, args=(to_email, subject, html), daemon=True).start()

PORT = int(os.environ.get('PORT', 8000))
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get('DB_PATH', os.path.join(DIRECTORY, 'brain.db'))


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        description TEXT,
        quantity INTEGER DEFAULT 0,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        zalo TEXT,
        email TEXT,
        registered_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
    # Migration: thêm cột email nếu chưa có (cho DB cũ)
    try:
        c.execute('ALTER TABLE customers ADD COLUMN email TEXT')
    except Exception:
        pass  # Cột đã tồn tại
    c.execute('''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER,
        product_id INTEGER,
        amount REAL,
        status TEXT DEFAULT 'pending',
        ref_code TEXT,
        ordered_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(customer_id) REFERENCES customers(id),
        FOREIGN KEY(product_id) REFERENCES products(id)
    )''')
    conn.commit()
    conn.close()


class AdminHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False, default=str).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', len(body))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.end_headers()
        self.wfile.write(body)

    def read_body(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length).decode('utf-8')
        try:
            return json.loads(raw)
        except Exception:
            return dict(urllib.parse.parse_qsl(raw))

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        p = self.path.split('?')[0]
        if p == '/admin':
            self.serve_file('admin.html')
        elif p == '/api/products':
            self.api_list('products')
        elif p == '/api/customers':
            self.api_list('customers')
        elif p == '/api/orders':
            self.api_orders_list()
        elif re.match(r'/api/orders/\d+/status', p):
            order_id = int(p.split('/')[3])
            self.api_order_status(order_id)
        else:
            super().do_GET()

    def do_POST(self):
        p = self.path
        if p == '/submit':
            self.handle_waitlist()
        elif p == '/api/products':
            self.api_create('products', ['name', 'price', 'description', 'quantity'])
        elif p == '/api/customers':
            self.api_create('customers', ['name', 'phone', 'zalo', 'email'])
        elif p == '/api/orders':
            self.api_create_order()
        elif p == '/api/checkout':
            self.api_checkout()
        elif p == '/api/sepay-webhook':
            self.api_sepay_webhook()
        elif re.match(r'/api/test-webhook/(\d+)', p):
            order_id = int(p.split('/')[-1])
            self.api_test_webhook(order_id)
        else:
            self.send_json({'error': 'Not found'}, 404)

    def do_PUT(self):
        m = re.match(r'/api/(products|customers|orders)/(\d+)', self.path)
        if m:
            self.api_update(m.group(1), int(m.group(2)))
        else:
            self.send_json({'error': 'Not found'}, 404)

    def do_DELETE(self):
        m = re.match(r'/api/(products|customers|orders)/(\d+)', self.path)
        if m:
            self.api_delete(m.group(1), int(m.group(2)))
        else:
            self.send_json({'error': 'Not found'}, 404)

    # ── Serve HTML files ─────────────────────────────────────────────
    def serve_file(self, filename):
        path = os.path.join(DIRECTORY, filename)
        with open(path, 'rb') as f:
            content = f.read()
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', len(content))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(content)

    # ── CHECKOUT: tạo đơn pending + tạo/tìm khách hàng ─────────────
    def api_checkout(self):
        data = self.read_body()
        name     = data.get('name', '').strip()
        phone    = data.get('phone', '').strip()
        product_id = data.get('product_id')
        amount   = data.get('amount')
        ref_code = data.get('ref_code', '')

        if not name:
            self.send_json({'error': 'Thiếu thông tin'}, 400)
            return

        conn = get_db()
        # Tìm hoặc tạo khách hàng
        row = conn.execute('SELECT id FROM customers WHERE phone=?', (phone,)).fetchone()
        if row:
            customer_id = row['id']
        else:
            cur = conn.execute(
                'INSERT INTO customers (name, phone) VALUES (?,?)', (name, phone)
            )
            customer_id = cur.lastrowid

        # Tạo đơn hàng pending
        cur = conn.execute(
            'INSERT INTO orders (customer_id, product_id, amount, status, ref_code) VALUES (?,?,?,?,?)',
            (customer_id, product_id, amount, 'pending', ref_code)
        )
        order_id = cur.lastrowid

        # Trừ tồn kho
        conn.execute('UPDATE products SET quantity = MAX(0, quantity-1) WHERE id=?', (product_id,))
        conn.commit()
        conn.close()

        self.send_json({'ok': True, 'order_id': order_id, 'customer_id': customer_id})

    # ── POLL STATUS: frontend hỏi đơn hàng đã paid chưa ────────────
    def api_order_status(self, order_id):
        conn = get_db()
        row = conn.execute('SELECT status FROM orders WHERE id=?', (order_id,)).fetchone()
        conn.close()
        if row:
            self.send_json({'status': row['status']})
        else:
            self.send_json({'error': 'Không tìm thấy đơn'}, 404)

    # ── SEPAY WEBHOOK: Sepay gọi vào đây khi nhận được tiền ─────────
    def api_sepay_webhook(self):
        data = self.read_body()
        print(f"\n[WEBHOOK] {datetime.now().strftime('%H:%M:%S')} - Nhận từ Sepay:")
        print(json.dumps(data, indent=2, ensure_ascii=False))

        # Sepay có thể gửi các field khác nhau tùy version
        # Thử lấy content từ nhiều field có thể có
        content = (
            str(data.get('content', '') or '') or
            str(data.get('description', '') or '') or
            str(data.get('transaction_content', '') or '') or
            str(data.get('memo', '') or '')
        ).strip()
        amount  = data.get('transferAmount') or data.get('amount', 0)

        print(f"[WEBHOOK] 📝 Content nhận được: '{content}'")
        print(f"[WEBHOOK] 💰 Số tiền: {amount}")

        conn = get_db()
        # Tìm tất cả đơn hàng pending
        rows = conn.execute(
            "SELECT id, ref_code FROM orders WHERE status='pending'"
        ).fetchall()

        print(f"[WEBHOOK] 🔍 Đang kiểm tra {len(rows)} đơn hàng pending...")

        matched = None
        # Clean content for easier matching: uppercase and remove spaces/special chars
        clean_content = content.upper().replace(" ", "").replace("-", "").replace("_", "")
        
        for row in rows:
            if row['ref_code']:
                clean_ref = row['ref_code'].upper().replace(" ", "").replace("-", "").replace("_", "")
                print(f"[WEBHOOK]   → So sánh ref='{clean_ref}' với content='{clean_content[:40]}...'")
                if clean_ref in clean_content:
                    matched = row['id']
                    print(f"[WEBHOOK] ✅ Khớp! Đơn #{matched} với ref='{row['ref_code']}'")
                    break

        if matched:
            conn.execute("UPDATE orders SET status='paid' WHERE id=?", (matched,))
            conn.commit()
            print(f"[WEBHOOK] ✅ Đơn #{matched} đã được cập nhật sang PAID")

            # Gửi email xác nhận nếu khách có email
            try:
                order_row = conn.execute(
                    '''SELECT o.amount, o.product_id, c.name, c.email
                       FROM orders o LEFT JOIN customers c ON c.id=o.customer_id
                       WHERE o.id=?''', (matched,)
                ).fetchone()
                if order_row and order_row['email']:
                    prod = conn.execute(
                        'SELECT name FROM products WHERE id=?', (order_row['product_id'],)
                    ).fetchone() if order_row['product_id'] else None
                    send_order_confirmation(
                        order_row['email'],
                        order_row['name'],
                        prod['name'] if prod else 'Khoá học Thuỷ Tộc',
                        order_row['amount']
                    )
            except Exception as e:
                print(f"[WEBHOOK] ⚠️ Lỗi gửi email xác nhận: {e}")
        else:
            print(f"[WEBHOOK] ⚠️  Không khớp ref_code nào!")
            print(f"[WEBHOOK]    Content gốc  : '{content}'")
            print(f"[WEBHOOK]    Content clean: '{clean_content}'")
            all_refs = [r['ref_code'] for r in rows if r['ref_code']]
            print(f"[WEBHOOK]    Các ref đang chờ: {all_refs}")

        conn.close()
        self.send_json({'success': True})

    # ── TEST WEBHOOK: Dùng để test thủ công (POST /api/test-webhook) ─
    def api_test_webhook(self, order_id):
        """Đánh dấu đơn hàng là paid để test frontend"""
        conn = get_db()
        row = conn.execute('SELECT id, ref_code, status FROM orders WHERE id=?', (order_id,)).fetchone()
        if not row:
            conn.close()
            self.send_json({'error': f'Không tìm thấy đơn #{order_id}'}, 404)
            return
        conn.execute("UPDATE orders SET status='paid' WHERE id=?", (order_id,))
        conn.commit()
        conn.close()
        print(f"[TEST] ✅ Đã force-paid đơn #{order_id} (test mode)")
        self.send_json({'ok': True, 'message': f'Đơn #{order_id} đã được đánh paid (test)'})

    # ── GENERIC CRUD ─────────────────────────────────────────────────
    def api_list(self, table):
        conn = get_db()
        rows = conn.execute(f'SELECT * FROM {table} ORDER BY id DESC').fetchall()
        conn.close()
        self.send_json([dict(r) for r in rows])

    def api_orders_list(self):
        conn = get_db()
        rows = conn.execute('''
            SELECT o.id, o.amount, o.status, o.ref_code, o.ordered_at,
                   c.name AS customer_name, c.phone AS customer_phone,
                   p.name AS product_name
            FROM orders o
            LEFT JOIN customers c ON c.id = o.customer_id
            LEFT JOIN products p ON p.id = o.product_id
            ORDER BY o.id DESC
        ''').fetchall()
        conn.close()
        self.send_json([dict(r) for r in rows])

    def api_create(self, table, fields):
        data = self.read_body()
        conn = get_db()
        cols = [f for f in fields if f in data]
        vals = [data[f] for f in cols]
        conn.execute(
            f'INSERT INTO {table} ({",".join(cols)}) VALUES ({",".join(["?"]*len(cols))})',
            vals
        )
        conn.commit()
        conn.close()
        self.send_json({'ok': True})

    def api_create_order(self):
        data = self.read_body()
        conn = get_db()
        pid = data.get('product_id')
        customer_id = data.get('customer_id')
        amount = data.get('amount', 0)
        if pid:
            conn.execute('UPDATE products SET quantity = MAX(0, quantity-1) WHERE id=?', (pid,))
        conn.execute(
            'INSERT INTO orders (customer_id, product_id, amount, status, ref_code) VALUES (?,?,?,?,?)',
            (customer_id, pid, amount, data.get('status', 'pending'), data.get('ref_code', ''))
        )

        # Gửi email xác nhận đơn hàng nếu khách có email
        if customer_id and amount:
            cust = conn.execute(
                'SELECT name, email FROM customers WHERE id=?', (customer_id,)
            ).fetchone()
            prod = conn.execute(
                'SELECT name FROM products WHERE id=?', (pid,)
            ).fetchone() if pid else None
            if cust and cust['email']:
                send_order_confirmation(
                    cust['email'],
                    cust['name'],
                    prod['name'] if prod else 'Khoá học Thuỷ Tộc',
                    amount
                )

        conn.commit()
        conn.close()
        self.send_json({'ok': True})

    def api_update(self, table, row_id):
        data = self.read_body()
        conn = get_db()
        sets = ', '.join([f'{k}=?' for k in data])
        vals = list(data.values()) + [row_id]
        conn.execute(f'UPDATE {table} SET {sets} WHERE id=?', vals)
        conn.commit()
        conn.close()
        self.send_json({'ok': True})

    def api_delete(self, table, row_id):
        conn = get_db()
        conn.execute(f'DELETE FROM {table} WHERE id=?', (row_id,))
        conn.commit()
        conn.close()
        self.send_json({'ok': True})

    def handle_waitlist(self):
        length = int(self.headers.get('Content-Length', 0))
        raw = self.rfile.read(length)
        data = {k: v[0] for k, v in urllib.parse.parse_qs(raw.decode()).items()}
        data['timestamp'] = datetime.now().isoformat()

        # Lưu vào waitlist.json (giữ nguyên)
        wf = os.path.join(DIRECTORY, 'waitlist.json')
        try:
            with open(wf, 'r', encoding='utf-8') as f:
                lst = json.load(f)
        except Exception:
            lst = []
        lst.append(data)
        with open(wf, 'w', encoding='utf-8') as f:
            json.dump(lst, f, ensure_ascii=False, indent=4)

        # Lưu vào bảng customers trong brain.db
        name  = data.get('name', '').strip()
        phone = data.get('phone', '').strip()
        email = data.get('email', '').strip()
        if name:
            conn = get_db()
            existing = None
            if phone:
                existing = conn.execute(
                    'SELECT id FROM customers WHERE phone=?', (phone,)
                ).fetchone()
            if not existing and email:
                existing = conn.execute(
                    'SELECT id FROM customers WHERE email=?', (email,)
                ).fetchone()
            if existing:
                conn.execute(
                    'UPDATE customers SET email=? WHERE id=? AND (email IS NULL OR email="")',
                    (email, existing['id'])
                )
            else:
                conn.execute(
                    'INSERT INTO customers (name, phone, email) VALUES (?,?,?)',
                    (name, phone, email)
                )
            conn.commit()
            conn.close()
            print(f'[WAITLIST] ✅ Khách mới: {name} | {phone} | {email}')

        # Gửi email sequence nếu có email
        if email and name:
            # Chế độ test: email chứa '+test' → gửi cả 3 ngay lập tức
            is_test = '+test' in email.lower()
            if is_test:
                print(f'[EMAIL] 🧪 Chế độ TEST — gửi cả 3 email ngay đến {email}')
            schedule_email_sequence(email, name, test_mode=is_test)

        self.send_json({'status': 'success'})

    def log_message(self, fmt, *args):
        pass


if __name__ == '__main__':
    init_db()
    print(f'✅ Server chạy tại http://localhost:{PORT}')
    print(f'🔧 Admin panel : http://localhost:{PORT}/admin')
    print(f'🪝 Webhook URL : http://localhost:{PORT}/api/sepay-webhook')
    with socketserver.TCPServer(('', PORT), AdminHandler) as httpd:
        httpd.allow_reuse_address = True
        httpd.serve_forever()
