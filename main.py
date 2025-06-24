#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学影像CT分析系统
Medical Image CT Analysis System

基于MONAI和PySide6的专业医学影像分析系统
Professional medical image analysis system based on MONAI and PySide6

版本: 2.1.3.20250321_alpha
作者: Medical Image Analysis Team
"""

import sys
import os
import logging
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from utils.logger import setup_logger

def main():
    """主函数"""
    # 设置日志
    setup_logger()
    logger = logging.getLogger(__name__)
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("医学影像CT分析系统")
    app.setApplicationVersion("2.1.3.20250321_alpha")
    
    # 设置应用图标和样式
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f0f0f0;
        }
        QMenuBar {
            background-color: #2c3e50;
            color: white;
            font-size: 12px;
            padding: 4px;
        }
        QMenuBar::item {
            padding: 8px 12px;
            border: none;
        }
        QMenuBar::item:selected {
            background-color: #34495e;
        }
        QStatusBar {
            background-color: #ecf0f1;
            border-top: 1px solid #bdc3c7;
        }
    """)
    
    try:
        # 创建主窗口
        window = MainWindow()
        window.show()
        
        logger.info("医学影像CT分析系统启动成功")
        
        # 运行应用
        sys.exit(app.exec())
        
    except Exception as e:
        logger.error(f"系统启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 