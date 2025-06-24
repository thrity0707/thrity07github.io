#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF报告生成器
PDF Report Generator
"""

import os
import logging
from datetime import datetime
from typing import Dict, Optional
import matplotlib.pyplot as plt
import matplotlib
import numpy as np

# 设置matplotlib后端
matplotlib.use('Agg')

try:
    from reportlab.lib.pagesizes import A4, letter
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.pdfgen import canvas
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
except ImportError:
    # 如果reportlab未安装，创建占位符
    A4_SIZE = (595.27, 841.89)
    SimpleDocTemplate = None

logger = logging.getLogger(__name__)

class PDFReportGenerator:
    """PDF报告生成器"""
    
    def __init__(self):
        """初始化报告生成器"""
        self.styles = None
        self.temp_images = []
        
        if SimpleDocTemplate:
            self.styles = getSampleStyleSheet()
            self._create_custom_styles()
    
    def _create_custom_styles(self):
        """创建自定义样式"""
        if not self.styles:
            return
            
        # 标题样式
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.darkblue
        )
        
        # 章节标题样式
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.darkblue
        )
        
        # 正文样式
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            leftIndent=0,
            rightIndent=0
        )
        
        # 重要信息样式
        self.important_style = ParagraphStyle(
            'Important',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.red,
            spaceAfter=6
        )
    
    def generate_report(self, analysis_result: Dict, output_path: str, 
                       patient_info: Optional[Dict] = None) -> bool:
        """
        生成PDF分析报告
        Generate PDF analysis report
        
        Args:
            analysis_result: 分析结果数据
            output_path: 输出文件路径
            patient_info: 患者信息（可选）
            
        Returns:
            生成是否成功
        """
        try:
            if not SimpleDocTemplate:
                logger.warning("ReportLab未安装，无法生成PDF报告")
                return self._generate_text_report(analysis_result, output_path, patient_info)
            
            # 创建PDF文档
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            
            # 添加标题
            story.append(Paragraph("医学影像CT分析报告", self.title_style))
            story.append(Spacer(1, 20))
            
            # 添加基本信息
            story.extend(self._create_basic_info_section(analysis_result, patient_info))
            
            # 添加分析结果
            story.extend(self._create_analysis_section(analysis_result))
            
            # 添加风险评估
            story.extend(self._create_risk_assessment_section(analysis_result))
            
            # 添加技术细节
            story.extend(self._create_technical_section(analysis_result))
            
            # 添加图像（如果有）
            story.extend(self._create_images_section(analysis_result))
            
            # 添加免责声明
            story.extend(self._create_disclaimer_section())
            
            # 生成PDF
            doc.build(story)
            
            # 清理临时文件
            self._cleanup_temp_files()
            
            logger.info(f"PDF报告生成成功: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"PDF报告生成失败: {str(e)}")
            # 尝试生成文本报告作为备选
            return self._generate_text_report(analysis_result, output_path, patient_info)
    
    def _create_basic_info_section(self, analysis_result: Dict, 
                                 patient_info: Optional[Dict] = None) -> list:
        """创建基本信息部分"""
        elements = []
        
        elements.append(Paragraph("基本信息", self.heading_style))
        
        # 患者信息表格
        data = []
        
        if patient_info:
            data.extend([
                ['患者姓名:', patient_info.get('name', 'N/A')],
                ['患者ID:', patient_info.get('id', 'N/A')],
                ['检查日期:', patient_info.get('study_date', 'N/A')],
                ['影像模态:', patient_info.get('modality', 'CT')]
            ])
        
        data.extend([
            ['分析时间:', analysis_result.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))],
            ['系统版本:', 'v2.1.3.20250321_alpha'],
            ['图像尺寸:', str(analysis_result.get('image_shape', 'N/A'))]
        ])
        
        table = Table(data, colWidths=[2*inch, 3*inch])
        table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 20))
        
        return elements
    
    def _create_analysis_section(self, analysis_result: Dict) -> list:
        """创建分析结果部分"""
        elements = []
        
        elements.append(Paragraph("分析结果", self.heading_style))
        
        # 分类结果
        if 'classification' in analysis_result:
            classification = analysis_result['classification']
            
            elements.append(Paragraph("分类分析:", self.body_style))
            
            result_text = f"诊断结果: <b>{classification.get('prediction_label', 'N/A')}</b><br/>"
            result_text += f"置信度: <b>{classification.get('confidence', 0):.1%}</b><br/>"
            
            elements.append(Paragraph(result_text, self.body_style))
            
            # 各类别概率
            if 'probabilities' in classification:
                prob_data = [['类别', '概率']]
                for label, prob in classification['probabilities'].items():
                    prob_data.append([label, f"{prob:.1%}"])
                
                prob_table = Table(prob_data, colWidths=[2*inch, 1.5*inch])
                prob_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                ]))
                
                elements.append(prob_table)
        
        elements.append(Spacer(1, 15))
        return elements
    
    def _create_risk_assessment_section(self, analysis_result: Dict) -> list:
        """创建风险评估部分"""
        elements = []
        
        if 'risk_assessment' not in analysis_result:
            return elements
        
        risk = analysis_result['risk_assessment']
        
        elements.append(Paragraph("风险评估", self.heading_style))
        
        # 风险等级
        risk_level = risk.get('risk_level', 'N/A')
        risk_score = risk.get('risk_score', 0)
        
        # 根据风险等级选择颜色
        risk_color = colors.green
        if risk_level == "高风险":
            risk_color = colors.red
        elif risk_level == "中风险":
            risk_color = colors.orange
        elif risk_level == "低风险":
            risk_color = colors.yellow
        
        risk_style = ParagraphStyle(
            'RiskLevel',
            parent=self.body_style,
            textColor=risk_color,
            fontSize=14,
            spaceAfter=10
        )
        
        elements.append(Paragraph(f"风险等级: <b>{risk_level}</b>", risk_style))
        elements.append(Paragraph(f"风险评分: {risk_score:.2f}", self.body_style))
        
        # 风险因素
        if 'risk_factors' in risk and risk['risk_factors']:
            elements.append(Paragraph("风险因素:", self.body_style))
            for factor in risk['risk_factors']:
                elements.append(Paragraph(f"• {factor}", self.body_style))
        
        # 建议
        if 'recommendation' in risk:
            elements.append(Paragraph("建议:", self.body_style))
            elements.append(Paragraph(risk['recommendation'], self.important_style))
        
        elements.append(Spacer(1, 15))
        return elements
    
    def _create_technical_section(self, analysis_result: Dict) -> list:
        """创建技术细节部分"""
        elements = []
        
        elements.append(Paragraph("技术细节", self.heading_style))
        
        # 分割统计
        if 'segmentation' in analysis_result:
            segmentation = analysis_result['segmentation']
            
            elements.append(Paragraph("区域分析:", self.body_style))
            
            if 'segment_statistics' in segmentation:
                seg_data = [['区域', '像素数', '占比']]
                
                for region, info in segmentation['segment_statistics'].items():
                    seg_data.append([
                        region,
                        f"{info['pixel_count']:,}",
                        f"{info['percentage']:.1f}%"
                    ])
                
                seg_table = Table(seg_data, colWidths=[2*inch, 1.5*inch, 1*inch])
                seg_table.setStyle(TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                ]))
                
                elements.append(seg_table)
        
        elements.append(Spacer(1, 15))
        return elements
    
    def _create_images_section(self, analysis_result: Dict) -> list:
        """创建图像部分"""
        elements = []
        
        # 如果有热力图，尝试保存并添加到报告中
        if 'heatmap' in analysis_result:
            try:
                heatmap_path = self._save_heatmap_image(analysis_result['heatmap'])
                if heatmap_path:
                    elements.append(Paragraph("热力图分析", self.heading_style))
                    img = Image(heatmap_path, width=4*inch, height=4*inch)
                    elements.append(img)
                    elements.append(Spacer(1, 15))
            except Exception as e:
                logger.warning(f"热力图添加失败: {str(e)}")
        
        return elements
    
    def _save_heatmap_image(self, heatmap_data) -> Optional[str]:
        """保存热力图为临时图像文件"""
        try:
            if isinstance(heatmap_data, np.ndarray):
                temp_path = f"temp_heatmap_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                
                plt.figure(figsize=(8, 8))
                plt.imshow(heatmap_data, cmap='jet')
                plt.axis('off')
                plt.title('AI Analysis Heatmap')
                plt.tight_layout()
                plt.savefig(temp_path, dpi=150, bbox_inches='tight')
                plt.close()
                
                self.temp_images.append(temp_path)
                return temp_path
        except Exception as e:
            logger.error(f"热力图保存失败: {str(e)}")
        
        return None
    
    def _create_disclaimer_section(self) -> list:
        """创建免责声明部分"""
        elements = []
        
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("免责声明", self.heading_style))
        
        disclaimer_text = """
        本报告由AI医学影像分析系统自动生成，仅供参考使用。
        任何医学诊断和治疗决策都应该基于专业医生的临床判断。
        本系统不能替代专业医疗建议、诊断或治疗。
        如有健康问题，请及时咨询合格的医疗专业人员。
        """
        
        disclaimer_style = ParagraphStyle(
            'Disclaimer',
            parent=self.body_style,
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        elements.append(Paragraph(disclaimer_text, disclaimer_style))
        
        return elements
    
    def _generate_text_report(self, analysis_result: Dict, output_path: str, 
                            patient_info: Optional[Dict] = None) -> bool:
        """生成文本格式报告（备选方案）"""
        try:
            report_text = "=== 医学影像CT分析报告 ===\n\n"
            
            # 基本信息
            if patient_info:
                report_text += f"患者姓名: {patient_info.get('name', 'N/A')}\n"
                report_text += f"患者ID: {patient_info.get('id', 'N/A')}\n"
                report_text += f"检查日期: {patient_info.get('study_date', 'N/A')}\n\n"
            
            report_text += f"分析时间: {analysis_result.get('timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))}\n"
            report_text += f"图像尺寸: {analysis_result.get('image_shape', 'N/A')}\n\n"
            
            # 分类结果
            if 'classification' in analysis_result:
                classification = analysis_result['classification']
                report_text += "## 分类分析结果\n"
                report_text += f"诊断结果: {classification.get('prediction_label', 'N/A')}\n"
                report_text += f"置信度: {classification.get('confidence', 0):.1%}\n\n"
            
            # 风险评估
            if 'risk_assessment' in analysis_result:
                risk = analysis_result['risk_assessment']
                report_text += "## 风险评估\n"
                report_text += f"风险等级: {risk.get('risk_level', 'N/A')}\n"
                report_text += f"风险评分: {risk.get('risk_score', 0):.2f}\n"
                
                if risk.get('risk_factors'):
                    report_text += "风险因素:\n"
                    for factor in risk['risk_factors']:
                        report_text += f"- {factor}\n"
                
                report_text += f"\n建议: {risk.get('recommendation', 'N/A')}\n\n"
            
            # 免责声明
            report_text += "\n注意: 此报告仅供参考，最终诊断请咨询专业医生。"
            
            # 保存为文本文件
            text_path = output_path.replace('.pdf', '.txt')
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            logger.info(f"文本报告生成成功: {text_path}")
            return True
            
        except Exception as e:
            logger.error(f"文本报告生成失败: {str(e)}")
            return False
    
    def _cleanup_temp_files(self):
        """清理临时文件"""
        for temp_file in self.temp_images:
            try:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {temp_file}, {str(e)}")
        
        self.temp_images.clear() 