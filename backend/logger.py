#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
import colorama
from colorama import Fore, Back, Style

colorama.init(autoreset=True)

class CyclopsLogger:
    """Logger với màu sắc và chi tiết"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.MAGENTA,
        'SUCCESS': Fore.GREEN + Style.BRIGHT,
    }
    
    def __init__(self, name: str = "Cyclops", log_file: str = "logs/cyclops.log"):
        self.name = name
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Setup logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(logging.DEBUG)
        console.setFormatter(self._console_formatter())
        
        # File handler
        file_handler = logging.FileHandler(str(self.log_file), encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(self._file_formatter())
        
        self.logger.addHandler(console)
        self.logger.addHandler(file_handler)
    
    def _console_formatter(self):
        class ColoredFormatter(logging.Formatter):
            def format(self, record):
                levelname = record.levelname
                color = CyclopsLogger.COLORS.get(levelname, Fore.WHITE)
                record.levelname = f"{color}{levelname}{Style.RESET_ALL}"
                record.name = f"{Fore.BLUE}{record.name}{Style.RESET_ALL}"
                
                # Thêm icon cho level
                icons = {
                    'DEBUG': '🔍',
                    'INFO': 'ℹ️',
                    'WARNING': '⚠️',
                    'ERROR': '❌',
                    'CRITICAL': '💀',
                    'SUCCESS': '✅',
                }
                icon = icons.get(levelname, '')
                record.msg = f"{icon} {record.msg}"
                
                return super().format(record)
        
        return ColoredFormatter(
            '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def _file_formatter(self):
        return logging.Formatter(
            '[%(asctime)s] [%(levelname)s] %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def debug(self, msg): self.logger.debug(msg)
    def info(self, msg): self.logger.info(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
    def critical(self, msg): self.logger.critical(msg)
    def success(self, msg): self.logger.info(f"{Fore.GREEN}✅ {msg}{Style.RESET_ALL}")

# Singleton
logger = CyclopsLogger()
