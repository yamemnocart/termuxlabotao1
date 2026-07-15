#!/bin/bash

# ====== CYCLOPS LAUNCHER ======
echo "🔥 CYCLOPS - Mắt thần báo thức"
echo "================================"

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 chưa cài đặt!"
    exit 1
fi

# Cài đặt requirements
echo "📦 Đang cài đặt thư viện..."
pip3 install -r requirements.txt --quiet

# Kiểm tra cloudflared
if ! command -v cloudflared &> /dev/null; then
    echo "⚠️ cloudflared chưa cài. Chạy lệnh sau để cài:"
    echo "curl -sSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared && chmod +x cloudflared && sudo mv cloudflared /usr/local/bin/"
    echo ""
    read -p "Đã cài cloudflared? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "⚠️ Server sẽ chạy localhost mà không có public link"
    fi
fi

# Chạy backend
echo "🚀 Khởi động Cyclops Server..."
cd backend
python3 app.py
