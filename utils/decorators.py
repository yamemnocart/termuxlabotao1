#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import functools
import time
import logging
from typing import Callable, Any
from backend.logger import logger

def log_function_call(func: Callable) -> Callable:
    """Decorator ghi lại lời gọi hàm"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        logger.debug(f"🔵 Calling {func.__name__}()")
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start
            logger.debug(f"🟢 {func.__name__}() completed in {elapsed:.3f}s")
            return result
        except Exception as e:
            logger.error(f"🔴 {func.__name__}() failed: {e}")
            raise
    
    return wrapper

def error_handler(func: Callable) -> Callable:
    """Decorator xử lý lỗi toàn diện"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.error(f"ValueError in {func.__name__}: {e}")
            return None
        except KeyError as e:
            logger.error(f"KeyError in {func.__name__}: {e}")
            return None
        except Exception as e:
            logger.critical(f"Unhandled exception in {func.__name__}: {e}")
            return None
    
    return wrapper

def rate_limit(max_calls: int = 10, time_window: int = 60):
    """Decorator giới hạn tần suất gọi"""
    calls = []
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.time()
            calls[:] = [c for c in calls if c > now - time_window]
            
            if len(calls) >= max_calls:
                logger.warning(f"⚠️ Rate limit exceeded for {func.__name__}")
                return None
            
            calls.append(now)
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator

def timing(func: Callable) -> Callable:
    """Decorator đo thời gian thực thi"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        logger.debug(f"⏱️ {func.__name__}: {elapsed:.4f}s")
        return result
    
    return wrapper

def retry(max_attempts: int = 3, delay: float = 1.0):
    """Decorator tự động thử lại khi thất bại"""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"Retry {attempt}/{max_attempts} for {func.__name__}: {e}")
                    if attempt < max_attempts:
                        time.sleep(delay * attempt)
            raise last_exception
        
        return wrapper
    
    return decorator
