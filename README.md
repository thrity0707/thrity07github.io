# 医学影像CT分析系统 / Medical Image CT Analysis System

<div align="center">

![Version](https://img.shields.io/badge/version-2.1.3.20250321_alpha-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-MIT-yellow)

基于MONAI和PySide6的专业医学影像分析系统  
Professional medical image analysis system based on MONAI and PySide6

</div>

## 📋 项目简介 / Project Introduction

这是一个基于深度学习的医学影像CT分析系统，集成了图像处理、AI分析、可视化和报告生成等功能。系统采用模块化设计，支持多种医学影像格式，提供直观的图形用户界面和强大的分析能力。

This is a deep learning-based medical CT image analysis system that integrates image processing, AI analysis, visualization, and report generation. The system uses modular design, supports multiple medical image formats, and provides an intuitive GUI with powerful analysis capabilities.

## ✨ 主要功能 / Main Features

### 核心功能 / Core Features
- 🖼️ **多格式支持**: DICOM, NIfTI, PNG, JPEG
- 🧠 **AI智能分析**: 基于MONAI的深度学习模型
- 🔍 **病灶检测**: 自动识别和定位异常区域
- 🌡️ **热力图生成**: 可视化AI关注区域
- 📊 **风险评估**: 自动化风险等级评定
- 📄 **PDF报告**: 专业医学报告生成

### 技术特性 / Technical Features
- ⚡ **GPU加速**: 支持CUDA加速计算
- 🔄 **多线程处理**: 异步分析提升效率
- 🎯 **模块化设计**: 易于扩展和维护
- 🖥️ **跨平台**: Windows, macOS, Linux
- 🔒 **数据安全**: 本地处理，保护隐私

## 🚀 快速开始 / Quick Start

### 系统要求 / System Requirements

- Python 3.8+
- 4GB+ RAM
- 可选: NVIDIA GPU (推荐 / Recommended)

### 安装依赖 / Installation

```bash
# 克隆项目 / Clone repository
git clone https://github.com/thrity0707/thrity07github.io.git
cd thrity07github.io

# 安装基础依赖 / Install basic dependencies
pip install -r requirements.txt

# 可选: 安装GPU支持 / Optional: Install GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### 运行系统 / Run System

```bash
# 检查依赖 / Check dependencies
python run_demo.py --mode check

# 启动图形界面 / Launch GUI
python run_demo.py --mode gui

# 命令行演示 / CLI demo
python run_demo.py --mode cli

# 或直接运行主程序 / Or run main program directly
python main.py
```

## 📁 项目结构 / Project Structure

```
thrity07github.io/
├── main.py                 # 主程序入口 / Main entry
├── run_demo.py            # 演示脚本 / Demo script
├── requirements.txt       # 依赖列表 / Dependencies
├── streamlit_app.py       # Web应用 / Web application
├── index.html             # 项目主页 / Project homepage
├── gui/                   # 图形界面 / GUI modules
│   ├── __init__.py
│   └── main_window.py     # 主窗口 / Main window
├── core/                  # 核心模块 / Core modules
│   ├── __init__.py
│   └── image_processor.py # 图像处理 / Image processing
├── models/                # AI模型 / AI models
│   ├── __init__.py
│   └── ct_analyzer.py     # CT分析器 / CT analyzer
├── utils/                 # 工具模块 / Utility modules
│   ├── __init__.py
│   ├── logger.py          # 日志系统 / Logging
│   └── report_generator.py # 报告生成 / Report generation
├── data/                  # 数据目录 / Data directory
├── output/                # 输出目录 / Output directory
└── logs/                  # 日志目录 / Log directory
```

## 🌐 在线访问 / Online Access

### GitHub Pages 主页
访问项目主页：[https://thrity0707.github.io/thrity07github.io](https://thrity0707.github.io/thrity07github.io)

### Streamlit 在线应用
在线体验AI分析：[https://thrity0707-thrity07github-io-streamlit-app.streamlit.app](https://thrity0707-thrity07github-io-streamlit-app.streamlit.app)

## 🔧 使用说明 / Usage Guide

### 图形界面操作 / GUI Operation

1. **加载影像**: 点击"加载影像"按钮选择CT文件
2. **开始分析**: 点击"开始分析"按钮进行AI分析
3. **查看结果**: 在右侧面板查看分析结果
4. **生成报告**: 点击"生成PDF报告"保存结果

### Web应用操作 / Web Application

1. 访问在线地址或点击主页的"启动在线分析系统"按钮
2. 使用"智能演示"查看系统功能
3. 上传您的CT影像文件
4. 查看AI分析结果和可视化图表
5. 下载分析报告

### 支持的文件格式 / Supported Formats

- **DICOM** (.dcm, .dicom): 医学标准格式
- **NIfTI** (.nii, .nii.gz): 神经影像格式
- **图像** (.png, .jpg, .jpeg): 标准图像格式

### 分析结果说明 / Analysis Results

- **分类结果**: 正常/异常二分类
- **置信度**: AI预测的可信程度
- **风险等级**: 低风险/中风险/高风险
- **热力图**: 显示AI关注的区域
- **技术细节**: 像素统计和分割信息

## 🛠️ 开发指南 / Development Guide

### 环境配置 / Environment Setup

```bash
# 创建虚拟环境 / Create virtual environment
python -m venv medical_analysis_env

# 激活环境 / Activate environment
# Windows:
medical_analysis_env\Scripts\activate
# macOS/Linux:
source medical_analysis_env/bin/activate

# 安装开发依赖 / Install dev dependencies
pip install -r requirements.txt
pip install pytest black flake8
```

### 代码结构 / Code Structure

- `MedicalImageProcessor`: 医学影像处理核心类
- `CTAnalyzer`: CT影像AI分析器
- `PDFReportGenerator`: PDF报告生成器
- `MainWindow`: 主界面窗口类

### 自定义模型 / Custom Models

系统支持加载自定义训练的模型：

```python
# 加载自定义分类模型
analyzer.load_classification_model("path/to/your/model.pth")

# 加载自定义分割模型
analyzer.load_segmentation_model("path/to/your/segmentation_model.pth")
```

## 📊 性能指标 / Performance Metrics

- **分析速度**: < 30秒 (CPU), < 10秒 (GPU)
- **内存使用**: < 2GB
- **支持尺寸**: 最大 2048x2048 像素
- **准确率**: > 90% (在测试数据集上)

## ⚠️ 重要声明 / Important Notice

**本系统仅供研究和教育用途，不能替代专业医疗诊断。任何医学决策都应基于专业医生的临床判断。**

**This system is for research and educational purposes only and cannot replace professional medical diagnosis. Any medical decisions should be based on professional clinical judgment.**

## 🤝 贡献指南 / Contributing

我们欢迎社区贡献！请遵循以下步骤：

1. Fork 项目仓库
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📝 更新日志 / Changelog

### v2.1.3.20250321_alpha
- ✅ 完整的GUI界面
- ✅ AI分析核心模块
- ✅ PDF报告生成
- ✅ 多格式图像支持
- ✅ 风险评估系统
- ✅ Streamlit Web应用
- ✅ GitHub Pages部署

### v1.0.0.20250314_alpha (已弃用 / Deprecated)
- 基础CT分类功能

## 🆘 技术支持 / Technical Support

- 📧 Email: jntm20111013@outlook.com
- 🐛 Issues: 请在GitHub Issues中报告问题
- 📖 Wiki: 查看项目Wiki获取详细文档

## 📄 许可证 / License

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**🏥 医学影像CT分析系统 - 让AI为医疗服务**  
**Medical Image CT Analysis System - AI for Healthcare**

Made with ❤️ by Medical AI Team

</div>
