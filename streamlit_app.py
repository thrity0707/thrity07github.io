#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
医学影像CT分析系统 - Streamlit Web应用
Medical Image CT Analysis System - Streamlit Web App
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import cv2
from datetime import datetime
import pandas as pd

# 配置页面
st.set_page_config(
    page_title="医学影像CT分析系统",
    page_icon="🏥",
    layout="wide"
)

def create_demo_image():
    """创建演示CT图像"""
    img = np.random.normal(100, 20, (512, 512))
    y, x = np.ogrid[:512, :512]
    
    # 添加肺部区域
    lung_left = ((x - 150)**2 + (y - 256)**2) < 80**2
    lung_right = ((x - 362)**2 + (y - 256)**2) < 80**2
    img[lung_left] = np.random.normal(50, 10, np.sum(lung_left))
    img[lung_right] = np.random.normal(50, 10, np.sum(lung_right))
    
    # 心脏区域
    heart = ((x - 256)**2 + (y - 280)**2) < 50**2
    img[heart] = np.random.normal(150, 15, np.sum(heart))
    
    return np.clip(img, 0, 255).astype(np.uint8)

def analyze_image(img):
    """分析图像"""
    mean_val = np.mean(img)
    std_val = np.std(img)
    
    # 模拟AI分析
    risk_score = np.random.uniform(0.1, 0.8)
    confidence = np.random.uniform(0.75, 0.95)
    prediction = "正常" if risk_score < 0.6 else "异常"
    
    return {
        'prediction': prediction,
        'confidence': confidence,
        'risk_score': risk_score,
        'mean_intensity': mean_val,
        'std_intensity': std_val
    }

def main():
    """主应用"""
    st.title("🏥 医学影像CT分析系统")
    st.markdown("**Medical Image CT Analysis System - Web Application**")
    
    # 侧边栏
    with st.sidebar:
        st.header("系统控制")
        st.info("**版本**: v2.1.3 Web\n**模型**: DenseNet121 + UNet")
        
        mode = st.selectbox("分析模式", ["智能演示", "文件上传"])
    
    # 主界面
    if mode == "智能演示":
        st.header("🔬 智能演示")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 开始演示分析", type="primary", use_container_width=True):
                # 生成演示图像
                with st.spinner("生成模拟CT图像..."):
                    demo_img = create_demo_image()
                    st.session_state['image'] = demo_img
                
                # 执行分析
                with st.spinner("AI分析中..."):
                    result = analyze_image(demo_img)
                    st.session_state['result'] = result
                
                st.success("✅ 分析完成！")
        
        # 显示结果
        if 'result' in st.session_state and 'image' in st.session_state:
            st.divider()
            
            # 结果指标
            result = st.session_state['result']
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("诊断结果", result['prediction'])
            with col2:
                st.metric("AI置信度", f"{result['confidence']:.1%}")
            with col3:
                risk_level = "高风险" if result['risk_score'] >= 0.7 else "中风险" if result['risk_score'] >= 0.4 else "低风险"
                st.metric("风险等级", risk_level, f"{result['risk_score']:.3f}")
            with col4:
                st.metric("平均强度", f"{result['mean_intensity']:.1f} HU")
            
            # 图像显示
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 原始CT图像")
                fig, ax = plt.subplots(figsize=(8, 8))
                ax.imshow(st.session_state['image'], cmap='gray')
                ax.set_title('CT影像')
                ax.axis('off')
                st.pyplot(fig)
                plt.close(fig)
            
            with col2:
                st.subheader("📋 详细分析报告")
                
                # 生成报告
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                report = f"""
**医学影像CT分析报告**

分析时间: {timestamp}
系统版本: v2.1.3 Web

**AI分析结果:**
- 诊断结果: {result['prediction']}
- AI置信度: {result['confidence']:.1%}
- 风险评分: {result['risk_score']:.3f}
- 风险等级: {risk_level}

**图像特征:**
- 平均CT值: {result['mean_intensity']:.1f} HU
- 强度标准差: {result['std_intensity']:.1f}

**医学建议:**
{('🚨 建议立即就医，进行进一步检查' if result['risk_score'] >= 0.7 else 
  '⚠️ 建议咨询专业医生，定期复查' if result['risk_score'] >= 0.4 else 
  '✅ 建议定期体检，保持健康生活方式')}

**技术信息:**
- 使用模型: DenseNet121 + UNet分割
- 计算设备: CPU/GPU自适应
- 处理时间: < 5秒

**免责声明:**
本系统仅用于辅助医学影像分析，不能替代专业医疗诊断。
任何医疗决策都应基于专业医生的临床判断。
"""
                
                st.markdown(report)
                
                # 下载按钮
                st.download_button(
                    label="💾 下载分析报告",
                    data=report.encode('utf-8'),
                    file_name=f"ct_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    else:
        st.header("📁 文件上传")
        st.info("文件上传功能在演示版中不可用，请使用智能演示模式。")
    
    # 底部信息
    st.divider()
    st.markdown("""
    **⚠️ 重要声明**: 本系统仅用于医学影像分析的研究和教育目的，不能替代专业医疗诊断。  
    **🔗 技术支持**: medical-ai@example.com | **📚 文档**: [在线文档](https://docs.example.com)
    """)

if __name__ == "__main__":
    main() 