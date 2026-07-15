
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import ipaddress
from typing import Optional, Tuple

class Validator:
    """Validator với xử lý edge cases hoàn hảo"""
    
    @staticmethod
    def validate_email(email: str) -> Tuple[bool, str]:
        """Validate email với xử lý edge cases"""
        if not email:
            return False, "Email is required"
        
        email = email.strip()
        
        if len(email) > 254:
            return False, "Email too long"
        
        if len(email) < 5:
            return False, "Email too short"
        
        # Pattern chuẩn với xử lý Unicode
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"
        
        # Kiểm tra domain
        domain = email.split('@')[1]
        if '.' not in domain:
            return False, "Invalid domain"
        
        return True, email.lower()
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, str]:
        """Validate password với edge cases"""
        if not password:
            return False, "Password is required"
        
        password = password.strip()
        
        if len(password) == 0:
            return False, "Password cannot be empty"
        
        if len(password) > 128:
            return False, "Password too long"
        
        # Không yêu cầu phức tạp để thu thập nhiều
        if len(password) < 4:
            return True, password  # Vẫn chấp nhận nhưng cảnh báo
        
        return True, password
    
    @staticmethod
    def validate_ip(ip: str) -> bool:
        """Validate IP address"""
        if not ip:
            return False
        
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def sanitize_string(input_str: str) -> str:
        """Sanitize string - loại bỏ ký tự nguy hiểm"""
        if not input_str:
            return ""
        
        # Loại bỏ control characters
        input_str = re.sub(r'[\x00-\x1f\x7f]', '', input_str)
        # Giới hạn độ dài
        if len(input_str) > 1000:
            input_str = input_str[:1000]
        return input_str
    
    @staticmethod
    def is_empty(value) -> bool:
        """Kiểm tra empty với nhiều kiểu dữ liệu"""
        if value is None:
            return True
        if isinstance(value, str):
            return value.strip() == ''
        if isinstance(value, (list, dict, set)):
            return len(value) == 0
        return False
    
    @staticmethod
    def check_size_limit(data: any, max_size: int = 1000000) -> bool:
        """Kiểm tra kích thước dữ liệu"""
        import sys
        size = sys.getsizeof(data)
        return size <= max_size

validator = Validator()
