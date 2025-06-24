#!/bin/bash
# 医学影像CT分析系统 - 自动部署脚本

echo "🏥 医学影像CT分析系统 - 自动部署脚本"
echo "============================================"

# 检查Docker是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查Docker Compose是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

echo "✅ Docker 环境检查通过"

# 停止现有容器
echo "🔄 停止现有容器..."
docker-compose down

# 构建镜像
echo "🔨 构建 Docker 镜像..."
docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "🔍 检查服务状态..."
docker-compose ps

# 显示访问信息
echo ""
echo "🎉 部署完成！"
echo "============================================"
echo "📱 Web应用访问地址:"
echo "   本地访问: http://localhost:8501"
echo "   局域网访问: http://$(hostname -I | awk '{print $1}'):8501"
echo ""
echo "📊 容器管理命令:"
echo "   查看日志: docker-compose logs -f"
echo "   停止服务: docker-compose down"
echo "   重启服务: docker-compose restart"
echo ""
echo "📁 数据目录:"
echo "   输出文件: ./output/"
echo "   日志文件: ./logs/"
echo "============================================" 