#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 CYCLOPS - RUN SCRIPT
Khởi chạy nhanh toàn bộ hệ thống
"""

import sys
import os
from pathlib import Path

# Thêm thư mục hiện tại vào path
sys.path.insert(0, str(Path(__file__).parent))

# Import và chạy main
from main import main

if __name__ == "__main__":
    main()
