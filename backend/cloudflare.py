#!/usr/bin/env python3
import subprocess
import time
import re
import threading
import logging

logger = logging.getLogger(__name__)

class CloudflareTunnel:
    """Tự động tạo tunnel công khai với cloudflared"""
    
    def __init__(self, port=5000):
        self.port = port
        self.public_url = None
        self.process = None
        self.running = False
        
    def start_tunnel(self):
        """Bắt đầu tunnel và lấy link public"""
        try:
            cmd = ['cloudflared', 'tunnel', '--url', f'http://localhost:{self.port}']
            self.process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            
            # Đọc output để lấy link
            for line in iter(self.process.stderr.readline, ''):
                if 'https://' in line:
                    match = re.search(r'https://[a-z0-9-]+\.trycloudflare\.com', line)
                    if match:
                        self.public_url = match.group()
                        logger.info(f"🌐 Link công khai: {self.public_url}")
                        return self.public_url
                if 'error' in line.lower():
                    logger.error(f"⚠️ Cloudflare lỗi: {line.strip()}")
                    
            return None
        except Exception as e:
            logger.error(f"❌ Tunnel thất bại: {e}")
            return None
    
    def stop_tunnel(self):
        """Dừng tunnel"""
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
            logger.info("🛑 Đã dừng tunnel")

# ====== SỬ DỤNG ======
if __name__ == '__main__':
    tunnel = CloudflareTunnel(5000)
    url = tunnel.start_tunnel()
    if url:
        print(f"✅ Link public: {url}")
        input("Nhấn Enter để dừng...")
        tunnel.stop_tunnel()
