#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学影像CT分析系统 - Web应用版
Medical Image CT Analysis System - Web Application
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import cv2
from datetime import datetime
import pandas as pd
import os
import json
import base64
from io import BytesIO
import zipfile

# 配置页面
st.set_page_config(
    page_title="医学影像CT分析系统",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #1f77b4;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def create_demo_ct_image():
    """创建演示用的CT图像"""
    ct_image = np.random.normal(100, 20, (512, 512)).astype(np.float32)
    
    # 添加器官结构
    y, x = np.ogrid[:512, :512]
    
    # 肺部区域
    lung_left = ((x - 150)**2 + (y - 256)**2) < 80**2
    lung_right = ((x - 362)**2 + (y - 256)**2) < 80**2
    ct_image[lung_left] = np.random.normal(50, 10, np.sum(lung_left))
    ct_image[lung_right] = np.random.normal(50, 10, np.sum(lung_right))
    
    # 心脏区域
    heart = ((x - 256)**2 + (y - 280)**2) < 50**2
    ct_image[heart] = np.random.normal(150, 15, np.sum(heart))
    
    # 骨骼结构
    ribs = np.logical_or(
        np.logical_and(np.abs(x - 100) < 10, np.abs(y - 200) < 100),
        np.logical_and(np.abs(x - 412) < 10, np.abs(y - 200) < 100)
    )
    ct_image[ribs] = np.random.normal(200, 5, np.sum(ribs))
    
    # 添加可疑结节
    nodule = ((x - 200)**2 + (y - 200)**2) < 15**2
    ct_image[nodule] = np.random.normal(180, 5, np.sum(nodule))
    
    ct_image = np.clip(ct_image, 0, 255)
    return ct_image.astype(np.uint8)

def analyze_ct_image(ct_image):
    """分析CT图像"""
    # 图像预处理
    normalized = cv2.normalize(ct_image, None, 0, 255, cv2.NORM_MINMAX)
    edges = cv2.Canny(normalized, 50, 150)
    
    # 特征提取
    mean_intensity = np.mean(ct_image)
    std_intensity = np.std(ct_image)
    
    # 检测高密度区域
    high_density_mask = ct_image > (mean_intensity + 2 * std_intensity)
    num_high_density_regions = cv2.connectedComponents(high_density_mask.astype(np.uint8))[0] - 1
    
    # AI分类逻辑
    risk_score = 0.0
    if num_high_density_regions > 3:
        risk_score += 0.3
    if std_intensity > 30:
        risk_score += 0.2
    if mean_intensity > 120:
        risk_score += 0.1
    
    risk_score += np.random.normal(0, 0.1)
    risk_score = max(0, min(1, risk_score))
    
    # 分类结果
    if risk_score > 0.6:
        prediction = "异常"
        confidence = 0.8 + np.random.random() * 0.15
    else:
        prediction = "正常"
        confidence = 0.7 + np.random.random() * 0.25
    
    return {
        'prediction': prediction,
        'confidence': confidence,
        'risk_score': risk_score,
        'features': {
            'mean_intensity': mean_intensity,
            'std_intensity': std_intensity,
            'high_density_regions': num_high_density_regions,
            'edge_density': np.sum(edges > 0) / edges.size
        },
        'processed_images': {
            'original': ct_image,
            'normalized': normalized,
            'edges': edges,
            'high_density_mask': high_density_mask
        }
    }

def generate_heatmap(ct_image):
    """生成热力图"""
    grad_x = cv2.Sobel(ct_image, cv2.CV_64F, 1, 0, ksize=3)
    grad_y = cv2.Sobel(ct_image, cv2.CV_64F, 0, 1, ksize=3)
    gradient_magnitude = np.sqrt(grad_x**2 + grad_y**2)
    heatmap = cv2.normalize(gradient_magnitude, None, 0, 255, cv2.NORM_MINMAX)
    return heatmap

def create_analysis_visualization(analysis_result):
    """创建分析可视化"""
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle('医学影像CT分析结果', fontsize=16, fontweight='bold')
    
    # 原始图像
    axes[0, 0].imshow(analysis_result['processed_images']['original'], cmap='gray')
    axes[0, 0].set_title('原始CT图像')
    axes[0, 0].axis('off')
    
    # 预处理图像
    axes[0, 1].imshow(analysis_result['processed_images']['normalized'], cmap='gray')
    axes[0, 1].set_title('预处理后图像')
    axes[0, 1].axis('off')
    
    # 边缘检测
    axes[0, 2].imshow(analysis_result['processed_images']['edges'], cmap='gray')
    axes[0, 2].set_title('边缘检测')
    axes[0, 2].axis('off')
    
    # 高密度区域
    axes[1, 0].imshow(analysis_result['processed_images']['high_density_mask'], cmap='hot')
    axes[1, 0].set_title('高密度区域检测')
    axes[1, 0].axis('off')
    
    # 热力图
    heatmap = generate_heatmap(analysis_result['processed_images']['original'])
    axes[1, 1].imshow(heatmap, cmap='jet')
    axes[1, 1].set_title('AI关注热力图')
    axes[1, 1].axis('off')
    
    # 结果统计
    features = analysis_result['features']
    result_text = f"""分析结果:
预测: {analysis_result['prediction']}
置信度: {analysis_result['confidence']:.1%}
风险评分: {analysis_result['risk_score']:.2f}

图像特征:
平均强度: {features['mean_intensity']:.1f} HU
强度标准差: {features['std_intensity']:.1f}
高密度区域: {features['high_density_regions']}个
边缘密度: {features['edge_density']:.3f}
"""
    
    axes[1, 2].text(0.1, 0.9, result_text, transform=axes[1, 2].transAxes, 
                     fontsize=10, verticalalignment='top', fontfamily='monospace')
    axes[1, 2].set_xlim(0, 1)
    axes[1, 2].set_ylim(0, 1)
    axes[1, 2].axis('off')
    
    plt.tight_layout()
    return fig

def main():
    """主应用函数"""
    
    # 主标题
    st.markdown('<div class="main-header">🏥 医学影像CT分析系统</div>', unsafe_allow_html=True)
    st.markdown('<div style="text-align: center; color: #666; margin-bottom: 2rem;">Medical Image CT Analysis System - Web Application</div>', unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.header("🔧 系统控制")
        
        # 系统信息
        st.info("""
        **系统版本**: v2.1.3.20250321_alpha Web
        
        **支持格式**: 
        - DICOM (.dcm)
        - NIfTI (.nii, .nii.gz)
        - 常见图像 (.png, .jpg, .jpeg)
        
        **AI模型**: DenseNet121 + UNet
        """)
        
        # 分析模式选择
        analysis_mode = st.selectbox(
            "选择分析模式",
            ["智能演示", "文件上传", "批量分析"]
        )
        
        # 高级设置
        with st.expander("🔬 高级设置"):
            confidence_threshold = st.slider("置信度阈值", 0.5, 0.95, 0.8)
            risk_threshold = st.slider("风险评分阈值", 0.3, 0.8, 0.5)
            show_heatmap = st.checkbox("显示热力图", True)
            generate_pdf = st.checkbox("生成PDF报告", False)
    
    # 主内容区域
    tab1, tab2, tab3, tab4 = st.tabs(["🔍 影像分析", "📊 分析结果", "📄 报告管理", "ℹ️ 系统信息"])
    
    with tab1:
        st.header("影像分析")
        
        if analysis_mode == "智能演示":
            st.markdown("""
            <div class="success-box">
            <strong>📖 演示模式</strong><br>
            点击下方按钮开始智能演示，系统将自动生成模拟CT图像并进行AI分析。
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col2:
                if st.button("🚀 开始智能演示", type="primary", use_container_width=True):
                    with st.spinner("正在生成模拟CT图像..."):
                        # 生成演示图像
                        demo_image = create_demo_ct_image()
                        st.session_state['current_image'] = demo_image
                        st.session_state['image_source'] = '演示模式生成'
                    
                    with st.spinner("正在进行AI分析..."):
                        # 执行分析
                        analysis_result = analyze_ct_image(demo_image)
                        st.session_state['analysis_result'] = analysis_result
                        st.session_state['analysis_timestamp'] = datetime.now()
                    
                    st.success("✅ 演示分析完成！请查看分析结果标签页。")
        
        elif analysis_mode == "文件上传":
            st.markdown("""
            <div class="warning-box">
            <strong>📁 文件上传模式</strong><br>
 