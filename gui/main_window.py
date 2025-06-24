#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学影像分析系统主界面
Medical Image Analysis System Main Window
"""

import sys
import os
import logging
from typing import Optional
import numpy as np

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTextEdit, QProgressBar, QTabWidget,
    QFileDialog, QMessageBox, QGroupBox, QScrollArea,
    QSplitter, QFrame, QStatusBar, QMenuBar,
    QToolBar, QComboBox, QSpinBox, QSlider, QCheckBox
)
from PySide6.QtGui import QAction
from PySide6.QtCore import Qt, QThread, QSignal, QTimer, QSize
from PySide6.QtGui import QPixmap, QImage, QPainter, QPen, QColor, QFont, QIcon

# 导入核心模块
try:
    from core.image_processor import MedicalImageProcessor
    from models.ct_analyzer import CTAnalyzer
    from utils.report_generator import PDFReportGenerator
except ImportError:
    # 如果模块不存在，创建占位符类
    class MedicalImageProcessor:
        def __init__(self): pass
    class CTAnalyzer:
        def __init__(self): pass
    class PDFReportGenerator:
        def __init__(self): pass

logger = logging.getLogger(__name__)

class AnalysisWorker(QThread):
    """分析工作线程"""
    progress = QSignal(int)
    result = QSignal(dict)
    error = QSignal(str)
    
    def __init__(self, image_processor, ct_analyzer, image_data):
        super().__init__()
        self.image_processor = image_processor
        self.ct_analyzer = ct_analyzer
        self.image_data = image_data
    
    def run(self):
        try:
            self.progress.emit(20)
            
            # 预处理图像
            processed_image = self.image_processor.preprocess_for_analysis()
            self.progress.emit(40)
            
            # AI分析
            result = self.ct_analyzer.comprehensive_analysis(processed_image)
            self.progress.emit(80)
            
            # 完成
            self.progress.emit(100)
            self.result.emit(result)
            
        except Exception as e:
            self.error.emit(str(e))

class ImageDisplayWidget(QLabel):
    """图像显示组件"""
    
    def __init__(self):
        super().__init__()
        self.setMinimumSize(400, 400)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #bdc3c7;
                background-color: #ecf0f1;
                color: #7f8c8d;
                font-size: 14px;
            }
        """)
        self.setAlignment(Qt.AlignCenter)
        self.setText("请选择CT影像文件\n支持格式: DICOM, NIfTI, PNG, JPG")
        self.setScaledContents(True)
        
    def set_image(self, image_array: np.ndarray):
        """设置显示图像"""
        try:
            if len(image_array.shape) == 3:
                # 如果是3D图像，显示中间切片
                slice_idx = image_array.shape[2] // 2
                image_2d = image_array[:, :, slice_idx]
            else:
                image_2d = image_array
            
            # 归一化到0-255
            normalized = ((image_2d - image_2d.min()) / 
                         (image_2d.max() - image_2d.min()) * 255).astype(np.uint8)
            
            # 转换为QImage
            height, width = normalized.shape
            q_image = QImage(normalized.data, width, height, width, QImage.Format_Grayscale8)
            
            # 转换为QPixmap并显示
            pixmap = QPixmap.fromImage(q_image)
            self.setPixmap(pixmap)
            
        except Exception as e:
            logger.error(f"图像显示失败: {str(e)}")

class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("医学影像CT分析系统 v2.1.3.20250321_alpha")
        self.setGeometry(100, 100, 1400, 900)
        
        # 初始化组件
        self.image_processor = MedicalImageProcessor()
        self.ct_analyzer = CTAnalyzer()
        self.report_generator = PDFReportGenerator()
        
        # 状态变量
        self.current_image_path = None
        self.current_analysis_result = None
        self.analysis_worker = None
        
        # 设置界面
        self.setup_ui()
        self.setup_menu()
        self.setup_toolbar()
        self.setup_status_bar()
        
        logger.info("主界面初始化完成")
    
    def setup_ui(self):
        """设置用户界面"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # 左侧面板 - 图像显示和控制
        left_panel = self.create_left_panel()
        splitter.addWidget(left_panel)
        
        # 右侧面板 - 分析结果
        right_panel = self.create_right_panel()
        splitter.addWidget(right_panel)
        
        # 设置分割器比例
        splitter.setSizes([600, 800])
    
    def create_left_panel(self) -> QWidget:
        """创建左侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 图像显示组
        image_group = QGroupBox("CT影像显示")
        image_layout = QVBoxLayout(image_group)
        
        self.image_display = ImageDisplayWidget()
        image_layout.addWidget(self.image_display)
        
        # 图像控制
        controls_layout = QHBoxLayout()
        
        self.load_btn = QPushButton("加载影像")
        self.load_btn.setIcon(QIcon())
        self.load_btn.clicked.connect(self.load_image)
        
        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.setIcon(QIcon())
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)
        
        controls_layout.addWidget(self.load_btn)
        controls_layout.addWidget(self.analyze_btn)
        controls_layout.addStretch()
        
        image_layout.addLayout(controls_layout)
        layout.addWidget(image_group)
        
        # 图像信息组
        info_group = QGroupBox("影像信息")
        info_layout = QVBoxLayout(info_group)
        
        self.image_info_text = QTextEdit()
        self.image_info_text.setMaximumHeight(150)
        self.image_info_text.setReadOnly(True)
        info_layout.addWidget(self.image_info_text)
        
        layout.addWidget(info_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        return panel
    
    def create_right_panel(self) -> QWidget:
        """创建右侧面板"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        # 分析结果选项卡
        self.result_tabs = QTabWidget()
        
        # 分类结果
        self.classification_tab = self.create_classification_tab()
        self.result_tabs.addTab(self.classification_tab, "分类分析")
        
        # 分割结果
        self.segmentation_tab = self.create_segmentation_tab()
        self.result_tabs.addTab(self.segmentation_tab, "区域分割")
        
        # 热力图
        self.heatmap_tab = self.create_heatmap_tab()
        self.result_tabs.addTab(self.heatmap_tab, "热力图")
        
        # 综合报告
        self.report_tab = self.create_report_tab()
        self.result_tabs.addTab(self.report_tab, "综合报告")
        
        layout.addWidget(self.result_tabs)
        
        # 操作按钮
        button_layout = QHBoxLayout()
        
        self.save_result_btn = QPushButton("保存结果")
        self.save_result_btn.clicked.connect(self.save_results)
        self.save_result_btn.setEnabled(False)
        
        self.generate_report_btn = QPushButton("生成PDF报告")
        self.generate_report_btn.clicked.connect(self.generate_pdf_report)
        self.generate_report_btn.setEnabled(False)
        
        self.clear_btn = QPushButton("清空结果")
        self.clear_btn.clicked.connect(self.clear_results)
        
        button_layout.addWidget(self.save_result_btn)
        button_layout.addWidget(self.generate_report_btn)
        button_layout.addWidget(self.clear_btn)
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        return panel
    
    def create_classification_tab(self) -> QWidget:
        """创建分类分析选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 结果显示
        self.classification_result = QTextEdit()
        self.classification_result.setReadOnly(True)
        layout.addWidget(self.classification_result)
        
        return widget
    
    def create_segmentation_tab(self) -> QWidget:
        """创建分割分析选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 分割图像显示
        self.segmentation_display = ImageDisplayWidget()
        self.segmentation_display.setText("分割结果将在此显示")
        layout.addWidget(self.segmentation_display)
        
        # 统计信息
        self.segmentation_stats = QTextEdit()
        self.segmentation_stats.setMaximumHeight(150)
        self.segmentation_stats.setReadOnly(True)
        layout.addWidget(self.segmentation_stats)
        
        return widget
    
    def create_heatmap_tab(self) -> QWidget:
        """创建热力图选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 热力图显示
        self.heatmap_display = ImageDisplayWidget()
        self.heatmap_display.setText("热力图将在此显示")
        layout.addWidget(self.heatmap_display)
        
        return widget
    
    def create_report_tab(self) -> QWidget:
        """创建综合报告选项卡"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 综合报告
        self.comprehensive_report = QTextEdit()
        self.comprehensive_report.setReadOnly(True)
        layout.addWidget(self.comprehensive_report)
        
        return widget
    
    def setup_menu(self):
        """设置菜单栏"""
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        
        open_action = QAction("打开影像", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.load_image)
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("退出", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # 分析菜单
        analysis_menu = menubar.addMenu("分析")
        
        start_analysis_action = QAction("开始分析", self)
        start_analysis_action.setShortcut("F5")
        start_analysis_action.triggered.connect(self.start_analysis)
        analysis_menu.addAction(start_analysis_action)
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """设置工具栏"""
        toolbar = QToolBar()
        self.addToolBar(toolbar)
        
        # 添加工具按钮
        toolbar.addAction("打开", self.load_image)
        toolbar.addAction("分析", self.start_analysis)
        toolbar.addSeparator()
        toolbar.addAction("保存", self.save_results)
        toolbar.addAction("报告", self.generate_pdf_report)
    
    def setup_status_bar(self):
        """设置状态栏"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪")
    
    def load_image(self):
        """加载影像文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择CT影像文件",
            "", "影像文件 (*.dcm *.dicom *.nii *.nii.gz *.png *.jpg *.jpeg)"
        )
        
        if file_path:
            try:
                self.status_bar.showMessage("正在加载影像...")
                
                # 加载图像
                image_data = self.image_processor.load_image(file_path)
                
                if image_data is not None:
                    self.current_image_path = file_path
                    self.image_display.set_image(image_data)
                    
                    # 显示图像信息
                    stats = self.image_processor.get_image_statistics()
                    metadata = self.image_processor.image_metadata
                    
                    info_text = f"文件路径: {file_path}\n"
                    info_text += f"图像尺寸: {stats.get('shape', 'N/A')}\n"
                    info_text += f"数据类型: {stats.get('dtype', 'N/A')}\n"
                    info_text += f"像素值范围: {stats.get('min_value', 0):.2f} - {stats.get('max_value', 0):.2f}\n"
                    
                    if 'PatientName' in metadata:
                        info_text += f"患者姓名: {metadata['PatientName']}\n"
                        info_text += f"检查日期: {metadata.get('StudyDate', 'N/A')}\n"
                        info_text += f"影像模态: {metadata.get('Modality', 'N/A')}\n"
                    
                    self.image_info_text.setText(info_text)
                    self.analyze_btn.setEnabled(True)
                    self.status_bar.showMessage("影像加载成功")
                    
                    logger.info(f"成功加载影像: {file_path}")
                else:
                    raise Exception("影像加载失败")
                    
            except Exception as e:
                QMessageBox.critical(self, "错误", f"加载影像失败:\n{str(e)}")
                self.status_bar.showMessage("影像加载失败")
                logger.error(f"加载影像失败: {str(e)}")
    
    def start_analysis(self):
        """开始分析"""
        if not self.current_image_path:
            QMessageBox.warning(self, "警告", "请先加载影像文件")
            return
        
        try:
            self.status_bar.showMessage("正在分析影像...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.analyze_btn.setEnabled(False)
            
            # 创建分析工作线程
            self.analysis_worker = AnalysisWorker(
                self.image_processor, 
                self.ct_analyzer, 
                self.image_processor.current_image
            )
            
            # 连接信号
            self.analysis_worker.progress.connect(self.progress_bar.setValue)
            self.analysis_worker.result.connect(self.on_analysis_complete)
            self.analysis_worker.error.connect(self.on_analysis_error)
            
            # 启动分析
            self.analysis_worker.start()
            
        except Exception as e:
            QMessageBox.critical(self, "错误", f"分析启动失败:\n{str(e)}")
            self.status_bar.showMessage("分析失败")
            self.analyze_btn.setEnabled(True)
            self.progress_bar.setVisible(False)
    
    def on_analysis_complete(self, result):
        """分析完成"""
        self.current_analysis_result = result
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.save_result_btn.setEnabled(True)
        self.generate_report_btn.setEnabled(True)
        
        try:
            # 显示分类结果
            if 'classification' in result:
                class_result = result['classification']
                class_text = f"分类结果: {class_result.get('prediction_label', 'N/A')}\n"
                class_text += f"置信度: {class_result.get('confidence', 0):.3f}\n\n"
                class_text += "各类别概率:\n"
                
                for label, prob in class_result.get('probabilities', {}).items():
                    class_text += f"{label}: {prob:.3f}\n"
                
                self.classification_result.setText(class_text)
            
            # 显示分割结果
            if 'segmentation' in result:
                seg_result = result['segmentation']
                if 'segmentation_mask' in seg_result:
                    self.segmentation_display.set_image(seg_result['segmentation_mask'])
                
                stats_text = "分割统计:\n"
                for region, info in seg_result.get('segment_statistics', {}).items():
                    stats_text += f"{region}: {info['percentage']:.1f}% ({info['pixel_count']} 像素)\n"
                
                self.segmentation_stats.setText(stats_text)
            
            # 显示热力图
            if 'heatmap' in result:
                heatmap = result['heatmap']
                if len(heatmap.shape) == 3:  # 彩色热力图
                    heatmap_gray = np.mean(heatmap, axis=2).astype(np.uint8)
                    self.heatmap_display.set_image(heatmap_gray)
            
            # 生成综合报告
            report_text = self.generate_comprehensive_report(result)
            self.comprehensive_report.setText(report_text)
            
            self.status_bar.showMessage("分析完成")
            logger.info("影像分析完成")
            
        except Exception as e:
            logger.error(f"结果显示失败: {str(e)}")
            QMessageBox.warning(self, "警告", f"结果显示出现问题:\n{str(e)}")
    
    def on_analysis_error(self, error_msg):
        """分析错误"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        QMessageBox.critical(self, "分析错误", f"分析过程中出现错误:\n{error_msg}")
        self.status_bar.showMessage("分析失败")
        logger.error(f"分析失败: {error_msg}")
    
    def generate_comprehensive_report(self, result) -> str:
        """生成综合报告文本"""
        report = "=== 医学影像CT分析报告 ===\n\n"
        
        if 'timestamp' in result:
            report += f"分析时间: {result['timestamp']}\n"
        
        if self.current_image_path:
            report += f"影像文件: {os.path.basename(self.current_image_path)}\n\n"
        
        # 分类结果
        if 'classification' in result:
            class_result = result['classification']
            report += "## 分类分析结果\n"
            report += f"诊断结果: {class_result.get('prediction_label', 'N/A')}\n"
            report += f"置信度: {class_result.get('confidence', 0):.1%}\n\n"
        
        # 风险评估
        if 'risk_assessment' in result:
            risk = result['risk_assessment']
            report += "## 风险评估\n"
            report += f"风险等级: {risk.get('risk_level', 'N/A')}\n"
            report += f"风险评分: {risk.get('risk_score', 0):.2f}\n"
            
            if risk.get('risk_factors'):
                report += "风险因素:\n"
                for factor in risk['risk_factors']:
                    report += f"- {factor}\n"
            
            report += f"\n建议: {risk.get('recommendation', 'N/A')}\n\n"
        
        # 技术信息
        if 'segmentation' in result:
            seg_result = result['segmentation']
            report += "## 技术细节\n"
            report += f"总像素数: {seg_result.get('total_pixels', 0):,}\n"
            
            if 'segment_statistics' in seg_result:
                report += "区域分析:\n"
                for region, info in seg_result['segment_statistics'].items():
                    report += f"- {region}: {info['percentage']:.1f}%\n"
        
        report += "\n注意: 此报告仅供参考，最终诊断请咨询专业医生。"
        
        return report
    
    def save_results(self):
        """保存分析结果"""
        if not self.current_analysis_result:
            QMessageBox.warning(self, "警告", "没有可保存的分析结果")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存分析结果", "", "JSON文件 (*.json)"
        )
        
        if file_path:
            try:
                import json
                with open(file_path, 'w', encoding='utf-8') as f:
                    # 处理numpy数组
                    save_data = {}
                    for key, value in self.current_analysis_result.items():
                        if isinstance(value, np.ndarray):
                            save_data[key] = value.tolist()
                        elif isinstance(value, dict):
                            save_data[key] = self._process_dict_for_json(value)
                        else:
                            save_data[key] = value
                    
                    json.dump(save_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(self, "成功", "分析结果已保存")
                logger.info(f"分析结果已保存到: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"保存失败:\n{str(e)}")
                logger.error(f"保存结果失败: {str(e)}")
    
    def _process_dict_for_json(self, data):
        """处理字典数据以便JSON序列化"""
        result = {}
        for key, value in data.items():
            if isinstance(value, np.ndarray):
                result[key] = value.tolist()
            elif isinstance(value, dict):
                result[key] = self._process_dict_for_json(value)
            elif isinstance(value, (np.integer, np.floating)):
                result[key] = float(value)
            else:
                result[key] = value
        return result
    
    def generate_pdf_report(self):
        """生成PDF报告"""
        if not self.current_analysis_result:
            QMessageBox.warning(self, "警告", "没有可生成报告的分析结果")
            return
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存PDF报告", "", "PDF文件 (*.pdf)"
        )
        
        if file_path:
            try:
                # 这里应该调用PDF报告生成器
                # self.report_generator.generate_report(self.current_analysis_result, file_path)
                
                # 临时解决方案：保存为文本文件
                report_text = self.generate_comprehensive_report(self.current_analysis_result)
                with open(file_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                    f.write(report_text)
                
                QMessageBox.information(self, "成功", "报告已生成（临时保存为文本格式）")
                logger.info(f"报告已生成: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(self, "错误", f"报告生成失败:\n{str(e)}")
                logger.error(f"PDF报告生成失败: {str(e)}")
    
    def clear_results(self):
        """清空结果"""
        self.classification_result.clear()
        self.segmentation_display.setText("分割结果将在此显示")
        self.segmentation_stats.clear()
        self.heatmap_display.setText("热力图将在此显示")
        self.comprehensive_report.clear()
        
        self.current_analysis_result = None
        self.save_result_btn.setEnabled(False)
        self.generate_report_btn.setEnabled(False)
        
        self.status_bar.showMessage("结果已清空")
    
    def show_about(self):
        """显示关于对话框"""
        QMessageBox.about(self, "关于", 
            "医学影像CT分析系统\n"
            "版本: 2.1.3.20250321_alpha\n\n"
            "基于MONAI和PySide6开发\n"
            "提供专业的医学影像分析功能\n\n"
            "技术支持: jntm20111013@outlook.com"
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        if self.analysis_worker and self.analysis_worker.isRunning():
            reply = QMessageBox.question(self, "确认", "分析正在进行中，确定要退出吗？")
            if reply == QMessageBox.Yes:
                self.analysis_worker.terminate()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept() 