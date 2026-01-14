"""
日志配置
"""

import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from ..config import config


def setup_logger(name: str = "idps", log_file: str = None) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        log_file: 日志文件路径，如果为None则使用配置中的路径

    Returns:
        配置好的日志记录器
    """
    logger = logging.getLogger(name)

    # 如果已经配置过，直接返回
    if logger.handlers:
        return logger

    # 设置日志级别
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    logger.setLevel(log_level)

    # 日志格式
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 文件处理器
    if log_file is None:
        log_file = config.LOG_FILE

    # 确保日志目录存在
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=log_file,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


# 创建默认日志记录器
default_logger = setup_logger()
