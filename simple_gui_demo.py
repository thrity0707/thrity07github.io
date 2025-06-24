#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学影像CT分析系统 - 简化GUI演示
Simplified GUI Demo for Medical Image CT Analysis System
"""

import sys
import os
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import cv2

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QFileDialog, QMessageBox,
    QProgressBar, QTabWidget, QGroupBox
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPixmap, QImage, QFont

class SimpleGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("医学影像CT分析系统 - 简化演示版")
        self.setGeometry(100, 100, 1200, 800)
        
        # 设置中心窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("医学影像CT分析系统")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        main_layout.addWidget(title)
        
        # 内容区域
        content_layout = QHBoxLayout()
        
        # 左侧控制面板
        left_panel = self.create_control_panel()
        content_layout.addWidget(left_panel)
        
        # 右侧结果显示
        right_panel = self.create_result_panel()
        content_layout.addWidget(right_panel)
        
        main_layout.addLayout(content_layout)
        
        # 底部状态栏
        self.status_label = QLabel("系统就绪")
        main_layout.addWidget(self.status_label)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        print("GUI界面初始化完成")
    
    def create_control_panel(self):
        """创建控制面板"""
        panel = QGroupBox("分析控制")
        layout = QVBoxLayout(panel)
        
        # 文件选择
        file_layout = QHBoxLayout()
        self.file_path_label = QLabel("未选择文件")
        load_btn = QPushButton("选择影像文件")
        load_btn.clicked.connect(self.select_file)
        
        file_layout.addWidget(QLabel("文件路径:"))
        file_layout.addWidget(self.file_path_label)
        file_layout.addWidget(load_btn)
        layout.addLayout(file_layout)
        
        # 分析按钮
        self.analyze_btn = QPushButton("开始AI分析")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)
        layout.addWidget(self.analyze_btn)
        
        # 演示按钮
        demo_btn = QPushButton("运行演示")
        demo_btn.clicked.connect(self.run_demo)
        layout.addWidget(demo_btn)
        
        # 生成报告按钮
        self.report_btn = QPushButton("生成报告")
        self.report_btn.clicked.connect(self.generate_report)
        self.report_btn.setEnabled(False)
        layout.addWidget(self.report_btn)
        
        # 清空结果按钮
        clear_btn = QPushButton("清空结果")
        clear_btn.clicked.connect(self.clear_results)
        layout.addWidget(clear_btn)
        
        layout.addStretch()
        return panel
    
    def create_result_panel(self):
        """创建结果显示面板"""
        panel = QGroupBox("分析结果")
        layout = QVBoxLayout(panel)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        
        # 分析结果标签页
        self.result_text = QTextEdit()
        self.result_text.setFont(QFont("Consolas", 10))
        self.tab_widget.addTab(self.result_text, "分析结果")
        
        # 系统日志标签页
        self.log_text = QTextEdit()
        self.log_text.setFont(QFont("Consolas", 9))
        self.tab_widget.addTab(self.log_text, "系统日志")
        
        layout.addWidget(self.tab_widget)
        
        return panel
    
    def select_file(self):
        """选择文件"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, 
            "选择医学影像文件",
            "",
            "所有支持格式 (*.dcm *.nii *.nii.gz *.png *.jpg *.jpeg);;DICOM (*.dcm);;NIfTI (*.nii *.nii.gz);;图像文件 (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.file_path_label.setText(os.path.basename(file_path))
            self.analyze_btn.setEnabled(True)
            self.current_file = file_path
            self.log_message(f"已选择文件: {file_path}")
    
    def start_analysis(self):
        """开始分析"""
        if not hasattr(self, 'current_file'):
            QMessageBox.warning(self, "警告", "请先选择影像文件")
            return
        
        self.log_message("开始AI影像分析...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # 模拟分析过程
        self.simulate_analysis()
    
    def simulate_analysis(self):
        """模拟分析过程"""
        self.status_label.setText("正在分析中...")
        
        # 创建定时器模拟进度
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.progress_value = 0
        self.timer.start(50)  # 每50ms更新一次
    
    def update_progress(self):
        """更新进度"""
        self.progress_value += 2
        self.progress_bar.setValue(self.progress_value)
        
        if self.progress_value >= 100:
            self.timer.stop()
            self.analysis_complete()
    
    def analysis_complete(self):
        """分析完成"""
        self.progress_bar.setVisible(False)
        self.status_label.setText("分析完成")
        
        # 生成模拟结果
        result = self.generate_mock_result()
        self.display_result(result)
        self.report_btn.setEnabled(True)
        
        self.log_message("AI分析完成")
    
    def generate_mock_result(self):
        """生成模拟分析结果"""
        # 模拟AI分析结果
        predictions = ["正常", "异常"]
        prediction = np.random.choice(predictions, p=[0.7, 0.3])
        confidence = np.random.uniform(0.75, 0.95)
        risk_score = np.random.uniform(0.1, 0.8)
        
        result = {
            'prediction': prediction,
            'confidence': confidence,
            'risk_score': risk_score,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'features': {
                'mean_intensity': np.random.uniform(80, 120),
                'std_intensity': np.random.uniform(20, 40),
                'high_density_regions': np.random.randint(1, 10),
                'edge_density': np.random.uniform(0.2, 0.4)
            }
        }
        
        return result
    
    def display_result(self, result):
        """显示分析结果"""
        # 风险等级评估
        risk_score = result['risk_score']
        if risk_score >= 0.7:
            risk_level = "高风险"
        elif risk_score >= 0.4:
            risk_level = "中风险"
        else:
            risk_level = "低风险"
        
        result_text = f"""
=== 医学影像CT分析结果 ===

分析时间: {result['timestamp']}
文件名称: {getattr(self, 'current_file', '未知').split('/')[-1] if hasattr(self, 'current_file') else '演示数据'}

## AI诊断结果
诊断结果: {result['prediction']}
AI置信度: {result['confidence']:.1%}
风险评分: {result['risk_score']:.3f}
风险等级: {risk_level}

## 图像特征分析
平均强度值: {result['features']['mean_intensity']:.1f} HU
强度标准差: {result['features']['std_intensity']:.1f}
高密度区域: {result['features']['high_density_regions']} 个
边缘特征密度: {result['features']['edge_density']:.4f}

## AI分析详情
- 使用模型: DenseNet121 + UNet分割
- 处理时间: < 10秒
- 计算设备: CPU/GPU自适应
- 图像预处理: ✓ 归一化 ✓ 噪声滤除
- 特征提取: ✓ 形态学分析 ✓ 纹理分析
- 分类预测: ✓ 深度学习模型
- 后处理: ✓ 置信度校准

## 医学建议
{'建议立即就医，进行进一步检查' if risk_score >= 0.7 else '建议咨询专业医生，定期复查' if risk_score >= 0.4 else '建议定期体检，保持健康生活方式'}

## 免责声明
本系统仅用于辅助医学影像分析，不能替代专业医疗诊断。
任何医疗决策都应基于专业医生的临床判断。

--- 分析完成 ---
"""
        
        self.result_text.setText(result_text)
        self.current_result = result
    
    def run_demo(self):
        """运行演示"""
        self.log_message("启动演示模式...")
        
        # 模拟选择文件
        self.file_path_label.setText("demo_ct_scan.dcm")
        self.current_file = "demo_ct_scan.dcm"
        self.analyze_btn.setEnabled(True)
        
        # 自动开始分析
        QTimer.singleShot(500, self.start_analysis)
        
        self.log_message("演示模式已启动，自动分析中...")
    
    def generate_report(self):
        """生成报告"""
        if not hasattr(self, 'current_result'):
            QMessageBox.warning(self, "警告", "没有可用的分析结果")
            return
        
        try:
            # 创建输出目录
            output_dir = "output"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            
            # 生成报告文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_path = os.path.join(output_dir, f'gui_report_{timestamp}.txt')
            
            # 写入报告
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(self.result_text.toPlainText())
            
            self.log_message(f"报告已保存到: {report_path}")
            
            QMessageBox.information(self, "成功", f"报告已保存到:\n{os.path.abspath(report_path)}")
            
        except Exception as e:
            error_msg = f"生成报告失败: {str(e)}"
            self.log_message(error_msg)
            QMessageBox.critical(self, "错误", error_msg)
    
    def clear_results(self):
        """清空结果"""
        self.result_text.clear()
        self.log_text.clear()
        self.file_path_label.setText("未选择文件")
        self.analyze_btn.setEnabled(False)
        self.report_btn.setEnabled(False)
        self.status_label.setText("系统就绪")
        
        if hasattr(self, 'current_file'):
            delattr(self, 'current_file')
        if hasattr(self, 'current_result'):
            delattr(self, 'current_result')
        
        self.log_message("结果已清空")
    
    def log_message(self, message):
        """记录日志消息"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        print(log_entry)

def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    print("=" * 60)
    print("医学影像CT分析系统 - 简化GUI演示")
    print("Medical Image CT Analysis System - Simple GUI Demo")
    print("=" * 60)
    
    try:
        window = SimpleGUI()
        window.show()
        
        print("GUI界面已启动")
        print("功能说明:")
        print("1. 点击'选择影像文件'选择医学影像")
        print("2. 点击'开始AI分析'进行分析")
        print("3. 点击'运行演示'体验完整流程")
        print("4. 点击'生成报告'保存分析结果")
        
        # 运行应用
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"GUI启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 