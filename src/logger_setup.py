"""
logger_setup.py - Настройка логирования
"""

import logging
import os
import traceback


def setup_logger():
    """Настройка логгера с записью в файл и консоль"""
    
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logger = logging.getLogger('school')
    logger.setLevel(logging.DEBUG)
    
    if logger.hasHandlers():
        logger.handlers.clear()
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler = logging.FileHandler(f"{log_dir}/school.log", encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    error_handler = logging.FileHandler(f"{log_dir}/errors.log", encoding='utf-8')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    return logger


logger = setup_logger()


def log_user_action(action: str, user: str = None, details: str = None):
    """Логирование действий пользователя"""
    msg = f"Действие: {action}"
    if user:
        msg += f" | Пользователь: {user}"
    if details:
        msg += f" | {details}"
    logger.info(msg)


def log_error(error: Exception, context: str = None):
    """Логирование ошибок с контекстом"""
    msg = f"ОШИБКА: {type(error).__name__}: {error}"
    if context:
        msg = f"[{context}] {msg}"
    logger.error(msg)
    logger.debug(traceback.format_exc())
