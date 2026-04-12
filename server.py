import http.server
import socketserver
import json
import urllib.parse
import sqlite3
import re
from datetime import datetime
import os

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
        registered_at TEXT DEFAULT CURRENT_TIMESTAMP
    )''')
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
            self.api_create('customers', ['name', 'phone', 'zalo'])
        elif p == '/api/orders':
            self.api_create_order()
        elif p == '/api/checkout':
            self.api_checkout()
        elif p == '/api/sepay-webhook':
            self.api_sepay_webhook()
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

        # Sepay gửi: transferAmount, transferType, content (nội dung CK)
        content = str(data.get('content', '') or data.get('description', ''))
        amount  = data.get('transferAmount') or data.get('amount', 0)

        conn = get_db()
        # Tìm đơn hàng theo ref_code trong nội dung chuyển khoản
        rows = conn.execute(
            "SELECT id, ref_code FROM orders WHERE status='pending'"
        ).fetchall()

        matched = None
        # Clean content for easier matching: uppercase and remove spaces
        clean_content = content.upper().replace(" ", "")
        
        for row in rows:
            if row['ref_code']:
                clean_ref = row['ref_code'].upper().replace(" ", "")
                if clean_ref in clean_content:
                    matched = row['id']
                    break

        if matched:
            conn.execute("UPDATE orders SET status='paid' WHERE id=?", (matched,))
            conn.commit()
            print(f"[WEBHOOK] ✅ Đơn #{matched} đã được cập nhật sang PAID")
        else:
            print(f"[WEBHOOK] ⚠️  Không khớp ref_code nào. Content: {content}")

        conn.close()
        self.send_json({'success': True})

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
        if pid:
            conn.execute('UPDATE products SET quantity = MAX(0, quantity-1) WHERE id=?', (pid,))
        conn.execute(
            'INSERT INTO orders (customer_id, product_id, amount, status, ref_code) VALUES (?,?,?,?,?)',
            (data.get('customer_id'), pid, data.get('amount'),
             data.get('status', 'pending'), data.get('ref_code', ''))
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
        wf = os.path.join(DIRECTORY, 'waitlist.json')
        try:
            with open(wf, 'r', encoding='utf-8') as f:
                lst = json.load(f)
        except Exception:
            lst = []
        lst.append(data)
        with open(wf, 'w', encoding='utf-8') as f:
            json.dump(lst, f, ensure_ascii=False, indent=4)
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
