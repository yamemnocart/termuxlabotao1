#!/bin/bash

echo "🔥 CYCLOPS - Khởi chạy"
echo "======================="

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 chưa cài!"
    exit 1
fi

# Cài đặt requirements
echo "📦 Kiểm tra thư viện..."
pip3 install -r requirements.txt --quiet 2>/dev/null || pip install -r requirements.txt --quiet

# Chạy main
echo "🚀 Khởi động CYCLOPS..."
python3 main.py
