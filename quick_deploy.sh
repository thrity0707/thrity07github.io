#!/bin/bash
# 医学影像CT分析系统 - 快速在线部署脚本

echo "🏥 医学影像CT分析系统 - 快速在线部署"
echo "=============================================="

# 检查git是否安装
if ! command -v git &> /dev/null; then
    echo "❌ Git 未安装，请先安装 Git"
    exit 1
fi

echo "✅ Git 环境检查通过"

# 初始化git仓库（如果还没有）
if [ ! -d ".git" ]; then
    echo "🔧 初始化 Git 仓库..."
    git init
    echo "node_modules/" >> .gitignore
    echo "*.pyc" >> .gitignore
    echo "__pycache__/" >> .gitignore
fi

# 添加所有文件
echo "📁 添加项目文件..."
git add .

# 提交更改
echo "💾 提交更改..."
git commit -m "Medical CT Analysis System - Ready for deployment"

echo ""
echo "🎉 项目已准备就绪！"
echo "=============================================="
echo ""
echo "🚀 选择部署方案："
echo ""
echo "【方案1 - Streamlit Cloud（推荐-免费）】"
echo "1. 在GitHub创建新仓库：medical-ct-analysis"
echo "2. 添加远程仓库："
echo "   git remote add origin https://github.com/YOUR_USERNAME/medical-ct-analysis.git"
echo "3. 推送代码："
echo "   git push -u origin main"
echo "4. 访问 https://share.streamlit.io"
echo "5. 连接GitHub仓库并选择 streamlit_app.py"
echo "6. 点击Deploy部署"
echo ""
echo "【方案2 - Hugging Face Spaces（AI社区-免费）】"
echo "1. 访问 https://huggingface.co/spaces"
echo "2. 创建新Space，选择Streamlit"
echo "3. 上传项目文件"
echo "4. 自动部署完成"
echo ""
echo "【方案3 - 本地临时公网访问（ngrok）】"
echo "1. 下载ngrok: https://ngrok.com"
echo "2. 运行: streamlit run streamlit_app.py"
echo "3. 新终端运行: ngrok http 8501"
echo "4. 获得临时公网地址"
echo ""
echo "💡 推荐使用方案1（Streamlit Cloud），完全免费且稳定"
echo ""
echo "📞 需要帮助？查看详细指南："
echo "   README_DEPLOYMENT.md"
echo "==============================================" 