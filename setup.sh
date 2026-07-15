#!/bin/bash

echo "🔥 CYCLOPS - Cài đặt tự động"
echo "============================="

# Cập nhật hệ thống
echo "📦 Cập nhật packages..."
pkg update -y && pkg upgrade -y

# Cài đặt các gói cần thiết
echo "📦 Cài đặt Python và công cụ..."
pkg install python git python-pip openssl-tool -y

# Cài đặt cloudflared
echo "🌐 Cài đặt cloudflared..."
if ! command -
