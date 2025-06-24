# 医学影像CT分析系统 - 部署指南

## 🌐 线上部署方案

本系统提供多种部署方案，适合不同的使用场景：

### 方案1：本地Docker部署（推荐）

#### 前提条件
- Docker >= 20.0
- Docker Compose >= 1.27

#### 快速部署
```bash
# 1. 克隆项目
git clone <repository-url>
cd medical_image_analysis-main

# 2. 运行自动部署脚本
./deploy.sh

# 3. 访问应用
# 浏览器打开: http://localhost:8501
```

#### 手动部署
```bash
# 构建并启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方案2：云平台部署

#### Streamlit Cloud（免费）
1. 将代码推送到GitHub
2. 访问 [share.streamlit.io](https://share.streamlit.io)
3. 连接GitHub仓库
4. 选择 `streamlit_app.py` 作为主文件
5. 点击 Deploy

#### Heroku部署
1. 创建Heroku应用
```bash
heroku create medical-ct-analysis
```

2. 设置构建包
```bash
heroku buildpacks:set heroku/python
```

3. 部署
```bash
git push heroku main
```

#### Railway部署
1. 连接GitHub仓库到Railway
2. 设置环境变量：
   - `PORT=8501`
   - `PYTHONPATH=/app`
3. 自动部署

### 方案3：VPS服务器部署

#### 服务器要求
- Ubuntu 20.04+ / CentOS 8+
- 2GB RAM minimum, 4GB recommended
- 10GB storage minimum

#### 部署步骤
```bash
# 1. 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 2. 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.0.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 3. 克隆项目
git clone <repository-url>
cd medical_image_analysis-main

# 4. 启动服务
sudo ./deploy.sh

# 5. 配置防火墙（如果需要）
sudo ufw allow 8501
```

## 📱 移动端访问优化

系统默认支持响应式设计，可以在移动设备上正常使用：

- iPhone/Android浏览器完全兼容
- 触摸操作优化
- 自适应屏幕尺寸

## 🔧 环境变量配置

创建 `.env` 文件进行自定义配置：

```env
# 服务器配置
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0

# 应用配置
MAX_UPLOAD_SIZE=200
ENABLE_ANALYTICS=false
DEBUG_MODE=false

# 安全配置
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,your-domain.com
```

## 🚀 性能优化

### 服务器优化
```bash
# 增加系统限制
echo "* soft nofile 65536" >> /etc/security/limits.conf
echo "* hard nofile 65536" >> /etc/security/limits.conf

# 优化内存使用
echo "vm.swappiness=10" >> /etc/sysctl.conf
```

### 应用优化
- 启用缓存：`@st.cache_data`
- 图像压缩：自动优化上传图像
- 异步处理：后台处理大文件

## 🔒 安全配置

### HTTPS配置（生产环境）
```bash
# 使用Let's Encrypt
sudo apt install certbot
sudo certbot --nginx -d your-domain.com
```

### 反向代理（Nginx）
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 📊 监控和日志

### 日志配置
```yaml
version: '3.8'
services:
  medical-ct-analysis:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 健康检查
```bash
# 检查服务状态
curl http://localhost:8501/_stcore/health

# 监控脚本
watch -n 30 'docker-compose ps'
```

## 🔧 故障排除

### 常见问题

1. **端口被占用**
```bash
# 查找占用进程
sudo lsof -i :8501
# 杀死进程
sudo kill -9 <PID>
```

2. **内存不足**
```bash
# 清理Docker
docker system prune -a
# 重启服务
docker-compose restart
```

3. **权限问题**
```bash
# 修复权限
sudo chown -R $USER:$USER ./output ./logs
```

### 日志查看
```bash
# 应用日志
docker-compose logs medical-ct-analysis

# 系统日志
tail -f /var/log/syslog
```

## 📞 技术支持

- **文档**: [在线文档](https://docs.medical-ai.com)
- **问题反馈**: [GitHub Issues](https://github.com/medical-ai/ct-analysis/issues)
- **邮件支持**: support@medical-ai.com

## 🎯 部署检查清单

- [ ] Docker环境正常
- [ ] 端口8501可访问
- [ ] 防火墙配置正确
- [ ] SSL证书配置（生产环境）
- [ ] 备份策略制定
- [ ] 监控系统部署
- [ ] 用户访问测试

## 📈 扩展部署

### 负载均衡
```yaml
version: '3.8'
services:
  app1:
    build: .
    ports:
      - "8501:8501"
  app2:
    build: .
    ports:
      - "8502:8501"
  nginx:
    image: nginx
    ports:
      - "80:80"
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
```

### 集群部署
- Kubernetes deployment
- Docker Swarm mode
- 数据库集群
- 缓存集群

---

*最后更新: 2025-06-24* 