# 医学影像CT分析系统 - Docker镜像
FROM python:3.9-slim

# 设置工作目录
WORKDIR /app

# 设置环境变量
ENV PYTHONPATH=/app
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements_web.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements_web.txt

# 复制应用文件
COPY streamlit_app.py .
COPY enhanced_demo.py .
COPY README.md .

# 创建输出目录
RUN mkdir -p output logs

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 启动命令
CMD ["streamlit", "run", "streamlit_app.py", "--server.headless", "true", "--server.fileWatcherType", "none"] 