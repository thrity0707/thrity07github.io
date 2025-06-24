#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志系统
Logging System
"""

import logging
import os
from datetime import datetime

def setup_logger(log_level=logging.INFO):
    """
    设置日志系统
    Setup logging system
    """
    # 确保日志目录存在
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # 日志文件名包含时间戳
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"medical_analysis_{timestamp}.log")
    
    # 配置日志格式
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 配置根日志器
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    # 创建专用的医学影像分析日志器
    logger = logging.getLogger('medical_analysis')
    logger.setLevel(log_level)
    
    return logger 