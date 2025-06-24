#!/bin/bash
# GitHub部署设置脚本

echo "🚀 GitHub Pages + Streamlit Cloud 部署设置"
echo "=========================================="

# 检查是否在git仓库中
if [ ! -d ".git" ]; then
    echo "❌ 不在git仓库中，请先运行 ./quick_deploy.sh"
    exit 1
fi

echo "✅ Git 仓库检查通过"

# 提示用户创建GitHub仓库
echo ""
echo "📝 请按以下步骤操作："
echo ""
echo "1️⃣ 在GitHub创建新仓库："
echo "   - 仓库名: medical-ct-analysis"
echo "   - 设为Public（这样可以使用免费的GitHub Pages）"
echo "   - 不要初始化README（因为本地已有文件）"
echo ""

read -p "已创建GitHub仓库？(y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "请先创建GitHub仓库后再继续"
    exit 1
fi

# 获取GitHub用户名
read -p "请输入您的GitHub用户名: " username
if [ -z "$username" ]; then
    echo "❌ 用户名不能为空"
    exit 1
fi

# 设置远程仓库
echo "🔗 设置远程仓库..."
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/$username/medical-ct-analysis.git

# 更新index.html中的链接
echo "🔧 更新项目链接..."
sed -i.bak "s/thrity07/$username/g" index.html
rm -f index.html.bak

# 提交更改
echo "💾 提交更改..."
git add .
git commit -m "Update GitHub username and prepare for deployment"

# 推送到GitHub
echo "📤 推送到GitHub..."
if git push -u origin main; then
    echo "✅ 推送成功"
else
    echo "⚠️ 推送失败，尝试使用master分支..."
    git push -u origin master
fi

echo ""
echo "🎉 GitHub仓库设置完成！"
echo "=========================================="
echo ""
echo "📱 访问地址："
echo "   GitHub仓库: https://github.com/$username/medical-ct-analysis"
echo "   GitHub Pages: https://$username.github.io/medical-ct-analysis"
echo ""
echo "🚀 接下来的部署步骤："
echo ""
echo "【GitHub Pages设置】"
echo "1. 访问: https://github.com/$username/medical-ct-analysis/settings/pages"
echo "2. Source选择: Deploy from a branch"
echo "3. Branch选择: main (或master)"
echo "4. 文件夹选择: / (root)"
echo "5. 点击Save保存"
echo ""
echo "【Streamlit Cloud部署】"
echo "1. 访问: https://share.streamlit.io"
echo "2. 用GitHub账号登录"
echo "3. 点击 'New app'"
echo "4. 选择仓库: $username/medical-ct-analysis"
echo "5. 主文件: streamlit_app.py"
echo "6. 点击 'Deploy!'"
echo ""
echo "🎯 部署完成后的访问方式："
echo "   - 项目主页: https://$username.github.io/medical-ct-analysis"
echo "   - 在线应用: https://$username-medical-ct-analysis-streamlit-app.streamlit.app"
echo ""
echo "✨ 用户只需访问GitHub Pages主页，点击按钮即可使用在线应用！"
echo "==========================================" 